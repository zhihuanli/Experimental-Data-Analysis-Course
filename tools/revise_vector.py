"""Synchronize the existing two vector-Branch projects and their lecture blocks."""
from lecture_editor import ROOT, PAGES, Page, pre, fragment
import subprocess
import re

def original(path):
    return subprocess.check_output(['git','show','HEAD:'+path],cwd=ROOT).decode()

def write(rel,src):
    (ROOT/rel).write_text(src)

MAKE='''CXX = c++
CPPFLAGS = -Iinclude $(shell root-config --cflags)
CXXFLAGS = -O2 -Wall
LDLIBS = $(shell root-config --libs)
SOURCES = main.cpp $(wildcard src/*.cpp src/*.C) LinkDict.cc
HEADERS = $(wildcard include/*.h)

all: dssd

LinkDict.cc: $(HEADERS) Linkdef.h
	rootcling -f $@ -Iinclude include/ana.h Linkdef.h

dssd: $(SOURCES) $(HEADERS)
	$(CXX) $(CPPFLAGS) $(CXXFLAGS) $(SOURCES) $(LDLIBS) -o $@

clean:
	rm -f dssd LinkDict.cc LinkDict_rdict.pcm
'''

p=Page(PAGES[17])
for k in [1,2]:
    base=f'chapt3/code/code{k}/'
    h=original(base+'include/ana.h')
    h=h.replace('#include <TRandom3.h>','#include <vector>\n#include <limits>')
    h=h.replace('  Double_t t;','  Double_t t = std::numeric_limits<double>::quiet_NaN();')
    if k==2:
        h=h.replace('Float_t sx1e','Double_t sx1e').replace('Float_t sy1e','Double_t sy1e')
        h=h.replace('#include <vector>','#include <vector>\n#include <limits>')
        h=h.replace('  Double_t t;','  Double_t t = std::numeric_limits<double>::quiet_NaN();')
    h=h.replace('  TRandom3 *gr;','')
    h=h.replace('  TTree *opt;','  Long64_t source_entry = 0;\n  TTree *opt;')
    # actual formatting in headers varies
    if 'Long64_t source_entry' not in h:
        h=h.replace(' public:',' public:\n  Long64_t source_entry = 0;')
    src=original(base+'src/ana.cpp')
    src=src.replace('x3v.size()>0 || x3v.size()>0','x3v.size()>0 || y3v.size()>0')
    src=src.replace('SortDS(dssd &a,dssd &b)','SortDS(const dssd &a,const dssd &b)')
    src=src.replace('int hit=min(x->size(),y->size());','size_t hit=std::min(x->size(),y->size());')
    src=src.replace('for(int i=0;i<hit;i++)','for(size_t i=0;i<hit;i++)')
    src=src.replace('    if(b1||b2||b3) opt->Fill();','    source_entry = jentry;\n    opt->Fill(); // 保留空事件及事件对应关系')
    src=src.replace('    bool b1=x1v.size()>0 || y1v.size()>0;\n    bool b2=x2v.size()>0 || y2v.size()>0;\n    bool b3=x3v.size()>0 || y3v.size()>0;\n','')
    src=src.replace('    if(d1.size()>0 || d2.size()>0 || d3.size()>0)\n        opt->Fill();','    opt->Fill(); // 无候选时保存空 vector，不改变事件顺序')
    for name in ['sx1e','sx2e','sx3e','sy1e','sy2e','sy3e']:
        src=src.replace(f'&{name},"{name}"',f'&{name},"{name}/D"')
    src=re.sub(r'    if\(\(jentry\) % 1000 == 0\) \{.*?\n    \}', '', src, flags=re.S)
    if k==1:
        src=src.replace('void ana::SetOutBranch()\n{','void ana::SetOutBranch()\n{\n  opt->Branch("source_entry", &source_entry, "source_entry/L");')
        src=src.replace('    ds.e=ee[i];','    ds.e=ee[i];\n    ds.t=std::numeric_limits<double>::quiet_NaN(); // 输入文件没有时间')
    else:
        src=src.replace('  br_x1v = NULL;','  ipt->SetBranchAddress("source_entry", &source_entry);\n  br_x1v = NULL;')
        src=src.replace('void ana::BranchOutput()\n{','void ana::BranchOutput()\n{\n  opt->Branch("source_entry", &source_entry, "source_entry/L");')
    write(base+'include/ana.h',h);write(base+'src/ana.cpp',src)
    link=original(base+'Linkdef.h').replace('__CINT__','__CLING__')
    write(base+'Linkdef.h',link);write(base+'makefile',MAKE)
    default_input='../../data/strip_arrays_16C.root' if k==1 else '../../vec_16C.root'
    default_output='../../vec_16C.root' if k==1 else '../../sort_16C.root'
    # Scope the analysis object so its generated base can release input once.
    main=f'''#include <TFile.h>
#include <TTree.h>
#include <iostream>
#include "ana.h"
int main(int argc, char** argv) {{
    const char* inputName = argc>1 ? argv[1] : "{default_input}";
    const char* outputName = argc>2 ? argv[2] : "{default_output}";
    TFile* input = TFile::Open(inputName);
    if (!input || input->IsZombie()) return 1;
    TTree* tin = input->Get<TTree>("tree");
    if (!tin) return 1;
    TFile output(outputName,"RECREATE");
    TTree* tout = new TTree("tree","vector branch");
    {{
        ana analysis(tin,tout);
        analysis.Analysis();
        std::cout << "Input=" << tin->GetEntries() << ", output=" << tout->GetEntries() << '\\n';
        output.cd();
        tout->Write();
    }}
    {'delete input;' if k==2 else '// MakeClass 基类的析构函数已释放 input。'}
    return 0;
}}
'''
    write(base+'main.cpp',main)

# This input has calibrated fixed arrays; it is not the similarly named
# compact-hit file used in 3.6. Preserve it under a distinct local filename.
dst=ROOT/'chapt3/data/strip_arrays_16C.root'
if not dst.exists(): subprocess.run(['cp','-cRp',str(ROOT/'materials/chapt3/vector/cal_16C.root'),str(dst)],check=True)

p.replace('cal_16C.root','strip_arrays_16C.root')
p.replace('Double_t d1t[32], d2t[32], d3t[32]; // xt','// 本节参考文件没有时间分支；t 用 NaN 表示不可用。')
p.append(0,'<p>本节输入为 <code>data/strip_arrays_16C.root</code>，保留刻度后的固定数组，区别于 3.6 的 compact-hit 文件。它没有时间数据，结构体中的 t 显式设为 NaN，不生成虚构时间。两个转换程序均保留原事件编号和空事件。</p>')
blocks=p.container(0).find_all('pre')
for block in blocks:
    text=block.get_text()
    rel=None
    if 'int main(' in text: rel='chapt3/code/code1/main.cpp'
    elif 'class ana : public test' in text: rel='chapt3/code/code1/include/ana.h'
    elif 'void ana::ProcessDS' in text: rel='chapt3/code/code1/src/ana.cpp'
    elif 'OBJ = dssd' in text: rel='chapt3/code/code1/makefile'
    if rel: block.replace_with(fragment(pre((ROOT/rel).read_text())))
    else:
        text=text.replace('__CINT__','__CLING__').replace('Double_t t;','Double_t t = std::numeric_limits<double>::quiet_NaN();')
        block.replace_with(fragment(pre(text.replace('```cpp','').replace('```',''))))
p.replace('只要三层 DSSD 中至少有一层存在 hit，就把该事件写入输出树。','每个输入事件都写入输出树，包括空 vector；这样后续仍能追溯原事件。')
p.replace('vector::assign(v1.begin(), v2.end());','vector::assign(v1.begin(), v1.end());')
p.replace('首地址','起始迭代器').__class__
p.replace('尾地址','末尾之后的迭代器')
p.replace('bool SortDS(dssd &a, dssd &b)','bool SortDS(const dssd &a, const dssd &b)')
p.replace('return Long64_t(a.e - b.e) == 0 && a.id == b.id;','return a.id == b.id && a.e == b.e && a.t == b.t;')
p.replace('int dt = Long64_t(it->t - b[0].t);','double dt = it->t - referenceTime;')
p.replace('if (b.size() > 0) {','if (b.size() > 0) {\n    const double referenceTime = b[0].t; // erase 前保存参考时间')
p.append(11,'<p><code>unique</code> 只去掉相邻的等价元素；相同条号和近似相等的能量不能证明是重复读出，真实 pileup 也可能如此。数据去重应有原始事件标识、timestamp 或电子学重复记录的证据。本节参考文件没有时间，不能运行基于 t 的物理 cut；时间选择代码仅说明有有效时间输入时的容器用法。</p><p>按能量排序后同下标配对，是单条响应和清晰能量分离下的初步候选算法，并未覆盖 3.6 的 sharing、共用条及多解事件。保留未匹配结果，再按需要回到完整重建。</p>')
for block in p.container(11).find_all('pre'):
    txt=block.get_text().replace('__CINT__','__CLING__')
    if 'int main(' in txt: txt=(ROOT/'chapt3/code/code2/main.cpp').read_text()
    elif 'class ana' in txt: txt=(ROOT/'chapt3/code/code2/include/ana.h').read_text()
    elif 'void ana::SetBranchInput' in txt:
        src=(ROOT/'chapt3/code/code2/src/ana.cpp').read_text();txt=src[src.index('void ana::SetBranchInput'):src.index('void ana::BranchOutput')]
    elif 'void ana::BranchOutput' in txt:
        src=(ROOT/'chapt3/code/code2/src/ana.cpp').read_text();txt=src[src.index('void ana::BranchOutput'):src.index('bool SortDS')]
    elif 'void ana::Analysis' in txt:
        src=(ROOT/'chapt3/code/code2/src/ana.cpp').read_text();txt=src[src.index('void ana::Analysis'):]
    block.replace_with(fragment(pre(txt)))
p.code(2,'gSystem->Load("code/code1/libhits.so"); // 本节 make 同时生成读取字典\nTCanvas *c1 = new TCanvas;\nTFile *ff = new TFile("vec_16C.root");\nTTree *tree = (TTree*)ff->Get("tree");')
# Build a small dictionary-only shared library for later interactive reads.
for k in [1,2]:
    f=ROOT/f'chapt3/code/code{k}/makefile'
    txt=f.read_text().replace('all: dssd','all: dssd libhits.so')
    txt=txt.replace('clean:\n','libhits.so: LinkDict.cc $(HEADERS)\n\t$(CXX) $(CPPFLAGS) $(CXXFLAGS) -fPIC -shared LinkDict.cc $(LDLIBS) -o $@\n\nclean:\n')
    txt=txt.replace('rm -f dssd','rm -f libhits.so dssd')
    f.write_text(txt)
p.save()
