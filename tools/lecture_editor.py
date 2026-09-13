"""Edit selected cells of the accepted HTML; retain the other cells and figures."""
from pathlib import Path
import html
import json
import re
import subprocess
import base64
from collections import defaultdict, deque
from bs4 import BeautifulSoup
from pygments import highlight
from pygments.lexers import CppLexer
from pygments.formatters import HtmlFormatter
import nbformat

ROOT = Path(__file__).resolve().parents[1]
PAGES = [
 'chapt1/1.1_create_tree.html', 'chapt1/1.2_read_tree.html',
 'chapt1/1.3_adc_analysis.html', 'chapt1/1.4_root_tree_makeclass.html',
 'chapt2/2.1_PPAC_analysis.html', 'chapt2/2.2_PPAC_tracking.html',
 'chapt2/2.3_comiling_1.html', 'chapt2/2.4_compiling_2.html',
 'chapt2/2.5_data_analysis_process.html',
 'chapt3/3.1_DSSD_energy_calibration_1.html',
 'chapt3/3.2_TTree_Branch_with_Dynamic_Array.html',
 'chapt3/3.3_DSSD_interstrip_correlation.html',
 'chapt3/3.4_DSSD_FB_correlation_I_DSSD1-new.html',
 'chapt3/3.5_DSSD_FB_correlation_II_DSSD1-new.html',
 'chapt3/3.5_DSSD_FB_correlation_II_DSSD1_multi-path.html',
 'chapt3/3.6_DSSD_Multiplicity_Analysis.html',
 'chapt3/3.7_DSSD_data_analysis.html',
 'chapt3/3.8_TTree_Branch_with_vector.html',
 'chapt1/Integration_in_TH1_and_TF1.html',
 'chapt1/Example_of_Integration_in_TH1_and_TF1.html',
 'chapt4/4.0_gamma-gamma_coincidence.html',
 'chapt4/4.0_pairtimewalk.html',
 'chapt4/4.0_check_corrected_timewalk.html',
 'chapt4/4.1_gamma-gamma_coincidence_matrix.html',
 'chapt4/4.2_gamma-gamma_background_matrix.html',
 'chapt5/5.1_Decay_analysis_I.html',
 'chapt5/5.2_Decay_analysis_II.html',
 'chapt5/fitting_LS_LH.html',
]

def fragment(s):
    return BeautifulSoup(s, 'html.parser')

def pre(s):
    return '<pre><code class="language-cpp">'+html.escape(s.strip())+'</code></pre>'

class Page:
    def __init__(self, path, current=False, revision='HEAD'):
        self.path = path
        original = (ROOT/path).read_text() if current else subprocess.check_output(['git','show', revision+':'+path], cwd=ROOT).decode()
        self.soup = BeautifulSoup(original, 'html.parser')
        self.cells = self.soup.select('.jp-Cell') or self.soup.select('.cell')
        self.changed = set()

    def container(self, i):
        return self.cells[i].select_one('.jp-RenderedMarkdown,.text_cell_render')

    def md(self, i, markup):
        c = self.container(i)
        c.clear()
        c.append(fragment(markup))
        self.changed.add(i)

    def append(self, i, markup):
        self.container(i).append(fragment(markup))
        self.changed.add(i)

    def paragraph(self, i, start, markup):
        for tag in self.container(i).select('p,li'):
            if tag.get_text().strip().startswith(start):
                tag.replace_with(fragment(markup))
                self.changed.add(i)
                return
        raise ValueError((self.path,i,start))

    def replace(self, old, new, indices=None):
        count = 0
        for i in (indices if indices is not None else range(len(self.cells))):
            c = self.container(i)
            if c is None:
                continue
            for block in list(c.find_all('pre')):
                value=block.get_text()
                if old in value:
                    count+=value.count(old)
                    block.replace_with(fragment(pre(value.replace(old,new))))
                    self.changed.add(i)
            for node in list(c.find_all(string=True)):
                if old in node:
                    count += str(node).count(old)
                    node.replace_with(str(node).replace(old,new))
                    self.changed.add(i)
        if not count:
            print('REVIEW replacement not found:', self.path, repr(old[:75]))
        return count

    def code(self, i, code=None):
        c = self.cells[i].select_one('.jp-InputArea-editor,.input_area')
        if code is None:
            return c.get_text().strip()
        c.clear()
        c.append(fragment(highlight(code.strip(), CppLexer(), HtmlFormatter())))
        self.changed.add(i)

    def patch_code(self, i, old, new):
        source = self.code(i)
        if old not in source:
            raise ValueError((self.path,i,old))
        self.code(i, source.replace(old,new))

    def save(self):
        # A page is runnable from its own directory. Never resolve files through
        # another checkout or change the original data in materials/.
        previous = defaultdict(deque)
        notebook_path=(ROOT/self.path).with_suffix('.ipynb')
        if notebook_path.exists():
            for cell in nbformat.read(notebook_path,as_version=4).cells:
                if cell.cell_type=='code':previous[cell.source.strip()].append(cell)
        nb = nbformat.v4.new_notebook()
        nb.metadata.kernelspec = {'display_name':'ROOT C++','language':'c++','name':'root'}
        nb.metadata.language_info = {'name':'c++','file_extension':'.C','pygments_lexer':'cpp'}
        code = {}
        for i,c in enumerate(self.cells):
            md = self.container(i)
            editor = c.select_one('.jp-InputArea-editor,.input_area')
            if md is not None:
                for anchor in md.select('a.anchor-link'): anchor.decompose()
                nb.cells.append(nbformat.v4.new_markdown_cell(md.decode_contents()))
            elif editor is not None:
                source = editor.get_text().strip()
                code[i] = source
                nc=nbformat.v4.new_code_cell(source)
                prior=previous[source].popleft() if previous[source] else None
                result=c.select_one('.verified-output')
                if result is not None:
                    nc.execution_count=i+1
                    for out in result.find_all('pre'):
                        nc.outputs.append(nbformat.v4.new_output('stream',name='stdout',text=out.get_text()))
                    for img in result.find_all('img',src=True):
                        image_path=(ROOT/self.path).parent/img['src']
                        if image_path.exists():
                            # Legacy static output; native notebooks retain their
                            # real MIME bundle below instead of being rebuilt.
                            image_path=image_path.with_suffix('.png')
                            nc.outputs.append(nbformat.v4.new_output('display_data',data={'image/png':base64.b64encode(image_path.read_bytes()).decode()}))
                elif prior is not None:
                    nc.outputs=prior.outputs
                    nc.execution_count=prior.execution_count
                if prior is not None:nc.id=prior.id
                nb.cells.append(nc)
        path = ROOT / self.path
        path.write_text(str(self.soup))
        nbformat.write(nb, path.with_suffix('.ipynb'))
        manifest = ROOT/'work'/'cells'/path.with_suffix('.json').name
        manifest.parent.mkdir(parents=True, exist_ok=True)
        manifest.write_text(json.dumps({'path':self.path,'code':code,'changed':sorted(self.changed)},ensure_ascii=False,indent=2))
        print('Revised', self.path, 'cells', sorted(self.changed))

    def insert_before(self, i, items):
        """Insert small Markdown/code cells; original indices stay valid until save."""
        for kind, value in items:
            if kind == 'md':
                content = '<div class="jp-RenderedHTMLCommon jp-RenderedMarkdown jp-MarkdownOutput" data-mime-type="text/markdown">'+value+'</div>'
                kind_class = 'jp-MarkdownCell'
            else:
                content = '<div class="jp-CodeMirrorEditor jp-Editor jp-InputArea-editor"><div class="cm-editor cm-s-jupyter">'+highlight(value.strip(), CppLexer(), HtmlFormatter())+'</div></div>'
                kind_class = 'jp-CodeCell'
            markup = '<div class="jp-Cell '+kind_class+' jp-Notebook-cell"><div class="jp-Cell-inputWrapper"><div class="jp-InputArea jp-Cell-inputArea">'+content+'</div></div></div>'
            self.cells[i].insert_before(fragment(markup))

    def refresh(self):
        self.cells = self.soup.select('.jp-Cell') or self.soup.select('.cell')

    def rebuild(self, items):
        """Replace a specifically approved supplement while retaining page assets."""
        self.insert_before(0, items)
        for cell in self.cells:
            cell.decompose()
        self.refresh()
