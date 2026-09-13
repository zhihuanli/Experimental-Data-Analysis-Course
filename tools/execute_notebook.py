"""Execute the ROOT C++ notebook and export its native Jupyter outputs.

The ROOT kernel produces JSROOT display_data. No SaveAs, output screenshots,
canvas lookup, manual output text, or plot replacement is performed here.
"""
from pathlib import Path
import sys,re,os
import nbformat
from nbclient import NotebookClient
from nbconvert import HTMLExporter
from bs4 import BeautifulSoup
from lecture_editor import ROOT, PAGES

number=int(sys.argv[1]); path=ROOT/PAGES[number]
render_only='--render-only' in sys.argv
nb=nbformat.read(path.with_suffix('.ipynb'),as_version=4)
nb.metadata.kernelspec={'name':'root','display_name':'ROOT C++','language':'c++'}
if not any(c.cell_type=='code' and re.search(r'^%jsroot\s+on\s*$',c.source,re.M) for c in nb.cells):
    nb.cells.insert(1,nbformat.v4.new_code_cell('%jsroot on',id='jsroot-on'))
for c in nb.cells:
    if c.cell_type!='code':continue
    if not render_only:
        c.outputs=[];c.execution_count=None
    # Definition cells are supported directly by the ROOT kernel's C++ magic.
    if re.match(r'^(void|bool|struct|class)\s+\w+[\s({]',c.source) or re.match(r'^TH\w+\s*\*\s*\w+\s*\(',c.source):
        c.source='%%cpp -d\n'+c.source

def progress(cell,cell_index,**kwargs):
    print('EXECUTE',path.name,cell_index,flush=True)

class LoggedClient(NotebookClient):
    def process_message(self,msg,cell,cell_index):
        if msg['msg_type']=='stream':
            print(msg['content']['text'],end='',flush=True)
        return super().process_message(msg,cell,cell_index)

client=LoggedClient(nb,kernel_name='root',timeout=300,
    resources={'metadata':{'path':str(path.parent)}},on_cell_start=progress)
if not render_only:
    client.execute()
for i,c in enumerate(nb.cells):
    for o in c.get('outputs',[]):
        text=o.get('text','')
        if o.output_type=='error' or re.search(r'(^|\n)(.*error:|Error in <|.*segmentation violation)',text):
            raise RuntimeError(f'{path.name} cell {i}: {text[:2500]}')
nbformat.write(nb,path.with_suffix('.ipynb'))

old=BeautifulSoup(path.read_text(),'html.parser')
exporter=HTMLExporter(template_name='lab',exclude_input_prompt=True,exclude_output_prompt=True)
body,_=exporter.from_notebook_node(nb)
soup=BeautifulSoup(body,'html.parser')
soup.html['lang']='zh-CN'
heading=soup.select_one('.jp-MarkdownOutput h1,.jp-MarkdownOutput h2')
if heading and soup.title:
    soup.title.string=heading.get_text(' ',strip=True).removesuffix('¶').strip()
soup.body['class']=list(dict.fromkeys(soup.body.get('class',[])+['lecture-review']))
for selector in ['.course-banner','link[data-course-header]','link[data-lecture-layout]']:
    for tag in old.select(selector):
        (soup.body if tag.name=='header' else soup.head).append(tag.extract())
header=soup.select_one('.course-banner')
if header:soup.body.insert(0,header.extract())
if not soup.select_one('link[data-lecture-layout]'):
    link=soup.new_tag('link',rel='stylesheet',href=os.path.relpath(ROOT/'assets/css/lecture-layout.css',path.parent))
    link['data-lecture-layout']='true';soup.head.append(link)
for table in soup.select('.jp-MarkdownOutput table'):
    if table.find_parent('table'):continue
    table['class']=list(dict.fromkeys(table.get('class',[])+['lecture-table']))
    if not table.find_parent(class_='lecture-table-scroll'):
        table.wrap(soup.new_tag('div',attrs={'class':'lecture-table-scroll'}))
path.write_text(str(soup))
plots=sum('text/html' in o.get('data',{}) and 'root_plot_' in o.data['text/html']
          for c in nb.cells for o in c.get('outputs',[]))
print('PASS NATIVE',path.name,'JSROOT outputs',plots,flush=True)
