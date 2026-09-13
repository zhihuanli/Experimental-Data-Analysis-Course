"""Check current lecture assets, notebook structure and preserved later chapters."""
from pathlib import Path
from urllib.parse import urlparse,unquote
from collections import Counter
import subprocess,json
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
                assert editor.get_text().strip()==ncell.source,(rel,'code differs')
                assert len(cell.select('.verified-output img'))==sum(o.output_type=='display_data' for o in ncell.outputs),(rel,'figures differ')
        figures=len(soup.select('.verified-output img'))
        print(rel, 'cells',len(nb.cells),'executed figures',figures)

# Compare semantic notebook content of later chapters, not serialization.
for rel in subprocess.check_output(['git','diff','--name-only'],cwd=ROOT,text=True).splitlines():
    if not rel.startswith(('chapt4/','chapt5/','chapt7/')) or not rel.endswith('.html'):continue
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
assert home.select_one('.course-home').find_all('a',href=True)[-1]['href']==prefix, 'Methods link should end the index'
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
