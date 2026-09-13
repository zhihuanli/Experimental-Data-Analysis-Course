"""Retain the neutron-detector example and the original four-section route."""
from lecture_editor import Page, ROOT, PAGES, pre, fragment
import re

INCLUDES='''#include <TFile.h>
#include <TTree.h>
#include <TH1D.h>
#include <TRandom3.h>
#include <TMath.h>
#include <iostream>
#include <cmath>
'''

def simulation():
    p=Page(PAGES[0])
    replacements={
     '$(n, p)$ 散射':'$n+p\\rightarrow n+p$ 弹性散射',
     '0-50 MeV 质子的经验响应模型':'质子光输出的经验模型',
     '对于 0-50 MeV 范围内的反冲质子，其电子等效能量':'反冲质子的电子等效能量',
     '根据对塑料闪烁体（如 BC408/NE-102）的大量实验数据拟合，标准建议参数为：':'本练习用下面一组参数演示非线性光输出；它们不是各种塑料闪烁体通用的刻度参数：',
     '$A_R>Q_{th}$':'$A_R>A_{th}$',
     'sigma_{niose}':'sigma_{noise}',
     '系数 $A_L$ 与 $A_R$':'系数 $W_L$ 与 $W_R$',
     't_{mes_{L/R}} = t_{L/R} +':'t_{mes_{L/R}} = t^{(0)}_{L/R} +',
     't_L = \\text{TOF} + \\frac{L+x}{v_{sc}} + t_{0L} + \\text{Gaus}(0, \\sigma_{t_L})':'t^{(0)}_L = \\text{TOF} + \\frac{L+x}{v_{sc}} + t_{0L}',
     't_R = \\text{TOF} + \\frac{L-x}{v_{sc}} + t_{0R} + \\text{Gaus}(0, \\sigma_{t_R})':'t^{(0)}_R = \\text{TOF} + \\frac{L-x}{v_{sc}} + t_{0R}',
     'x_q = \\frac{\\lambda}{2}\\ln \\frac{q_L}{q_R}':'x_q = \\frac{\\lambda}{2}\\ln \\frac{q_R}{q_L}',
     'Q_0^2 = e^{2L/\\lambda} q_L \\cdot q_R/4':'Q_0^2 = 4e^{2L/\\lambda} q_L q_R',
     'x_q = \\frac{\\lambda}{2}\\frac{g_R}{g_L}\\ln \\frac{A_L}{A_R}':'x_q = \\frac{\\lambda}{2}\\ln \\frac{A_R g_L}{A_L g_R}',
     '入射深度 (z_true)':'入射深度 (depth_true) 和实际路径 (path_true)',
     '能量沉积（电荷）信息：$q_L, q_R$':'经增益转换的两端幅度：$A_L, A_R$',
     'tree->Write();  // 将缓冲区内的所有事件批量压缩并写入磁盘':'tree->Write();  // 写入尚未落盘的内容及树的元数据',
    }
    for a,b in replacements.items(): p.replace(a,b)
    for tag in list(p.container(0).find_all('p')):
        if tag.get_text().startswith('这里是对 TTree 核心概念'): tag.decompose()
    p.append(0,r'''<h3>模型中使用的近似</h3><p>100 MeV 中子不宜只用非相对论 TOF 式。代码采用 \(\gamma=1+E_n/(m_nc^2)\)、\(\beta=\sqrt{1-\gamma^{-2}}\)、\(TOF=d/(\beta c)\)，其中 \(m_nc^2=939.565\) MeV，\(c=0.299792458\) m/ns；前面的非相对论式是低能极限。</p><p>参考练习先抽样反冲质子能量，再计算光输出。各向同性 n-p 散射、单次反冲以及 gamma 的简化沉积谱均用于展示数据处理，不代表此几何下的完整输运响应。光输出参数依赖材料和读出条件。参见 R. A. Cecil, B. D. Anderson and R. Madey, <a href="https://www.sciencedirect.com/science/article/pii/0029554X79904173">Nucl. Instrum. Methods 161 (1979) 439–447</a>。</p><p>重建公式中的时间先扣除 walk。\(t^{(0)}\) 不含随机涨落；每端最终测量时间只加入一次 Gaussian 涨落，避免重复加入分辨。</p>''')
    p.md(1,'<h2>3. 模拟代码</h2><p>先用单能中子、固定时间分辨和无阈值的简化例子说明 TTree 的创建、逐事件 Fill 和写入。随后参考练习加入反冲、光输出、阈值、幅度相关的时间分辨和 walk。</p>')
    c=p.code(2)
    c=re.sub(r'  const Double_t (a|b|c|d|EnFWHM|sigt_no|sigt_stat|Walk_AL|Walk_AR|A_th) =[^\n]*\n','',c)
    c=c.replace('new TRandom3(0)','new TRandom3(1101)').replace('tree.root','tree_demo.root').replace('/2.35','/2.355')
    c=c.replace('Reconstructed time of flight','Mean end time;Mean end time (ns);Counts')
    c=c.replace('  Double_t x_true;','  Double_t depth_true, path_true;\n  Double_t x_true;')
    c=c.replace('  opt->Branch("x_true"','  opt->Branch("depth_true", &depth_true, "depth_true/D");\n  opt->Branch("path_true", &path_true, "path_true/D");\n  opt->Branch("x_true"',1)
    c=c.replace('Double_t y_prime = gr->Uniform(-T/2.0, T/2.0);','depth_true = gr->Uniform(-T/2.0, T/2.0);')
    c=c.replace('D + y_prime','D + depth_true')
    c=c.replace('    Double_t E_dep = 0;','    path_true = dis;\n    Double_t E_dep = 0;')
    c=c.replace('3.333 * dis','dis / 0.299792458').replace('72.3 / TMath::Sqrt(e_true) * dis','dis / (0.299792458 * sqrt(1-pow(1+e_true/939.565,-2)))')
    p.code(2,c)
    (ROOT/'chapt1/create_tree.C').write_text(INCLUDES+c+'\n')
    for i in [8]: p.code(i,p.code(i).replace('tree.root','tree_demo.root'))
    p.code(15,'tree->Draw("tR-tL>>hdt(100,-15,50)");\nc1->Draw();')
    p.code(20,'c1->Clear();\nc1->Divide(2,1);\nc1->cd(1); tree->Draw("tof_true:x_true>>hpath0(100,-1,1,150,10,50)","","colz");\nc1->cd(2); tree->Draw("tof_true/path_true:x_true>>hpath1(100,-1,1,150,0,10)","","colz");\nc1->Draw();')
    p.code(27,'TFile *fHW = new TFile("tree_hw_demo.root");\nTTree *tree = (TTree*)fHW->Get("tree");')
    p.append(23,'<p>程序给出不含测量涨落的 <code>tL_true/tR_true</code>；最终时间在加入 walk 后只展宽一次。保存 <code>depth_true/path_true</code> 用于与重建比较。分析未知数据时不使用这些真值。</p>')
    src=(ROOT/'materials/chapt1/root-tree/create_tree_hw.cc').read_text()
    src=src.replace('tree_hw.root','tree_hw_demo.root').replace('new TRandom3(0)','new TRandom3(1102)').replace('/2.35','/2.355')
    src=src.replace('  Double_t x_true;','  Double_t depth_true, path_true;\n  Double_t x_true;')
    src=src.replace('  opt->Branch("x_true"','  opt->Branch("depth_true", &depth_true, "depth_true/D");\n  opt->Branch("path_true", &path_true, "path_true/D");\n  opt->Branch("x_true"',1)
    src=src.replace('Double_t z_prime =','depth_true =').replace('D + z_prime','D + depth_true').replace('    E_dep = 0;','    path_true = dis;\n    E_dep = 0;')
    src=src.replace('3.333 * dis','dis / 0.299792458').replace('72.3 / TMath::Sqrt(e_true) * dis','dis / (0.299792458 * sqrt(1-pow(1+e_true/939.565,-2)))')
    src=re.sub(r'double E_ee =.*?E_dep = gr->Uniform\(0, E_ee\);','double Ep = gr->Uniform(0, e_true); // 先抽样反冲质子能量\n        E_dep = std::max(0.0, a*Ep - b*(1-TMath::Exp(-c*TMath::Power(Ep,d))));',src,flags=re.S)
    src=src.replace('    // *** 加入 Time-Walk 效应 ***','    if (AL <= A_th || AR <= A_th) continue; // 先检查有效幅度\n    // *** 加入 Time-Walk 效应 ***')
    src=src.replace('Gamma沉积全部能量 (简化)','简化 gamma 沉积模型').replace('// MeVee, 阈值','// 幅度单位的阈值')
    (ROOT/'chapt1/create_tree_hw.cc').write_text(INCLUDES+'#include <algorithm>\n'+src+'\n')
    p.save()

ANALYZE=r'''#include <TFile.h>
#include <TTree.h>
#include <cmath>
#include <iostream>
void Analyze(double WL, double WR, double timeOffset) {
    TFile input("tree_hw_demo.root");
    TTree *tin = input.Get<TTree>("tree");
    double AL, AR, tL, tR;
    tin->SetBranchAddress("AL", &AL);
    tin->SetBranchAddress("AR", &AR);
    tin->SetBranchAddress("tL", &tL);
    tin->SetBranchAddress("tR", &tR);

    TFile output("calibrated.root", "RECREATE");
    TTree *tout = tin->CloneTree(0); // 保留原有分支，只复制结构
    double xt, xq, tof_cal;
    Long64_t entry;
    tout->Branch("source_entry", &entry, "source_entry/L");
    tout->Branch("xt", &xt, "xt/D");
    tout->Branch("xq", &xq, "xq/D");
    tout->Branch("tof_cal", &tof_cal, "tof_cal/D");
    for (entry=0; entry<tin->GetEntries(); ++entry) {
        tin->GetEntry(entry);
        if (AL<=0 || AR<=0) continue;
        double tl = tL-WL/std::sqrt(AL);
        double tr = tR-WR/std::sqrt(AR);
        xt = 0.075/2 * (tl-tr-(5.5-20.4)); // m
        xq = 3.8/2 * std::log(AR*10/(AL*15)); // m
        tof_cal = (tl+tr)/2 + timeOffset; // ns
        tout->Fill();
    }
    std::cout << "Input=" << tin->GetEntries() << ", output=" << tout->GetEntries() << '\n';
    tout->Write();
}'''

def reading():
    p=Page(PAGES[1])
    p.replace('附加延迟遵循反比定律','附加延迟在本例中用下式作经验描述')
    p.replace('真实 $TOF$ 是固定的常数（光速）','在窄位置切片内，真实 TOF 近似相同')
    p.replace('x_q = \\frac{\\lambda}{2}\\frac{g_R}{g_L}\\ln \\frac{A_L}{A_R}','x_q = \\frac{\\lambda}{2}\\ln \\frac{A_R g_L}{A_L g_R}')
    p.patch_code(1,'tree_hw.root','tree_hw_demo.root')
    p.patch_code(5,'log(AL/AR)+0.5','log(AL/AR)-log(10.0/15.0)')
    p.replace('$tL/tR : \\sqrt{AL/AR}$','两端的 $t : 1/\\sqrt{A}$')
    p.append(6,'<p>TProfile 保存每个横轴 bin 内的平均时间及其误差；拟合斜率给出 W。位置切片有有限宽度，幅度比也有噪声，因此这是近似校准；可比较不同切片的结果。示例中的 pid 只用来展示已知粒子的响应，作业改用图形选择。</p>')
    for i,side in [(7,'L'),(9,'R')]:
        c=p.code(i).replace(f'walk{side}(50, 0, 0.6)',f'walk{side}(50,0,0.6,240,20,100)')
        c=c.replace(f'TProfile *prof{side} = walk{side}->ProfileX',f'TH2 *walk{side} = (TH2*)gROOT->FindObject("walk{side}");\nTProfile *prof{side} = walk{side}->ProfileX')
        p.code(i,c)
    p.code(12,p.code(12).replace('h_new(200,30,70)','h_new(200,10,90)').replace('"h_old"','"htof"'))
    p.replace('导数的峰值位置才是物理边界最可靠的估计','可用导数极值定位边缘，也可直接拟合展宽后的阶梯形状')
    p.replace('使得重建出的 $x$ 恰好落在 $[-L, L]$ 区间','使两处边缘的中心映射到 −L 和 L；分辨会使少量重建值落在边界外')
    p.append(13,'<p>有限差分应止于最后一个相邻的普通 bin，不把 overflow 混入。邻近差分共享计数，彼此相关；用导数图定位边缘时，不宜把各点简单当作独立计数来求精确误差。</p>')
    p.replace('const Double_t t0L - t0R =','const Double_t t0L_t0R =')
    p.replace('“干净”的时间差信息','已扣除主要 walk 的时间差信息').__class__
    p.replace('“干净”时间差信息','已扣除主要 walk 的时间差信息')
    p.replace('c_{tof} = -L/v_{sc} + (t_{0L}+t_{0R})','c_{tof} = -L/v_{sc} - (t_{0L}+t_{0R})/2')
    p.replace('现在精固定','现在位于')
    p.code(18,p.code(18).replace('3.33* %s','%s/0.299792458').replace('cout << "time offset of tof = "<<mean<<endl;','cout << "time offset of tof = " << mean << " +/- " << fitFunc->GetParError(1) << " ns" << endl;'))
    p.md(19,r'''<h3>3.4 TOF 刻度验证</h3><p>左图蓝色为模拟真值，红色为重建后按估计路径归一化的 TOF。gamma 真值位于 \(1/c=3.33564\) ns/m，重建分布还含时间涨落、位置误差和未知反应深度的影响；不能把红色峰宽直接等同于单端时间分辨。中子速度较小，分布位于更长 TOF 处。</p><p>右图用两端幅度的几何平均观察 TOF—幅度关联。</p>''')
    p.patch_code(20,'tof_true/sqrt(x_true*x_true+5*5)','tof_true/path_true')
    p.md(21,'<h2>4. TTree 的逐事件读取与二次存储</h2><p><code>SetBranchAddress</code> 将已有分支绑定到同类型变量；<code>GetEntry(i)</code> 读取第 i 个事件的活动分支。需要只读部分分支时，再用 <code>SetBranchStatus</code> 设置。</p><h3>示例：Analyze.C</h3><p>把前面拟合得到的 WL、WR 和 TOF offset 传给事件循环。这里的几何与增益取模拟设定，作业中再从数据确定。CloneTree(0) 先复制结构，Fill 时同时保存原量和新增物理量。</p>'+pre(ANALYZE)+'<p>载入后调用 <code>Analyze(WL, WR, mean)</code>。原始输入不修改，结果另存为 calibrated.root。</p>')
    (ROOT/'chapt1/Analyze.C').write_text(ANALYZE+'\n')
    p.md(22,r'''<h2 id="assignment">作业</h2><ol><li>在 TOF—幅度图上选择 gamma 和中子区域，保存并应用 TCutG，不使用 pid 作分析条件。</li><li>比较多个位置切片的 walk 系数及误差，修正两端时间。用探测器边缘确定位置刻度，与模拟设定比较。</li><li>从两端幅度比求增益比与衰减长度，比较时间差位置和电荷比位置。改变相对电荷分辨，观察两种位置估计的变化。</li><li>用 gamma 峰完成 TOF 绝对刻度。按估计路径归一到 1 m，再由 \(\beta=d/(ct)\)、\(E_n=(1/\sqrt{1-\beta^2}-1)m_nc^2\) 求中子动能，与真值比较。将原始量和新增的时间、位置、TOF、能量逐事件保存到新树中。</li></ol><p>重建时只使用测量量；真值用于最后核验。几何路径的单位为 m，时间为 ns，能量为 MeV。</p>''')
    p.code(23,'gROOT->ProcessLine(".L Analyze.C");\nAnalyze(WL, WR, mean);')
    p.save()

def adc():
    p=Page(PAGES[2])
    p.replace('无限精度','浮点精度')
    # Keep the original detector, electronics settings and digitization example.
    p.replace('4095/4','4096/4000')
    p.append(0,r'''<h3>道值、量程与状态</h3><p>12-bit ADC 有 4096 个码。理想 0–4 V 量程的步距为 \(4/4096\) V，约 0.977 mV；码间距不是完整的仪器精度。Pedestal 是无物理信号时的基线分布，均值为 pedestal offset、宽度反映噪声，增加 offset 不保证所有噪声样本都为正。</p><p>本例约定超量程信号饱和到最大码；真实 ADC/TDC 对 overflow、无命中和无效时间的编码应查对应模块。TDC 的符号和有效区间还取决于 common-start/common-stop 等读出方式。</p>''')
    p.md(1,r'''<h2>2. 数字化数据的处理</h2><h3>Pedestal 与有效区间</h3><p>先画原始 channel 分布，识别 pedestal、物理信号和无效码。阈值由噪声水平与信号需求选择。对理想 Gaussian 噪声，单侧超过均值 3σ 的概率约 0.135%；这是纯噪声的越阈概率，不是“该事例为真实信号的概率”。对数、开方及倒数运算前，检查其输入是否有效。</p><h3>量化与 Dithering</h3><p>ADC/TDC 原始整数道值可以直接保留。若 N 表示区间 [N,N+1)，可用 N+0.5 作代表值；变换后的直方图 bin 宽度应与输入步距相称。Dithering 是按“bin 内均匀”近似加上 U(0,1) 的可选做法，并不恢复真实的连续信号，也不改善探测器分辨。</p><p>下面用同一组模拟时间比较 bin 中心取值与 bin 内随机化。两者保持相同的平均刻度，随机化只是改变量化结构的显示，并额外引入随机涨落。</p>''')
    p.code(2,'''TRandom3 rng(1301);
TH1D *hcenter = new TH1D("hcenter","Bin-center values;Mean time (channel);Counts",200,30,70);
TH1D *hdither = new TH1D("hdither","Uniform within-bin model;Mean time (channel);Counts",200,30,70);
for (int i=0; i<100000; ++i) {
    int left = std::floor(rng.Gaus(50,5));
    int right = std::floor(rng.Gaus(50,5));
    hcenter->Fill(((left+0.5)+(right+0.5))/2);
    hdither->Fill(((left+rng.Uniform())+(right+rng.Uniform()))/2);
}
TCanvas *c1 = new TCanvas("c1","Quantization",900,400);
c1->Divide(2,1);
c1->cd(1); hcenter->Draw();
c1->cd(2); hdither->Draw();
c1->Draw();
cout << "Bin centers: mean=" << hcenter->GetMean() << ", RMS=" << hcenter->GetStdDev() << endl;
cout << "Dither model: mean=" << hdither->GetMean() << ", RMS=" << hdither->GetStdDev() << endl;''')
    p.md(3,'<h2>3. 用于后续分析</h2><p>保留原始码和状态，再生成刻度后的幅度、时间。有效性检查与阈值选择记录在分析中；是否使用 dithering 是量化模型的选择，不是所有数据的必做步骤。</p>')
    p.save()

def makeclass():
    p=Page(PAGES[3])
    p.md(6,'<h3>实例化</h3><p><code>ppac t;</code> 用生成代码中记录的默认文件。构造函数的参数是 TTree 指针，不是文件名。若换文件，先打开 TFile、取出树，再传给 ppac：</p>'+pre('TFile *other = new TFile("run0006.root");\nppac tOther(other->Get<TTree>("tree"));'))
    p.append(4,'<p>以下头文件是节选。使用 ROOT 实际生成的完整 ppac.h，不要省略分支指针及 Init/LoadTree 的实现。生成的析构函数会删除当前输入文件，不要再重复释放同一个 TFile。</p>')
    for block in p.container(4).find_all('pre'):
        src=block.get_text()
        if 'TH1D *h1' not in src:continue
        src=src.replace('  //new tree and root file','  if (!fChain) return;\n  //new tree and root file')
        src=src.replace('     if(jentry % 10 ==0) \n         h1->Fill','     h1->Fill')
        src=src.replace('txl<4900 && txr<4900','txl>0 && txr>0 && txl<4900 && txr<4900').replace('tyu<4900 && tyd<4900','tyu>0 && tyd>0 && tyu<4900 && tyd<4900')
        src=src.replace('    tree->Write();','    cout << "Input=" << nentries << ", selected=" << tree->GetEntries() << endl;\n    tree->Write();')
        src=src.replace('"ppac.root"','"ppac_demo.root"')
        (ROOT/'chapt1/ppac1.C').write_text(src+'\n')
        block.replace_with(fragment(pre(src)))
    p.patch_code(13,'ppac.root','ppac_demo.root')
    p.append(14,'<p>重新生成 MakeClass 可能覆盖同名文件，修改前保留自己添加的分析代码；2.4 将演示用继承把生成代码与分析代码分开。TTreeReader 是 ROOT 中另一种带类型检查的读取方式，本章仍沿 MakeClass 的路线完成后续例子。</p>')
    p.md(16,'<h2 id="assignment">作业</h2><p>用 MakeClass 读取前面的模拟数据，为探测器增加两端读出的薄 Veto Wall，按原练习的简化设定生成带电粒子的 veto 信号。比较应用 veto 条件前后的归一化 TOF—幅度二维图，不用 pid 作选择。</p><p>再把测量幅度、时间映射为 12-bit ADC/TDC 道值，保留原始量与状态。选定有效区间后重建位置和 TOF，比较 bin 中心取值与 1.3 的可选 dithering 结果。</p><p>Veto Wall 厚 1 cm，前后距离 5 cm；练习中设带电粒子沉积入射能量的 1/10，中子和 gamma 不产生 veto 信号，响应分辨采用前面的参数。这是该模拟的设定，不是实际探测效率的描述。</p><p><img src="fig/vetowall.png" alt="Veto Wall 与中子探测器"></p>')
    p.save()

if __name__=='__main__':
    import sys
    for name in sys.argv[1:] or ['simulation','reading','adc','makeclass']:
        globals()[name]()
