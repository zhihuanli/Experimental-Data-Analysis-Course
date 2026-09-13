"""Correct PPAC geometry, fitting errors, efficiency, and build examples in place."""
from lecture_editor import Page, ROOT, PAGES, pre, fragment
import subprocess
import re

def signals():
    p=Page(PAGES[4])
    p.replace('t_{x2} - t_{x1}','t_{x1} - t_{x2}')
    p.replace('t_{x2}-t_{x1}','t_{x1}-t_{x2}')
    p.append(1,r'''<p>这里 L 指有效读出宽度，T_delay 是两端之间的总延迟。x 的正方向须与两端编号一致；实际刻度的斜率正负由接线和坐标约定确定。位置通道的和减去两倍 anode 时间可消除公共到达时间，但其宽度包含三个通道的测量误差及相关项，不能直接当作单个通道的分辨。</p>''')
    p.replace('beamTrig+must2Trig','beamTrig || must2Trig')
    for i in [16]:
        p.code(i,p.code(i).replace('TH1D*','TH1*').replace('TH1D *','TH1 *').replace('(TH1D*)','(TH1*)'))
    p.append(17,'<p>sum gate 检查的是各路时间是否符合单事例的读出关系，可以抑制一部分 pileup，但不能识别所有重叠脉冲；窗口也会影响有效事件的保留比例。</p>')
    p.save()

def tracking():
    p=Page(PAGES[5])
    # Keep the original derivations and figures. Correct overclaims where the
    # assumptions matter for the example immediately below them.
    p.replace('指数级','按误差平方的倒数')
    for cell in [1,2]:
        for tag in p.container(cell).select('p,li'):
            txt=tag.get_text()
            if '负相关' in txt or '强负' in txt:
                tag.replace_with(fragment('<p>slope 与 intercept 的 covariance 取决于 z 原点及探测器布局，符号不总为负。外推误差使用完整协方差矩阵，不能预先假定忽略交叉项一定使误差偏大或偏小。</p>'))
    p.append(1,r'''<p>\(\arctan k_x\)、\(\arctan k_y\) 是两个投影角；相对 z 轴的极角为 \(\theta=\arctan\sqrt{k_x^2+k_y^2}\)。两点也可确定直线并在已知测量误差下传播参数误差，但 NDF=0，不能用 χ²/NDF 检验拟合。</p><p>束斑中不同事例的真实位置本来就有分布，束斑中心不应仅按各事例的 tracking 误差加权；inverse-variance 平均要求它们测量同一个参数，或在模型中同时纳入束斑的本征宽度。</p>''')
    p.append(2,r'''<p>用于分辨估计的 residual 应区分 included 和 excluded fit。若待测层未参与 tracking、且误差独立，则 \(\sigma_r^2=\sigma_{DUT}^2+\sigma_{track}^2\)；同一层参与拟合时，测量值与预测值相关，不能再用这个加法。探测效率也始终对应所选参考径迹、触发条件和有效面积；x 与 y 的响应不必独立。</p>''')
    src=p.container(5).find('pre').get_text()
    src=src.replace('"tracking.root"','"tracking_demo.root"')
    src=src.replace('"targetX" );','"targetX/F");').replace('&targetX, "targetX"','&targetX, "targetX/F"').replace('&targetY, "targetY"','&targetY, "targetY/F"')
    src=src.replace('    tx = -999; ty = -999;','    tx = -999; ty = -999;\n    c2nx = -1; c2ny = -1;\n    for (int i=0;i<3;++i) { dx[i]=-999; dy[i]=-999; }')
    src=src.replace('(Int_t)(i * k + b)','i * k + b')
    src=src.replace('赋予探测器真实的本征分辨率','输入假设的单层位置误差')
    src=src.replace('"SQ"','"SQN"').replace('if (rx->IsValid())','if (int(rx)==0 && rx.Get() && rx->IsValid())').replace('if (ry->IsValid())','if (int(ry)==0 && ry.Get() && ry->IsValid())')
    src=src.replace('            SetTrace(htf8xz','            if (jentry < 10000) SetTrace(htf8xz').replace('            SetTrace(htf8yz','            if (jentry < 10000) SetTrace(htf8yz')
    src=src.replace('    tree->Branch("xx",','    tree->Branch("source_entry", &source_entry, "source_entry/L");\n    tree->Branch("xx",',1)
    src=src.replace('        TrackInit();','        source_entry = jentry;\n        TrackInit();')
    src=src.replace('        tree->Fill();','        if (c2nx>=0 && c2ny>=0) tree->Fill();')
    src=src.replace('    opf->Close();','    cout << "Input events=" << nentries << ", accepted reference tracks=" << tree->GetEntries() << endl;\n    opf->Close();')
    p.container(5).find('pre').replace_with(fragment(pre(src)))
    p.append(5,'<p>本例固定用 1A、2A、3 三层在两个方向均有效的事件作 reference track，2B 不参与拟合。每层 σ=1 mm 是演示误差传播的假设，不是从本数据已测得的分辨。<code>S</code> 返回拟合结果，<code>Q</code> 减少日志，<code>N</code> 不把逐事件 TF1 挂到 TGraph 上。</p><p>位置与效率分析保留全部合格事件；仅径迹累积图显示输入前 10000 个事件中的合格径迹，以便快速显示。不会按拟合效果挑选显示事例。</p>')
    generated=ROOT/'work/generated_tracking';generated.mkdir(parents=True,exist_ok=True)
    subprocess.run(['/opt/homebrew/opt/root/bin/root','-l','-b','-q','-e',f'TFile f("{ROOT}/chapt2/f8ppac001.root"); f.Get<TTree>("tree")->MakeClass("tracking");'],cwd=generated,check=True,capture_output=True)
    header=(generated/'tracking.h').read_text()
    fields='''
   Double_t xx[3], xz[3], yy[3], yz[3], dx[3], dy[3];
   Double_t xx2b[2], yy2b[2], xz2b, yz2b, anode2b;
   Double_t tx,ty,theta_x,theta_y,sigma_tx,sigma_ty,sigma_thetax,sigma_thetay,c2nx,c2ny;
   Long64_t source_entry;
   void SetBranch(TTree *tree);
   void TrackInit();
   void SetTrace(TH2D *h, Double_t k, Double_t b, Int_t min, Int_t max);
'''
    header=header.replace('#include <TROOT.h>','#include <TROOT.h>\n#include <TH2.h>').replace('public :','public :'+fields)
    # Generated destructor owns its input file. main does not delete it again.
    (ROOT/'chapt2/tracking.h').write_text(header)
    (ROOT/'chapt2/tracking.C').write_text(src+'\n')
    p.md(4,'<h3>tracking.h</h3><p>先对本节的 f8ppac001.root 运行 MakeClass，再在 <code>public:</code> 后补充这些成员。生成的分支绑定、构造函数和 LoadTree 等内容保持原样。</p>'+pre(fields)+'<p>头文件需要 <code>#include &lt;TH2.h&gt;</code>。完整文件与下面的 tracking.C 放在同一目录。</p>')
    p.code(6,'gROOT->ProcessLine(".L tracking.C");\ngROOT->ProcessLine("{ TFile *input=new TFile(\\\"f8ppac001.root\\\"); tracking tr(input->Get<TTree>(\\\"tree\\\")); tr.Loop(); }");\nTFile *f = new TFile("tracking_demo.root");\nTTree *tree = (TTree*)f->Get("tree");')
    # Histograms remain owned by the output file and are retrieved explicitly.
    p.code(6,p.code(6)+'\nTCanvas *c1 = new TCanvas("c1","Tracking");')
    p.code(8,'TH2 *hxz=(TH2*)f->Get("htf8xz");\nhxz->Draw("colz");\nc1->Draw();')
    p.code(9,'TH2 *hyz=(TH2*)f->Get("htf8yz");\nhyz->Draw("colz");\nc1->Draw();')
    for i in [11,20]:
        c=p.code(i).replace('tx:ty','ty:tx').replace('>>(120,-60,60)','>>hbeam(120,-60,60,120,-60,60)')
        p.code(i,c)
    p.append(14,'<p>double-Gaussian 是描述 core 与 tail 的经验模型；宽分量不自动等于本底，窄分量 σ 也不自动等于探测器本征分辨。</p>')
    p.code(17,'''tree->Draw("dx[0]>>hdx(200,-5,5)");
TH1 *hdx = (TH1*)gROOT->FindObject("hdx");
g1->SetParameters(hdx->GetMaximum(),0,0.3);
hdx->Fit(g1,"Q","",-0.5,0.5);
double sigma = fabs(g1->GetParameter(2));
total->SetParameters(g1->GetParameter(0),g1->GetParameter(1),sigma,hdx->GetMaximum()*0.1,0,3*sigma);
total->SetParLimits(0,0,2*hdx->GetMaximum());
total->SetParLimits(3,0,2*hdx->GetMaximum());
total->SetParLimits(2,0.05,5);
total->SetParLimits(5,0.1,15);
TFitResultPtr residualFit=hdx->Fit(total,"S");
cout << "Core sigma=" << total->GetParameter(2) << ", tail sigma=" << total->GetParameter(5) << " mm" << endl;
gPad->SetLogy(0);
c1->Draw();''')
    p.code(24,'''TCut c2btrack = "abs(xx2b[1])<100 && abs(yy2b[1])<60";
TCut c2ba = "anode2b>-900"; // -1000 是该文件的无效标记
TCut c2bx = "abs(xx2b[0])<120";
TCut c2by = "abs(yy2b[0])<75";''')
    p.code(28,'// 下面的分母为同一触发和 fiducial 区域内的 reference tracks。')
    p.code(29,'''Long64_t Ntrack = tree->GetEntries(c2btrack);
Long64_t Na = tree->GetEntries(c2btrack && c2ba);
Long64_t Nx = tree->GetEntries(c2btrack && c2bx);
Long64_t Ny = tree->GetEntries(c2btrack && c2by);
Long64_t Nxy = tree->GetEntries(c2btrack && c2bx && c2by);
if (Ntrack==0 || Na==0) throw std::runtime_error("empty efficiency denominator");
cout << "Reference tracks=" << Ntrack << ", anode=" << Na << endl;
for (Long64_t n : {Nx,Ny,Nxy}) {
    double eff = double(n)/Ntrack;
    cout << "eff=" << eff << " +/- " << sqrt(eff*(1-eff)/Ntrack) << endl;
}
Long64_t Nxa=tree->GetEntries(c2btrack && c2ba && c2bx);
Long64_t Nya=tree->GetEntries(c2btrack && c2ba && c2by);
Long64_t Nxya=tree->GetEntries(c2btrack && c2ba && c2bx && c2by);
cout << "Given anode: x=" << double(Nxa)/Na << ", y=" << double(Nya)/Na
     << ", xy=" << double(Nxya)/Na << endl;''')
    p.md(30,'<h3>效率的含义</h3><p>这里得到的是 reference tracking 样本和指定面积内的条件效率。阳极触发条件下的效率用与阳极同时有效的 numerator，不能把未要求 anode 的 Nx 直接除以 Na。给出的误差是大样本 binomial 近似；x-y 联合效率直接计数，不假设 x、y 独立。</p><p>示例的 fiducial 区域是 |x|&lt;100 mm、|y|&lt;60 mm，位于探测器有效面内。比较不同触发或 reference 组合时使用相同区域，并同时报告分母。</p>')
    p.replace('DetHit[5]','DetHitX[5], DetHitY[5]')
    p.replace('出射角','入射方向的投影角')
    p.append(31,'<p>使用两层时记录 NDF=0，不计算 χ²/NDF。对不同 reference 组合比较效率时，检查共同的几何范围和样本条件，不预先要求结果相等。</p>')
    p.save()

if __name__=='__main__':
    import sys
    for name in sys.argv[1:] or ['signals','tracking']:
        globals()[name]()
