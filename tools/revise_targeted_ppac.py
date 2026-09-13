"""Targeted PPAC revisions: retain the signal -> tracking -> program workflow."""
from lecture_editor import Page, ROOT, pre
import re

p=Page('chapt2/2.1_PPAC_analysis.html')
p.replace('$(\\Delta t_{x2} - \\Delta t_{x1})$', '$(\\Delta t_{x1} - \\Delta t_{x2})$')
p.replace('得到刻度系数 $k = L / 2T_{xdelay}$。','得到线性刻度 $x=k\\,\\Delta t+b$。理想模型给出 $k=L/(2T_{xdelay})$；实际采用 mask 峰位的拟合结果，并检查各孔位置的 residual。')
p.replace('(与束流速度无关，分布表现为一个极窄的峰，直接反映探测器本征时间分辨率)','（公共到达时间被抵消，分布通常变窄；宽度包含两端及 anode 定时误差和相关项。）')
p.replace('Trigger = beamTrig + must2Trig','触发样本可用 beamTrig || must2Trig 选择；两个标记也可能同时为 1。')
p.replace('必须消除束流动量弥散带来的 $TOF$ 展宽','可先消除公共 $TOF$ 引入的展宽')
p.md(2,'<h2>2. 原始信号与 time-sum</h2><p>先查看各路 TDC 道值。这个文件的编码范围为 0–4095；以下用 10–4000 排除端点附近的无效读数，再检查时间组合的分布。这里仍是 TDC channel，尚未换算为时间单位。</p>')
p.code(16,r'''
TCanvas *c4 = new TCanvas("c4","Time sums",1000,400);
c4->Divide(2,1);
c4->cd(1);
tree->Draw("dt_x2+dt_x1>>hdt_xsum(1500,0,1500)",cut_xvalid,"hist");
TH1 *hdt_xsum = (TH1*)gROOT->FindObject("hdt_xsum");
double xm = hdt_xsum->GetBinCenter(hdt_xsum->GetMaximumBin());
TF1 *fx = new TF1("fx","gaus",xm-25,xm+25); // 只拟合主峰附近
hdt_xsum->Fit(fx,"RQ");
fx->Draw("same");
double xpeak=fx->GetParameter(1), xsigma=abs(fx->GetParameter(2));
gPad->SetLogy();

c4->cd(2);
tree->Draw("dt_y2+dt_y1>>hdt_ysum(1500,0,1500)",cut_yvalid,"hist");
TH1 *hdt_ysum = (TH1*)gROOT->FindObject("hdt_ysum");
double ym = hdt_ysum->GetBinCenter(hdt_ysum->GetMaximumBin());
TF1 *fy = new TF1("fy","gaus",ym-25,ym+25);
hdt_ysum->Fit(fy,"RQ");
fy->Draw("same");
double ypeak=fy->GetParameter(1), ysigma=abs(fy->GetParameter(2));
gPad->SetLogy();
cout << "X sum: mean=" << xpeak << ", sigma=" << xsigma << " channels\n"
     << "Y sum: mean=" << ypeak << ", sigma=" << ysigma << " channels\n";
c4->Draw();
''')
p.md(17,r'''<h3>Time-sum 选择</h3>
<p>正常的两端信号应满足近似固定的 time-sum。若两粒子在延迟线传输时间内到达，两端可能记录了不同粒子的最早信号，time-sum 就可能偏小。δ rays 也可造成提前的读出信号。因此，峰外事件不能全称为 pileup，落在峰内也不能保证没有重叠。</p>
<p>下面以主峰的 ±3σ 作为示例 gate。先看上图主峰和尾部，再选择保留范围；σ 来自主峰附近的 Gaussian 拟合，不是对整个尾部的拟合。gate 的宽度决定了选择效率。</p>
<p>实验中的 time-sum 与 δ-ray 效应见 S. Kumagai et al., <a href="https://arxiv.org/abs/1311.0215">Delay-line PPACs for the BigRIPS separator</a>, Nucl. Instrum. Methods B 317 (2013) 717–727。</p>''')
for i in (18,19,20):
 c=p.code(i).replace('xpile','xsum').replace('ypile','ysum').replace('xypile','xysum')
 p.code(i,c)
# The old red lines were an unrelated manually chosen gate. Derive them from the fitted gate instead.
code=p.code(15)
code=re.sub(r'TLine \*tlx1.*?tlx2->Draw\("same"\);','',code,flags=re.S)
code=re.sub(r'TLine \*tly1.*?tly2->Draw\("same"\);','',code,flags=re.S)
p.code(15,code)
p.insert_before(21,[
('md',r'''<h2>3. 位置刻度与边界 cut</h2>
<p>这里用 $L$ 表示<strong>半宽</strong>，物理灵敏区为 $-L&lt;x&lt;L$（前面 delay-line 公式中的总宽度为 $2L$）。有限分辨使测量位置 $x_{\rm rec}=x+\delta x$ 在物理边界外也有分布。不能把谱中最外侧的非零 bin 强行刻度到 ±L；mask 孔或 slit 的已知位置才提供独立的位置基准。只有照明分布与边缘响应已知时，才适合用边缘模型辅助刻度。</p>
<p>下图仅用均匀照明、Gaussian 分辨 σ=1 mm、半宽 L=120 mm <strong>说明边界展宽</strong>，不是对本组 PPAC 数据的拟合。左图为测量分布在右边缘的变化；右图为真实位置给定时，通过 $|x_{\rm rec}|&lt;L$ 的概率。</p>'''),
('code',r'''
TCanvas *cBoundary=new TCanvas("cBoundary","Resolution at an active edge",1000,380);
cBoundary->Divide(2,1);
TF1 *edge=new TF1("edge",
 "0.5*(TMath::Erf((x+[0])/(sqrt(2)*[1]))-TMath::Erf((x-[0])/(sqrt(2)*[1])))",
 114,126);
edge->SetParameters(120,1); // half-width L, assumed sigma, in mm
cBoundary->cd(1);
edge->SetTitle("Uniform illumination, Gaussian response;x_{rec} (mm);Relative density");
edge->Draw();
TLine *boundary=new TLine(120,0,120,1);
boundary->SetLineStyle(2); boundary->Draw();
cBoundary->cd(2);
TF1 *survival=(TF1*)edge->Clone("survival");
survival->SetRange(114,120);
survival->SetTitle("Acceptance of |x_{rec}|<120 mm;True x (mm);Cut survival probability");
survival->Draw();
cout << "At x=L: " << survival->Eval(120)
     << "; at x=L-sigma: " << survival->Eval(119) << endl;
cBoundary->Draw();
'''),
('md',r'''<h3>怎样选择边界？</h3>
<p>若目的是测量探测器内部的读出效率，先用<strong>不包含待测 PPAC 的 reference track</strong>预测位置，并选择 $|x_{\rm ref}|&lt;L-d$ 的内部区域。$d$ 根据参考径迹的不确定度及边缘响应选择，不能直接用待测层自己的位置定义分母。下一节采用的 $|x_{\rm ref}|&lt;100$ mm、$|y_{\rm ref}|&lt;60$ mm 就是在 240×150 mm² 灵敏区内留下边缘余量。</p>
<p>若分析要求测量坐标也落在 ±L 内，可以再加这个 cut，但删去的边缘事件属于<strong>位置选择损失</strong>，不应直接解释为探测器没有响应。也可以保留边界外的少量测量尾部，再通过 residual 和本底确定是否可靠。没有一条对所有束斑和分辨都适用的固定放宽范围。</p>
<p>在同一 reference 样本内，分别数出 $N_{\rm ref}$、有有效读数的 $N_{\rm valid}$、以及读数通过边界 cut 的 $N_{\rm pass}$：</p>
<p>$$\epsilon_{\rm read}=\frac{N_{\rm valid}}{N_{\rm ref}},\qquad
\epsilon_{\rm cut}=\frac{N_{\rm pass}}{N_{\rm valid}},\qquad
\epsilon_{\rm selected}=\frac{N_{\rm pass}}{N_{\rm ref}}
=\epsilon_{\rm read}\epsilon_{\rm cut}.$$</p>
<p>这是计数定义，不要求两个过程独立。若已用最后一个比值作总效率修正，就不要再重复修正边界损失。真实边界处的 cut 保留概率约为 50%，不表示全探测器损失一半；总损失还取决于束斑在边缘的粒子比例。</p>''')])
p.refresh();p.save()

p=Page('chapt2/2.2_PPAC_tracking.html')
p.replace('本实验中采用的重建策略','一般重建策略与本例的选择')
p.replace('因此实际上$x$ 方向与 $y$ 方向的径迹重建是完全独立进行的。','因此可以分别收集有效的 $x$ 和 $y$ 测量点，重建两个投影。下面的演示固定选择 1A、2A、3 在两个方向均有效的样本；作业再实现按方向选择有效点。')
p.replace('残差 (Residual) 计算（用于评估位置分辨率）','included residual 计算（先检查径迹与测量的一致性）')
p.replace('（用于求阳极本征效率）','（用于统计参考样本内的阳极响应效率）')
# Preserve the covariance derivation, remove the contradictory beam-weighting recipe.
c=p.container(1)
heading=next(h for h in c.find_all(['h2','h3','h4']) if '2. 协方差' in h.get_text())
for node in list(c.contents):
 if node is heading: break
 node.extract()
p.container(1).insert(0,__import__('bs4').BeautifulSoup(r'''<h3>靶点位置与入射方向的不确定度</h3>
<p>外推精度由单层测量误差、探测器间距以及外推距离共同决定。三个测量点不一定比相距较远的两个点有更好的角度精度。这里先假定每层位置误差为 1 mm，说明 ROOT 如何把测量误差传播到靶点与方向；这个数值不是本数据的分辨测量结果。</p>''','html.parser'))
p.replace('得到靶点位置的真实方差','得到模型内的靶点位置方差')
p.replace('得到角度的真实绝对误差','一阶误差传播得到投影角的标准不确定度')
p.md(2,r'''<h3>4. 位置分辨：先区分两种 residual</h3>
<p>准直源或 mask 可用于独立测量。若测量位置是真实照明位置与独立读出误差之和，则方差相加：
$\sigma_{\rm measured}^2=\sigma_{\rm illumination}^2+\sigma_{\rm det}^2$。
均匀照明宽度为 $w$ 的狭缝，其位置方差是 $w^2/12$，不是 Gaussian 峰宽。拟合时可把已知照明分布与分辨函数卷积。源、束流的电离密度及边缘散射不同，所得分辨也可能不同。</p>
<p>束流实验可用其他 PPAC 预测待测层（DUT）的位置。定义
$r_i=x_i-\hat x_{-i}(z_i)$，其中下标 $-i$ 表示拟合中<strong>没有使用第 i 层</strong>。若 DUT 与参考测量误差独立，且直线模型足够描述径迹，</p>
<p>$$\sigma_{r_i}^2=\sigma_i^2+\sigma_{\rm pred}^2(z_i),\qquad
\sigma_{\rm pred}^2(z_i)=C_{00}+2z_i C_{01}+z_i^2 C_{11}.$$</p>
<p>因此，residual 的宽度还要扣除 reference track 的预测方差，才能估计单层分辨。参考层分辨若未知，可结合多层的 excluded residual 建立方差方程；不能把演示中假设的 1 mm 当作已经测出的输入。多重散射、对准误差和读出相关性也会影响这个关系。</p>
<p>相反，若第 i 层已经参与拟合，$x_i$ 与预测位置相关，included residual 通常较窄，不能套用上述方差相加公式。下面先画 included residual 检查径迹一致性，再画未参与拟合的 2B residual。</p>
<h3>5. 探测效率：分母由谁提供？</h3>
<p>用阳极有效的事例作分母，得到的是<strong>给定阳极响应后的</strong>位置读出效率：
$\epsilon_{x|a}=N_{x\cap a}/N_a$。它不计入阳极自身漏掉的事例。</p>
<p>用独立 reference tracks 作分母，可估计该触发及照明样本内的响应效率。先要求参考径迹通过 DUT 的内部有效区域，再统计 DUT 的 anode、x、y 与 x-y 是否有效。参考径迹及分母的 cut 不使用 DUT 信号；x-y 联合效率直接计数，不假定 x 与 y 独立。</p>
<p>本文件中的位置已在上游处理阶段作过有效性选择。因此，下文“有效读数”指文件中仍保留的有效坐标，不能据此拆分上游已丢失的电子学响应与 time-sum 选择损失。若要分开测量这些效率，应从原始信号逐级计数。</p>''')
p.replace('生成 tracking.root','生成 tracking_demo.root')
p.md(14,r'''<h3>Residual 与 χ²/NDF</h3>
<p>先看参与拟合的 1A residual。分布有窄核和尾部，可以用 double-Gaussian 作经验描述；两项本身不能分别认定为“真实信号”和“本底”。窄核宽度是该 residual 的描述参数，不是单层探测器分辨。</p>
<p>χ²/NDF 用于检查直线与测量点的一致性。它依赖输入的位置误差；本例统一输入 1 mm，因此下面的 10、20 只是演示如何查看不同拟合一致性的样本，不是经过标定的通用判据。只有两点时 NDF=0，不能用这个比值。</p>''')
p.code(15,'// 先给窄核初值，再拟合包含尾部的分布。')
p.patch_code(16,'TH1F *hdx;\nDouble_t sigma;','')
p.code(12,p.code(12).replace('tx:ty>>htx','ty:tx>>htx_beam'))
p.code(21,p.code(21).replace('tx:ty>>','ty:tx>>'))
for i in (18,19):
 p.code(i,p.code(i).split('//从chi2')[0])
p.insert_before(22,[
('md',r'''<h3>待测层 2B 的 excluded residual</h3>
<p>2B 没有参与 1A、2A、3 的拟合，因此可直接比较 <code>xx2b[0]</code>（测量值）和 <code>xx2b[1]</code>（预测值）。以下拟合中心 ±1.5 mm 的主峰，打印的是 residual 的 core σ。先检查中心是否偏离零以及尾部；分辨的进一步提取再使用上面的预测方差公式。</p>'''),
('code',r'''
TCanvas *cDUT=new TCanvas("cDUT","Excluded residual of PPAC 2B",1000,380);
cDUT->Divide(2,1);
cDUT->cd(1);
tree->Draw("xx2b[0]-xx2b[1]>>hDutX(240,-6,6)","xx2b[0]>-900","hist");
TH1 *hDutX=(TH1*)gROOT->FindObject("hDutX");
TF1 *dutX=new TF1("dutX","gaus",-1.5,1.5);
hDutX->Fit(dutX,"RQ"); dutX->Draw("same");
cDUT->cd(2);
tree->Draw("yy2b[0]-yy2b[1]>>hDutY(240,-6,6)","yy2b[0]>-900","hist");
TH1 *hDutY=(TH1*)gROOT->FindObject("hDutY");
TF1 *dutY=new TF1("dutY","gaus",-1.5,1.5);
hDutY->Fit(dutY,"RQ"); dutY->Draw("same");
cout << "Excluded core sigma X=" << abs(dutX->GetParameter(2))
     << ", Y=" << abs(dutY->GetParameter(2)) << " mm (not intrinsic resolution)\n";
cDUT->Draw();
''')])
p.code(24,r'''
TCut c2btrack = "abs(xx2b[1])<100 && abs(yy2b[1])<60"; // reference position
TCut c2ba = "anode2b>-900";
TCut c2bx = "xx2b[0]>-900"; // 文件中的有效读数，与边界 cut 分开
TCut c2by = "yy2b[0]>-900";
TCut c2bInside = "abs(xx2b[0])<120 && abs(yy2b[0])<75";
''')
p.md(25,'<h3>1. 选择 reference tracks</h3><p>分母只由 reference track 定义。内部区域避开物理边缘，不使用 2B 的测量位置。以下统计合并触发样本；比较 beamTrig 与 must2Trig 时，分子、分母应同时加上相同触发条件。</p>')
p.code(29,p.code(29)+r'''
Long64_t Npass=tree->GetEntries(c2btrack && c2bx && c2by && c2bInside);
if (Nxy==0) throw std::runtime_error("no valid xy readings");
cout << "Nref=" << Ntrack << ", Nvalid(xy)=" << Nxy << ", Npass=" << Npass << '\n';
cout << "xy read efficiency=" << double(Nxy)/Ntrack
     << ", boundary-cut survival=" << double(Npass)/Nxy
     << ", selected efficiency=" << double(Npass)/Ntrack << '\n';
''')
p.replace('绝对探测效率（方法一：Tracking 外推作为分母）','reference 样本内的响应效率（Tracking 外推作为分母）')
p.replace('（结果应相近）','；差异可能来自几何接受度、粒子组成或参考选择的偏差')
p.replace('以及散射角分布','以及入射方向的投影角分布')
p.replace('拟合卡方值（chi2/ndf）','拟合卡方值及 NDF（仅 NDF>0 时计算 chi2/ndf）')
p.replace('传输效率计算：','靶区接受度：')
p.replace('（即靶的几何接受度/传输效率 $\\varepsilon_{target}$）','（说明分母采用全部束流触发，还是成功重建的束流触发；两者分别还包含或不包含重建损失）')
p.md(5,'<h3>tracking.C：逐事件计算</h3>'+pre((ROOT/'chapt2/tracking.C').read_text())+
'''<p>本例固定使用 1A、2A、3 的有效测量，2B 不参与拟合。<code>SetPointError(i,0,1)</code> 输入假设的 1 mm 位置误差；<code>S</code> 返回结果和协方差，<code>Q</code> 减少逐事件日志，<code>N</code> 不向图附加每次拟合的函数。轨迹图只累积输入前 10000 个事例中的合格径迹，结果树保留全部合格事例。</p>''')
p.refresh();p.save()

# Keep the same compilation lessons, but stop duplicating the entire tracking algorithm.
for lesson,num in [('chapt2/2.3_comiling_1.html',1),('chapt2/2.4_compiling_2.html',2)]:
 p=Page(lesson)
 base=ROOT/f'chapt2/code/compile{num}'
 main=(base/'main.cpp').read_text()
 if num==1:
  intro='''<h1>2.3 编译执行：从 ROOT macro 到独立程序</h1>
<h2>1. 运行方式</h2><p>2.2 中的宏由 ROOT 的 Cling 即时编译。<code>.L tracking.C+</code> 则使用 ACLiC 编译并加载宏。本节把同一算法编译为终端中可调用的程序，方便传入 run 号、批量处理文件。改变的是程序入口和文件管理，不是 tracking 方法。</p>
<h2>2. 目录与 MakeClass</h2><p>本例位于 <code>code/compile1</code>。<code>main.cpp</code> 管理输入输出，<code>include/tracking.h</code> 声明类，<code>src/tracking.C</code> 保存 2.2 的计算过程。生成 MakeClass 框架时不要覆盖已经修改的分析文件；可以在新目录中生成并比较。</p>'''
 else:
  intro='''<h1>2.4 编译执行：分开数据读取与分析代码</h1>
<p>这一节保留 2.3 的 tracking 算法。区别是把它从 MakeClass 生成的文件中移到 <code>ana</code> 类。以后 branch 变化需要重新生成 reader 时，物理分析代码仍保留在自己的文件中。</p>
<h2>1. 文件与继承关系</h2><p>本例位于 <code>code/compile2</code>。<code>tracking.h/C</code> 由 MakeClass 生成，负责读取 branch；<code>ana.h/ana.cpp</code> 是用户分析代码。<code>main.cpp</code> 仍负责打开文件和保存结果。</p>'''+pre('class ana : public tracking {\npublic:\n    TTree *fOutTree;\n    ana(TTree *input, TTree *output)\n        : tracking(input), fOutTree(output) {}\n    void Analysis();\n    // xx、yy、tx 等计算变量及方法声明见完整 ana.h\n};')+'''<p><code>: tracking(input)</code> 调用基类构造函数，绑定输入树；<code>fOutTree(output)</code> 保存输出树指针。<code>Analysis()</code> 中的 <code>GetEntry</code>、径迹拟合和 <code>Fill</code> 与上一节相同，不需要再复制一遍学习。</p>'''
 items=[('md',intro),('md','<h2>2. 主程序：参数、文件、分析调用</h2><p><code>argc</code> 是参数个数，<code>argv[1]</code> 是 run 号。没有提供目录时，输入在章目录，输出在本例程序目录。下面代码与实际 main.cpp 一致；读取失败时返回非零值，供批处理脚本判断。</p>'+pre(main)),
 ('md','<h2>3. Makefile：编译与链接</h2>'+pre((base/'Makefile').read_text())+'''<p><code>root-config --cflags</code> 提供 ROOT 头文件及编译选项，<code>--libs</code> 提供链接库。包含头文件解决声明问题，链接解决函数实现问题，两者不能互相替代。修改源码后重新执行 <code>make</code>；编译失败先看第一条 error。</p>'''),
 ('md',f'''<h2>4. 运行和核对</h2><p>在章目录执行下面两行。程序读取 <code>f8ppac001.root</code>，写出 <code>code/compile{num}/out001.root</code>。原始文件不变。使用同一输入与选择条件时，输出事例编号、靶点位置及拟合参数应与 2.2 一致，而不只是比较最终事例数。</p>'''),
 ('code',f'!make -C code/compile{num}\n!cd code/compile{num} && ./tracking 1'),
 ('md',f'''<p>完整源码：<a href="code/compile{num}/main.cpp">main.cpp</a> · <a href="code/compile{num}/include/tracking.h">tracking.h</a> · <a href="code/compile{num}/src/tracking.C">tracking.C</a>'''+(f' · <a href="code/compile2/include/ana.h">ana.h</a> · <a href="code/compile2/src/ana.cpp">ana.cpp</a>' if num==2 else '')+'</p>')]
 p.rebuild(items);p.save()

p=Page('chapt2/2.5_data_analysis_process.html')
p.md(1,'''<p>实验数据分析通常沿着<strong>解码 → 刻度 → 事件重建 → 物理分析</strong>展开。原始信号保存一次；在耗时或反复使用的阶段保存中间结果。改变 PID cut 时，不必重新解码。</p><p>每个结果应能追溯到输入 run、事例编号和所用刻度。直方图便于检查，TTree 保留逐事件信息，两者用途不同。</p><h2>第一阶段：从原始读数到可分析的信号</h2><p>DAQ 原始文件按电子学插件协议保存数据块，包含 ADC/TDC 道值、通道地址及 overflow 等状态。读取格式之前，先确认本实验使用的插件协议和 mapping。</p>''')
p.md(5,'''<h3>步骤二：有效信号与可重建信息</h3><p>先按各通道的范围和状态判断有效性，再计算位置、能量等组合量。缺失与真实零值分开保存；无效标记不参与刻度、求和和拟合。</p><p>例如 PPAC 两端时间差可以在 anode 缺失时计算，但本节的 time-sum 检查需要 anode。是否保留这类位置，要用独立 reference tracks 检查 residual 和误判率，不能只因为公式仍能计算就认定结果有效。若采用不同重建方法，在输出中保存方法标记。</p>''')
p.md(14,r'''<h2>第二阶段：事件重建与物理分析</h2>
<p>用刻度后的信号构建粒子 hit，处理相邻条的 charge sharing、front-back 对应关系和探测器间符合，再计算位置、能量及时间。第三章将逐步处理 DSSD 的这些问题。</p>
<p>物理选择常来自 ΔE–E 或 TOF–ΔE 的 PID、prompt 时间区间以及几何或运动学约束。选择后的数据仍可能含本底，且 cut 会改变效率与接受度。</p>
<p>在确定的反应假设下，用能量和方向计算 Q 值、激发能等物理量。截面还需要束流归一、靶厚、探测效率与接受度。重建和选择参数保存在结果旁，后续改变 cut 时就能知道哪些步骤需要重算。</p>''')
p.md(15,'''<h2>批量处理多个 run</h2><p>先确认单个文件能正常处理，再用 Bash 循环调用 2.4 的程序。下面脚本接收起止 run、输入目录、输出目录和程序路径；每个 run 单独留日志，失败时继续处理其他 run，最后返回失败状态。</p>'''+
 pre((ROOT/'chapt2/run_batch.sh').read_text())+'''<p>在章目录运行：</p>'''+pre('bash run_batch.sh 1 1 . batch_output code/compile2/tracking')+'''<p><code>"$var"</code> 保留路径中的空格；<code>&gt;log 2&gt;&amp;1</code> 把正常输出和错误都写入日志。输入文件缺失或程序返回非零状态时，该 run 不被当作成功结果。再次运行前先检查输出目录，避免覆盖此前结果。</p>''')
p.save()
