"""Run a lecture's C++ cells in order with ROOT, then attach actual outputs.

The runner uses the same Cling interpreter as ROOT notebooks. It is not a
physics reimplementation. Inputs are read in the chapter directory; generated
files have distinct names. Start a new process for each lecture.
"""
from pathlib import Path
import sys
import json
import re
import ctypes
import base64
import subprocess
import ROOT
from bs4 import BeautifulSoup
import nbformat
from lecture_editor import ROOT as BASE, PAGES

ROOT.gROOT.SetBatch(True)
ROOT.gInterpreter.Declare('''
#include <iostream>
#include <fstream>
#include <vector>
#include <map>
#include <algorithm>
#include <stdexcept>
#include <cmath>
#include <TFile.h>
#include <TTree.h>
#include <TChain.h>
#include <TCanvas.h>
#include <TH1.h>
#include <TH2.h>
#include <TProfile.h>
#include <TGraph.h>
#include <TGraphErrors.h>
#include <TF1.h>
#include <TFitResult.h>
#include <TFitResultPtr.h>
#include <TMatrixDSym.h>
#include <TCut.h>
#include <TCutG.h>
#include <TLine.h>
#include <TLegend.h>
#include <TLatex.h>
#include <TRandom3.h>
#include <TSpectrum.h>
#include <TPolyMarker.h>
using namespace std;
''')

number=int(sys.argv[1])
path=BASE/PAGES[number]
manifest=json.loads((BASE/'work/cells'/path.with_suffix('.json').name).read_text())
soup=BeautifulSoup(path.read_text(),'html.parser')
cells=soup.select('.jp-Cell') or soup.select('.cell')
nb=nbformat.read(path.with_suffix('.ipynb'),as_version=4)
ROOT.gSystem.ChangeDirectory(str(path.parent))
figs=path.parent/'figures'/path.stem
figs.mkdir(parents=True,exist_ok=True)
logs=BASE/'work/logs'/path.stem
logs.mkdir(parents=True,exist_ok=True)
extra={
 13:{18:['c_res_fity'],20:['c_res_fitx'],22:['c_res_fity'],28:['c_check']},
 14:{11:['cVal']},
}

for key,source in manifest['code'].items():
    i=int(key)
    if not source.strip(): continue
    print('RUN',number,i,flush=True)
    code=re.sub(r'^%%cpp[^\n]*\n','',source).strip()
    log=logs/f'{i:02d}.txt'
    err=ctypes.c_int(0)
    if code.startswith('!'):
        # Only the inspected build/run cells of these two lessons are shell cells.
        if number not in (6,7):
            raise RuntimeError('Shell cell needs explicit review')
        commands='\n'.join(line[1:] for line in code.splitlines() if line.startswith('!'))
        completed=subprocess.run(commands,cwd=path.parent,shell=True,executable='/bin/bash',capture_output=True,text=True)
        log.write_text(completed.stdout+completed.stderr)
        err.value=completed.returncode
        code=''
    else:
        log.write_text('')
    ROOT.gSystem.RedirectOutput(str(log),'a')
    try:
        # A definition cell can contain several functions; Declare preserves
        # namespace scope. All executable cells go through ProcessLine.
        definition = source.startswith('%%cpp -d') or bool(re.match(r'^(void|bool|struct|class)\s+\w+[\s({]',code))
        if definition:
            if not ROOT.gInterpreter.Declare(code): err.value=1
        elif code.startswith(('.L ','.x ')):
            ROOT.gROOT.ProcessLine(code)
        elif code:
            ROOT.gInterpreter.ProcessLine(code)
    finally:
        ROOT.gROOT.ProcessLine('gSystem->RedirectOutput(nullptr);')
    output=log.read_text()
    if err.value or re.search(r'(^|\n)(.*error:|Error in <|.*segmentation violation)',output):
        print(output[-7000:],flush=True)
        raise RuntimeError(f'{path.name} cell {i} failed ({err.value})')
    for old in cells[i].select('.jp-Cell-outputWrapper,.output_wrapper,.verified-output'):
        old.decompose()
    result=soup.new_tag('div',attrs={'class':'verified-output'})
    if output.strip():
        pre=soup.new_tag('pre');pre.string=output.strip();result.append(pre)
    images=[]
    names=list(dict.fromkeys(re.findall(r'\b(\w+)->(?:Draw|Update)\(\s*\)',code)+extra.get(number,{}).get(i,[])))
    for name in names:
        canvas=ROOT.gROOT.GetListOfCanvases().FindObject(name)
        if not canvas:
            canvas=getattr(ROOT,name,None)
            if not canvas or not hasattr(canvas,'InheritsFrom') or not canvas.InheritsFrom('TCanvas'): continue
        if not canvas: continue
        img=figs/f'cell_{i:02d}_{name}.png'
        canvas.SaveAs(str(img))
        tag=soup.new_tag('img',attrs={'src':str(img.relative_to(path.parent)),'alt':f'{path.stem}: cell {i}, {name}','style':'max-width:100%;height:auto;max-height:1100px;object-fit:contain'})
        result.append(tag); images.append(img)
    if result.contents: cells[i].append(result)
    nb.cells[i].execution_count=i+1
    nb.cells[i].outputs=[]
    if output.strip(): nb.cells[i].outputs.append(nbformat.v4.new_output('stream',name='stdout',text=output))
    for img in images:
        nb.cells[i].outputs.append(nbformat.v4.new_output('display_data',data={'image/png':base64.b64encode(img.read_bytes()).decode()}))
    path.write_text(str(soup))
    nbformat.write(nb,path.with_suffix('.ipynb'))
print('PASS',path.name,flush=True)
