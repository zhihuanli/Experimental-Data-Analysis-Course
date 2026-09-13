"""Keep MakeClass -> compiled class -> inherited analysis -> batch processing."""
from lecture_editor import ROOT, PAGES, Page, pre, fragment
import re

MAKE='''CXX = c++
CPPFLAGS = -Iinclude $(shell root-config --cflags)
CXXFLAGS = -O2 -Wall
LDLIBS = $(shell root-config --libs)
SOURCES = main.cpp $(wildcard src/*.cpp src/*.C)
HEADERS = $(wildcard include/*.h)

all: tracking

tracking: $(SOURCES) $(HEADERS)
	$(CXX) $(CPPFLAGS) $(CXXFLAGS) $(SOURCES) $(LDLIBS) -o $@

clean:
	rm -f tracking
'''

def main(inherited=False):
    return '''#include <TFile.h>
#include <TTree.h>
#include <TString.h>
#include <cstdlib>
#include <iostream>
'''+('#include "ana.h"\n' if inherited else '#include "tracking.h"\n')+'''
int main(int argc, char** argv) {
    if (argc!=2 && argc!=4) {
        std::cerr << "Usage: ./tracking run [input_dir output_dir]\\n";
        return 1;
    }
    int run = std::atoi(argv[1]);
    const char* inputDir = argc==4 ? argv[2] : "../..";
    const char* outputDir = argc==4 ? argv[3] : ".";
    TString inputName = Form("%s/f8ppac%03d.root",inputDir,run);
    TString outputName = Form("%s/out%03d.root",outputDir,run);
    TFile* input = TFile::Open(inputName);
    if (!input || input->IsZombie()) return 1;
    TTree* tin = input->Get<TTree>("tree");
    if (!tin) return 1;
    TFile output(outputName,"RECREATE");
    if (output.IsZombie()) return 1;
    TTree* tout = new TTree("tree","PPAC tracking");
    {
'''+('        ana analysis(tin,tout);\n        analysis.Analysis();\n' if inherited else '        tracking analysis(tin);\n        analysis.Loop(tout);\n')+'''
        std::cout << "Input=" << tin->GetEntries() << ", output=" << tout->GetEntries() << '\\n';
        output.Write();
    } // MakeClass 基类析构时释放输入文件；不再重复 delete input。
    return 0;
}
'''

source=(ROOT/'chapt2/tracking.C').read_text()
source=source.replace('void tracking::Loop()','void tracking::Loop(TTree *tree)')
source=re.sub(r'    TFile \*opf =.*?    SetBranch\(tree\);','    SetBranch(tree);',source,flags=re.S)
source=source.replace('    htf8xz->Write();','').replace('    htf8yz->Write();','').replace('    tree->Write();','').replace('    opf->Close();','')
source=source.replace('    cout << "Tracking finished. Output saved to tracking.root" << endl;','')
header=(ROOT/'chapt2/tracking.h').read_text().replace('Loop();','Loop(TTree *tree);')
for n in [1,2]:
    folder=ROOT/f'chapt2/code/compile{n}'
    (folder/'include').mkdir(parents=True,exist_ok=True);(folder/'src').mkdir(exist_ok=True)
    (folder/'Makefile').write_text(MAKE)
    (folder/'main.cpp').write_text(main(n==2))
    if n==1:
        (folder/'include/tracking.h').write_text(header)
        (folder/'src/tracking.C').write_text(source)
    else:
        generated=ROOT/'work/generated_tracking'
        (folder/'include/tracking.h').write_text((generated/'tracking.h').read_text())
        (folder/'src/tracking.C').write_text((generated/'tracking.C').read_text())
        members=header.split('public :',1)[1].split('   TTree',1)[0]
        ana='''#ifndef ANA_H
#define ANA_H
#include "tracking.h"
#include <TH2.h>
class ana : public tracking {
public:
'''+members+'''
    TTree *fOutTree;
    ana(TTree *input,TTree *output) : tracking(input),fOutTree(output) {}
    void Analysis();
};
#endif
'''
        (folder/'include/ana.h').write_text(ana)
        child=source.replace('#define tracking_cxx\n','').replace('#include "tracking.h"','#include "ana.h"').replace('tracking::','ana::').replace('void ana::Loop(TTree *tree)\n{','void ana::Analysis()\n{\n    TTree *tree = fOutTree;')
        (folder/'src/ana.cpp').write_text(child)

p=Page(PAGES[6])
p.paragraph(0,'解释执行','<li><code>.x mycode.C</code> 由 ROOT 的 Cling 即时编译并执行，适合交互探索；不是逐行解释器，也不意味着事件循环必然很慢。</li>')
p.paragraph(0,'编译执行','<li>独立可执行程序使用 C++ 编译器和 ROOT 库构建，便于检查头文件依赖、组织多个源文件及批量运行。ACLiC 的 <code>.L mycode.C+</code> 也可编译宏。</li>')
p.replace('必须且只能放置在 LIBS 变量中','在本 Makefile 中集中放入 LDLIBS')
p.replace('“重复编译”错误','重复定义错误')
p.replace('不写函数的具体实现逻辑','本例将实现放入源文件；inline 与模板可以在头文件定义')
folder=ROOT/'chapt2/code/compile1'
for block in p.container(0).find_all('pre'):
    text=block.get_text()
    path=None
    if 'int main(' in text:path=folder/'main.cpp'
    elif 'class tracking' in text and 'Double_t' in text:
        # Show the class body, not hundreds of generated I/O lines.
        block.replace_with(fragment(pre(header.split('#ifdef tracking_cxx')[0])));continue
    elif 'void tracking::' in text:path=folder/'src/tracking.C'
    elif 'ROOTCFLAGS' in text:path=folder/'Makefile'
    if path:block.replace_with(fragment(pre(path.read_text())))
p.append(0,'<p>完整工程位于 <code>code/compile1</code>。Loop 沿用 2.2 的同一套 tracking 和误差传播；main 负责文件，Loop 负责填充传入的树。头文件中的生成代码仍保留，不应从上面的节选中删去构造函数和分支绑定。</p>')
p.md(1,'<h3>编译和运行</h3><p>在 <code>code/compile1</code> 中执行：</p>'+pre('make\n./tracking 1\n# 或显式指定输入、输出目录\n./tracking 1 ../.. .')+'<p><code>root-config --cflags</code> 给编译选项，<code>--libs</code> 给链接选项。源文件中包含声明所用类型的头文件（如 TGraphErrors.h）；这与链接 ROOT 库是两件不同的事。编译报错时先检查第一处错误。</p>')
p.code(2,'!make -C code/compile1')
p.code(3,'!cd code/compile1 && ./tracking 1')
p.save()

p=Page(PAGES[7])
p.replace('工程目录严格划分为','本例把工程目录划分为')
p.replace('全部交由主程序 main.cpp 来调度','在本例中交由 main.cpp 调度')
p.replace('程序即具备了自动化批处理（Batch Processing）的能力','就便于用脚本批量调用')
for para in list(p.container(0).find_all('p')):
    if '默认的随机值' in para.get_text():
        para.replace_with(fragment('<p>初始化列表直接初始化成员。内置类型若未初始化，值是不确定的，并不是编译器特意赋予的“随机值”；对引用、const 成员和基类，初始化列表尤其重要。</p>'))
folder=ROOT/'chapt2/code/compile2'
for block in p.container(0).find_all('pre'):
    text=block.get_text();path=None
    if 'int main(' in text:path=folder/'main.cpp'
    elif 'class ana : public tracking' in text:path=folder/'include/ana.h'
    elif 'void ana::Analysis' in text:path=folder/'src/ana.cpp'
    if path:block.replace_with(fragment(pre(path.read_text())))
p.append(0,'<p>完整工程位于 <code>code/compile2</code>。tracking.h/C 保持 MakeClass 生成形式；ana 继承输入成员和 LoadTree，将与 2.3 相同的物理计算移入 Analysis。两种工程应对同一输入给出相同的输出事件和 tracking 参数。</p>')
p.code(1,'!make -C code/compile2\n!cd code/compile2 && ./tracking 1')
p.save()

p=Page(PAGES[8])
p.paragraph(1,'整个分析流程','<p>可将分析分为解码、刻度、事件重建和物理分析几个阶段。在计算耗时或需要重复使用的阶段保存中间 ROOT 文件；无需每做一步都另存一个文件。保留原事件编号、输入来源、刻度参数和选择条件，便于复查。</p>')
p.md(4,'<h3>步骤一：检查原始道值与量化</h3><p>保留 ADC/TDC 的整数码及无效、overflow 等状态，检查其有效区间。刻度可以直接作用于原始码或 bin 中心。1.3 的 dithering 是基于 bin 内均匀近似的可选处理，不是刻度的必需步骤，也不恢复丢失的精度。</p>')
p.replace('在得到原始 ROOT 文件后，必须进行以下标准化处理','在得到原始 ROOT 文件后，可按以下顺序检查')
p.replace('在后续分析中，直接在 TTree 结构中通过 tree->Draw() 实时查看每个参数的分布极其耗时。','对大型文件反复画同一分布会重复读取数据。')
p.replace('还需将常用信息','可将常用信息')
p.replace('必须确认基础参数的时间稳定性','先检查基础参数的时间稳定性')
p.replace('经过 Cut 筛选后的纯净事件','经过 Cut 选择后的候选事件')
p.replace('可精确提取','可在给定模型下估计')
p.replace('展宽（对应寿命）','峰宽（需分离自然宽度与仪器分辨后才可能关联寿命）')
p.replace('其包含的变量仍是','其中使用的量包括')
for para in list(p.container(15).find_all('p')):
    if para.get_text().startswith(('以下是为你整理','该教程紧密衔接')):para.decompose()
p.replace('终极解决方案：使用','后台运行可使用')
p.replace('一旦电脑休眠、断网或 SSH 终端连接断开，正在运行的程序会被 Linux 系统强制终止（Kill）。','关闭终端或 SSH 连接可能发送 SIGHUP；电脑休眠会暂停本机任务。nohup 不能防止休眠、重启或资源限制导致的终止。')
for block in p.container(15).find_all('pre'):
    txt=block.get_text().replace('mkdir -p $OUT_DIR','mkdir -p "$OUT_DIR"').replace('$(seq $START $END)','$(seq "$START" "$END")')
    if 'IN_DIR=' in txt:
        txt=txt.replace('./tracking $run','if ! ./tracking "$run" "$IN_DIR" "$OUT_DIR"; then\n        echo "Run $run failed" >&2\n        continue\n    fi')
        txt=re.sub(r'    # 6\..*?\n    fi\n','',txt,flags=re.S)
    block.replace_with(fragment(pre(txt)))
p.code(12,'TCanvas *c1 = new TCanvas("c1","Directory example");\n'+p.code(12))
p.save()
