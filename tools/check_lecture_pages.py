"""Check current lecture assets, notebook structure and preserved later chapters."""
from pathlib import Path
from urllib.parse import urlparse,unquote
from collections import Counter
import subprocess,json,re,base64,zlib
import nbformat
from bs4 import BeautifulSoup
from lecture_editor import ROOT,PAGES

errors=[]
pages=['index.html']+PAGES+['chapt1/ROOT_tips.html']
for rel in pages:
    path=ROOT/rel
    soup=BeautifulSoup(path.read_text(),'html.parser')
    for tag,attr in [('img','src'),('a','href'),('link','href')]:
        for node in soup.find_all(tag,attrs={attr:True}):
            value=node[attr];url=urlparse(value)
            if url.scheme or url.netloc or not url.path: continue
            target=path.parent/unquote(url.path)
            if not target.exists():errors.append((rel,tag,value))
            elif url.fragment=='assignment':
                linked=BeautifulSoup(target.read_text(),'html.parser')
                if not linked.find(id='assignment'):errors.append((rel,'anchor',value))
    if rel in PAGES:
        nb=nbformat.read(path.with_suffix('.ipynb'),as_version=4)
        nbformat.validate(nb)
        htmlcells=soup.select('.jp-Cell') or soup.select('.cell')
        assert len(htmlcells)==len(nb.cells),(rel,len(htmlcells),len(nb.cells))
        for cell,ncell in zip(htmlcells,nb.cells):
            editor=cell.select_one('.jp-InputArea-editor,.input_area')
            if editor:
                assert editor.get_text().strip()==ncell.source.strip(),(rel,'code differs')
                # Native Jupyter MIME bundles belong to their generating code
                # cell. Check their plot IDs and scripts, not exported images.
                expected=[]
                for output in ncell.outputs:
                    assert output.output_type!='error',(rel,'execution error')
                    markup=output.get('data',{}).get('text/html','')
                    packed=re.search(r"Core.unzipJSON\((\d+),'([^']*)'",markup)
                    if packed:
                        assert packed[2],(rel,'empty JSROOT compressed payload')
                        payload=base64.b64decode(packed[2]);raw=b''
                        while payload:
                            assert payload[:2]==b'ZL',(rel,'ROOT compression header')
                            size=int.from_bytes(payload[3:6],'little')
                            raw+=zlib.decompress(payload[9:9+size])
                            payload=payload[9+size:]
                        assert len(raw)==int(packed[1]),(rel,'truncated JSROOT data')
                        json.loads(raw)
                    bundle=BeautifulSoup(markup,'html.parser')
                    expected.extend(n['id'] for n in bundle.select('[id^="root_plot_"]'))
                    for script in bundle.find_all('script'):
                        assert any(script.get_text().strip()==s.get_text().strip()
                                   for s in cell.find_all('script')),(rel,'native script differs')
                    if output.output_type=='stream':
                        plain=re.sub(r'\x1b\[[0-9;]*m','',output.text).replace('\r\n','\n').replace('\r','\n').strip()
                        rendered='\n'.join(p.get_text() for p in cell.select('.jp-OutputArea pre'))
                        assert plain in rendered,(rel,'printed output differs',plain[:100])
                actual=[n['id'] for n in cell.select('[id^="root_plot_"]')]
                assert expected==actual,(rel,'JSROOT output attached to wrong cell',expected,actual)
                assert not cell.select('.verified-output'),(rel,'legacy manual output wrapper')
        if rel not in [PAGES[19]]:
            assert any(c.cell_type=='code' and re.search(r'^%jsroot\s+on\s*$',c.source,re.M)
                       for c in nb.cells),(rel,'JSROOT not enabled')
            assert nb.metadata.kernelspec.name=='root',(rel,'ROOT kernel')
        figures=len(soup.select('[id^="root_plot_"]'))
        identifiers=[p['id'] for p in soup.select('[id^="root_plot_"]')]
        assert len(set(identifiers))==len(identifiers),(rel,'duplicate JSROOT plot IDs')
        print(rel, 'cells',len(nb.cells),'native JSROOT outputs',figures)

# Compare semantic notebook content of later chapters, not serialization.
for rel in subprocess.check_output(['git','diff','--name-only'],cwd=ROOT,text=True).splitlines():
    if rel in PAGES:continue
    if not rel.startswith(('chapt4/','chapt5/','chapt6/','chapt7/')) or not rel.endswith('.html'):continue
    old=BeautifulSoup(subprocess.check_output(['git','show','HEAD:'+rel],cwd=ROOT),'html.parser')
    new=BeautifulSoup((ROOT/rel).read_text(),'html.parser')
    for selector in ['.jp-Cell','.cell']:
        if old.select(selector):
            assert [n.get_text() for n in old.select(selector)]==[n.get_text() for n in new.select(selector)],(rel,'later content changed')
            break
for path in ROOT.glob('chapt[123]/coursework*.html'):
    soup=BeautifulSoup(path.read_text(),'html.parser')
    for link in soup.select('a[href]'):
        url=urlparse(link['href'])
        if url.scheme:continue
        target=path.parent/unquote(url.path)
        assert target.exists(),target
        assert BeautifulSoup(target.read_text(),'html.parser').find(id=url.fragment),(target,url.fragment)
home=BeautifulSoup((ROOT/'index.html').read_text(),'html.parser')
prefix='https://zhihuanli.github.io/Experimental-Method-in-Nuclear-Physics/'
assert not home.select('.course-nav,nav'), 'The course index should not have section navigation'
links=home.select_one('.course-home').find_all('a',href=prefix)
assert len(links)==1,'Use one Methods link, before chapter 1'
chapters=[h for h in home.find_all(['h2','h3']) if re.search(r'第一章|chapter\s+1\.',h.get_text(),re.I)]
assert chapters,'Chapter 1 heading'
assert links[0] in list(chapters[0].previous_elements),'Methods link should precede chapter 1'
prerequisite=home.find(id='preparation')
assert prerequisite and prerequisite.get_text(strip=True).startswith('前置课程：')
assert prerequisite.find('a')==links[0], 'The prerequisite links directly to Methods'
for link in home.select('a[href]'):
    if link['href'].startswith(prefix):
        target=ROOT.parent/'method'/unquote(link['href'][len(prefix):] or 'README.md')
        if not target.exists() and target.suffix=='.html':target=target.with_suffix('.md')
        assert target.exists(),target
print('Local missing targets:',len(errors))
for entry in errors:print(*entry,sep=' | ')
(ROOT/'work/page_checks.json').write_text(json.dumps(errors,ensure_ascii=False,indent=2))
if errors:raise SystemExit(1)
print('PASS: links, notebook code/output parity, later chapter content')
