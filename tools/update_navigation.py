"""Keep one course index and a shared banner, without section navigation."""
from pathlib import Path
from urllib.parse import urlparse, unquote
import os
import shutil
import sys
import mistune
from bs4 import BeautifulSoup
from lecture_editor import ROOT, PAGES

METHOD='https://zhihuanli.github.io/Experimental-Method-in-Nuclear-Physics/'
DATA='https://zhihuanli.github.io/Experimental-Data-Analysis-Course/'
asset=ROOT/'assets/images/course-logo.png'
asset.parent.mkdir(parents=True,exist_ok=True)
if not asset.exists(): shutil.copy2(ROOT.parent/'method/assets/images/course-logo.png',asset)

def header(prefix):
    return f'''<header class="course-banner"><div class="course-banner-inner">
<a href="{prefix}index.html"><img src="{prefix}assets/images/course-logo.png" alt="课程标志"></a>
<div class="course-banner-title"><a href="{prefix}index.html">核物理实验数据处理</a>
<span class="course-banner-en">Experimental Data Analysis in Nuclear Physics</span></div></div></header>'''

body=mistune.create_markdown(plugins=['table'])((ROOT/'ReadMe.md').read_text())
soup=BeautifulSoup(body,'html.parser')
for a in soup.find_all('a',href=True):
    if a['href'].startswith(DATA): a['href']=a['href'][len(DATA):]
for h in soup.select('h2'):
    if h.get_text() in ('课前准备', 'ROOT 基础'): h['id']='preparation'
    if h.get_text().startswith('chapter 1.'): h['id']='lectures'
(ROOT/'index.html').write_text('<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>核物理实验数据处理</title><link rel="stylesheet" href="assets/css/course-header.css"></head><body class="course-home-body">'+header('')+'<main class="course-home">'+str(soup)+'</main></body></html>')

if '--index-only' in sys.argv:
    print('Course index updated; lecture pages unchanged.')
    raise SystemExit(0)

# Keep old URLs useful, but maintain the common introductory text in one place.
redirects={
 'ROOT/ROOT Tutorial I.html':METHOD+'tutorial/ROOT/ROOT_Tutorial_I_CPP.html',
 'ROOT/ROOT Tutorial II.html':METHOD+'tutorial/ROOT/ROOT_Tutorial_II_CPP.html',
 'ROOT/ROOT_III-Example.html':METHOD+'tutorial/ROOT/ROOT_Tutorial_II_CPP.html',
 'ROOT/juypter.html':METHOD+'tutorial/setup/ROOT_Jupyter_Installation.html',
 'chapt0/introduction_basic.html':METHOD+'tutorial/cpp/introduction_basic.html',
 'chapt0/introduction_advanced.html':METHOD+'tutorial/cpp/introduction_advanced.html',
 'chapt1/coursework1.1.html':'1.2_read_tree.html#assignment',
 'chapt1/coursework1.2.html':'1.4_root_tree_makeclass.html#assignment',
 'chapt2/coursework2.1.html':'2.2_PPAC_tracking.html#assignment',
 'chapt3/coursework3.1.html':'3.2_TTree_Branch_with_Dynamic_Array.html#assignment',
 'chapt3/coursework3.2.html':'3.4_DSSD_FB_correlation_I_DSSD1-new.html#assignment',
 'chapt3/coursework3.3.html':'3.5_DSSD_FB_correlation_II_DSSD1-new.html#assignment',
 'chapt3/coursework3.4.html':'3.6_DSSD_Multiplicity_Analysis.html#assignment',
}
for rel,url in redirects.items():
    path=ROOT/rel
    path.write_text(f'<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><title>课程资料</title><meta http-equiv="refresh" content="0;url={url}"><link rel="canonical" href="{url}"></head><body><p>本内容已整合至<a href="{url}">对应讲义</a>。</p></body></html>')

# Header only on current lecture and supplement pages. The scientific content
# of chapters 4--6 is deliberately left untouched.
pages=set(PAGES+['chapt1/ROOT_tips.html','chapt1/Integration_in_TH1_and_TF1.html','chapt1/Example_of_Integration_in_TH1_and_TF1.html'])
for a in soup.find_all('a',href=True):
    href=a['href']
    if href.startswith('chapt') and href.endswith('.html'): pages.add(unquote(href))
for rel in sorted(pages):
    path=ROOT/rel
    if not path.exists(): continue
    page=BeautifulSoup(path.read_text(),'html.parser')
    for link in page.select('link[href="custom.css"]'): link.decompose()
    for old in page.select('.course-banner,.course-nav,link[data-course-header]'): old.decompose()
    prefix=os.path.relpath(ROOT,path.parent)+'/'
    link=page.new_tag('link',rel='stylesheet',href=prefix+'assets/css/course-header.css')
    link['data-course-header']='true';page.head.append(link)
    page.body.insert(0,BeautifulSoup(header(prefix),'html.parser'))
    if rel in PAGES:
        for heading in page.select('h1,h2,h3,h4'):
            if heading.get_text().strip().rstrip('¶').strip().rstrip('：:') in ['作业','Assignment','作业要求']:
                heading['id']='assignment'
    path.write_text(str(page))
print('Header updated on',len(pages),'lecture pages; introductory links consolidated.')
