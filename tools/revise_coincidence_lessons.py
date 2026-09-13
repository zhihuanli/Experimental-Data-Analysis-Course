"""Targeted chapter-5 repairs; retain the accepted examples and cell order."""
import re
import nbformat
from lecture_editor import Page, ROOT, PAGES

def finish(p):
    p.refresh()
    p.save()
    path=(ROOT/p.path).with_suffix('.ipynb')
    n=nbformat.read(path,as_version=4)
    n.cells=[c for c in n.cells if c.cell_type!='code' or c.source.strip()]
    for c in n.cells:
        if c.cell_type=='code': c.source=c.source.replace('%jsroot off','%jsroot on')
    if not any(c.cell_type=='code' and re.search(r'^%jsroot on$',c.source,re.M) for c in n.cells):
        n.cells.insert(1,nbformat.v4.new_code_cell('%jsroot on'))
    nbformat.write(n,path)

p=Page(PAGES[20],current=True)
p.replace('$\\gamma - \\gamma$ coincidence','5.0 γ-γ 符合：event building、time walk 与 addback',indices=[0])
p.replace('若两条 $\\gamma$ 射线属于同一级联过程，它们应当在探测器时间分辨范围内表现为 prompt coincidence。','当中间能级寿命远短于探测器时间分辨时，同一级联的两条 $\\gamma$ 射线表现为 prompt coincidence；经过长寿命能级的级联则需要 delayed coincidence 时间窗。',indices=[0])
p.append(0,'<p><code>ge</code> 的单位为 keV，<code>gt</code> 的单位为 ns，都是已换算的量。本节不重复加 dithering；整数 ADC/TDC 的连续化在上游刻度时完成。每个原始 entry 是一个触发读出帧，不等同于一次核衰变。以下只在各读出帧内部按时间重建事件；没有记录的帧间时间不能补出符合事件。</p>')
code=p.code(7).replace('  tin->SetBranchAddress("ghit", &ghit);','  if (tin->GetMaximum("ghit") > MAXHIT)\n    throw std::runtime_error("Increase MAXHIT before reading branches");\n  tin->SetBranchAddress("ghit", &ghit);')
code=code.replace('  Long64_t nentries = tin->GetEntries();','  Long64_t inputHits=0, outputHits=0;\n  Long64_t nentries = tin->GetEntries();')
code=code.replace('    tin->GetEntry(ientry);','    tin->GetEntry(ientry);\n    inputHits += ghit;')
code=code.replace('      tout->Fill();','      outputHits += o_ghit;\n      tout->Fill();')
code=code.replace('  fout->cd();','  std::cout << "Input / output hits = " << inputHits << " / " << outputHits\n            << "; rebuilt events = " << tout->GetEntries() << std::endl;\n  fout->cd();')
p.code(7,code)
p.code(14,p.code(14).replace('(10,0,20)','(21,-0.5,20.5)'))
p.md(15,'<h3>检查高 multiplicity 事件</h3><p>一个 multiplicity 为 <em>M</em> 的事件可产生 <em>M(M−1)/2</em> 个无序 pair，高 multiplicity 事件因而可能明显影响符合矩阵。放射源的真级联、晶体间散射、宇宙线和公共电子学干扰都可能增加 multiplicity，不能仅凭 <code>ghit&gt;5</code> 判为噪声。</p><p>先查看这些事件的时间聚集、晶体分布和能量。若确认某类为公共干扰，再在分析时加 cut，并比较 cut 前后的时间谱、峰强度和保留事例数。这里保存完整的 event-built tree，便于重新检查选择条件。</p>')
p.code(16,'tree->SetScanField(0);\ntree->Scan("ghit:int(gid/7):gid%7:ge:gt","ghit>10","",200,0);')
p.append(21,'<p><code>ProfileY</code> 在这里给出每个能量 bin 内的平均时间差，而非逐 bin 拟合 prompt 峰的位置。只有 prompt ridge 占主导时，这个均值才适合作为 time walk 估计；背景明显时，可对时间切片拟合 prompt 峰后再拟合峰位随能量的变化。</p>')
p.code(23,p.code(23).replace('hp_tw1->Fit("f_tw", "R0");','f_tw->SetParameters(0,1000,-10000,100000); // 经验函数的起始参数\nhp_tw1->Fit(f_tw, "R0");').replace('f_tw->SetRange(50, 1500);','// 50–600 keV 是拟合区间，之外的曲线只是外推。\nf_tw->SetRange(50, 1500);'))
p.replace('p_{0,c,s}\\leftarrow p_{0,c,s}+C_{c,s}.','p_{0,c,s}\\leftarrow p_{0,c,s}-f_{c,s}(E_{\\rm ref})+C_{c,s},\\qquad E_{\\rm ref}=600\\ {\\rm keV}.',indices=[24])
p.replace('经过这种处理后，最终文件中的 gt 已经同时包含 time-walk correction 和高能 offset correction，可以直接用于跨 segment、跨 cluster 的 $\\gamma$-$\\gamma$ coincidence 分析。','下面的实现完成 cluster 内的 time walk 和高能 offset 修正，并保存修正前的 gt_raw 与拟合函数。跨 cluster 的常数 offset $D_c$ 是后续检查项，当前代码没有自动求解和扣除它。不能用 cluster 内部的时间差谱代替这项检查。',indices=[24])
p.append(24,'<p>先完成下面链接中的 pair correction，再继续 addback。没有有效拟合或无法连接到参考 segment 的通道保持原时间，并用 <code>tw_ok</code> 分支标记；不能把“未修正”当成“修正为零”。经验函数在拟合区外属于外推，需要在修正后的能量—时间差图中检查。</p>')
p.md(29,r'<p>下面的检查分别给出高能参考和全能区的时间差。cluster 内 prompt 峰的宽度不能证明 cluster 间已对齐；跨 cluster 检查使用编号固定的参考 cluster 保留时间差的正负号，避免对称填充掩盖 offset。</p><p>本例后续先取 $|\Delta t|&lt;180\ \mathrm{ns}$ 作为 prompt 条件。这个数是工作窗口的半宽，需结合各 cluster 的峰位、宽度及低能区的变化检查，不由单个高能峰的 $\sigma$ 直接保证全部能区的效率。</p>')
p.replace('时间差不在符合时间窗内的 hit pair 通常代表偶然符合，而不是同一物理过程中的真实 $\\gamma$-$\\gamma$ 关联。','避开 prompt 尾部及 delayed 结构后，远时间区的 hit pair 可用于估计偶然符合。不能把所有 prompt 窗外事例都视为随机本底。',indices=[33])
p.append(33,'<p>上图 prompt 和 random 时间窗的总宽度不同，当前显示的是原始计数，先比较结构而非直接比较强度。此外，3 μs event-building 窗口会限制大时间差 pair 的接受度；定量扣除时，需要检查时间差本底及有效时间窗归一化。</p>')
p.append(34,'<p>代码把满足“同一 cluster、相邻晶体、时间差小于 400 ns”的 hit 连成组，再对组内能量求和。这是连通分组：A 与 B、B 与 C 相连即可成组，A 与 C 不一定直接相邻，整组的最大时间跨度也可能超过 400 ns。400 ns 因而是连边条件，不是整组跨度的上限。组的时间及编号取能量沉积最大的一条；原始晶体级分支同时保留。</p>')
p.code(40,p.code(40).replace('"", "");','"", "hist");').replace('"", "same");','"", "hist same");'))
p.replace('假的 summing peak','summing peak（加和峰，不对应单条跃迁）',indices=[41])
p.replace('假的加合峰','不对应单条跃迁的加和峰',indices=[41])
finish(p)

# These two detailed examples were already separate linked notebooks.
p=Page(PAGES[21],current=True)
p.code(0,'%%cpp -d\n'+(ROOT/'chapt4/pair_timewalk_correction.C').read_text())
p.insert_before(0,[('md','<h1>Pair time-walk correction</h1><p>接续 5.0 的 event building，从同一 cluster 内的高能 pair 求相对 offset，再合并有效参考通道，拟合各晶体的 time walk。先看 cluster 6 的图和参数，再处理所有 cluster。下面保留完整实现，也可使用同目录 <a href="pair_timewalk_correction.C">macro</a>。</p>')])
p.append(5,'<p>函数参数初值为 <code>(0,1000,−10000,100000)</code>，用于启动数值优化；能量单位 keV、时间单位 ns。拟合范围为 30–800 keV，画出的延伸段不是额外测量。先检查拟合状态，再在 600 keV 处归一化并加入相对参考 segment 的常数 offset。</p>')
p.append(7,'<p>输出保留 <code>ghit/gid/ge</code> 和各事件的 hit 对应关系；<code>gt</code> 为修正后的时间，<code>gt_raw</code> 保留原时间，<code>tw_ok</code> 表示该通道是否有有效修正。有效拟合函数一并写入文件。这里不做跨 cluster 常数 offset 的二次校准。</p>')
finish(p)

p=Page(PAGES[22],current=True)
p.insert_before(0,[('md','<h1>检查 time-walk 修正</h1><p>先检查各 cluster 内高能参考及全能区的分布，再检查不同 cluster 的高能时间差。比较相同能量选择下的峰位和宽度；全能区出现尾部时，应回到能量—时间差图查找来源。</p>')])
p.append(3,'<p>以下谱只统计同一 cluster 内的 pair；“all”表示把这些谱合并，不是跨 cluster 的时间差。Gaussian 拟合描述 prompt 峰核心，不能代表全部尾部的效率。</p>')
p.insert_before(9,[('md','<h2>跨 cluster 的高能时间差</h2><p>固定 cluster 0 为参考，画 <code>t(cluster)−t(cluster 0)</code>，两条能量均取 600–3000 keV。每个无序 pair 只填一次，不补相反符号。若某个 cluster 的 prompt ridge 系统性偏离零，需要先校正该常数 offset，再应用共同的 prompt gate。</p>'),('code',r'''TFile *fcross=TFile::Open("eurica_time_pair.root");
TTree *tcross=(TTree*)fcross->Get("tree");
int nh, id[MAXHIT]; double energy[MAXHIT], time[MAXHIT];
tcross->SetBranchAddress("ghit",&nh);
tcross->SetBranchAddress("gid",id);
tcross->SetBranchAddress("ge",energy);
tcross->SetBranchAddress("gt",time);
TH2F *hcross=new TH2F("hcross","High-energy cross-cluster timing;Cluster;#Deltat (ns)",11,0.5,11.5,160,-800,800);
for (Long64_t n=0;n<tcross->GetEntries();++n) {
    tcross->GetEntry(n);
    for (int i=0;i<nh;++i) {
        if (id[i]/7!=0 || energy[i]<600 || energy[i]>3000) continue;
        for (int j=0;j<nh;++j) {
            if (id[j]/7==0 || energy[j]<600 || energy[j]>3000) continue;
            hcross->Fill(id[j]/7,time[j]-time[i]);
        }
    }
}
TCanvas *ccross=new TCanvas("ccross","Cross-cluster timing",800,450);
hcross->Draw("colz");
ccross->Draw();''')])
finish(p)

p=Page(PAGES[23],current=True)
p.replace('γ-γ coincidence matrix','5.1 γ-γ 符合矩阵与开窗谱',indices=[0])
p.paragraph(0,'在忽略', '<p>本节将各探测器的能量换算到共同的 keV 标尺，合并不同探测器对的能量关联，不保留角度坐标。对强度作定量解释时，仍需考虑各探测器对的效率及角关联；合并并不意味着所有探测器响应相同。</p>')
p.paragraph(0,'这种处理隐含的前提是','<p>对称填充来自交换同一 pair 的两个坐标，不要求各探测器效率和分辨率完全相同。两轴采用相同的刻度单位与选择条件，就可把它们作为无序能量对来显示。镜像的两个计数来自同一 pair，不能当成两次独立测量。</p>')
p.code(1,p.code(1)+'\nTH1::SetDefaultSumw2(); // 本底相减之前保留各 bin 的计数方差')
code=p.code(6).replace('  tree->SetBranchAddress("ahit",&ahit);','  if (tree->GetMaximum("ahit")>maxhit) throw std::runtime_error("Increase maxhit before reading");\n  tree->SetBranchAddress("ahit",&ahit);')
code=code.replace('        if (i == j) continue;','        if (i == j || aid[i] == aid[j]) continue;\n        if (ae[i]<30 || ae[j]<30) continue;')
code=code.replace('  fout->Write();','  std::cout << "Ordered pair rows = " << tout->GetEntries() << std::endl;\n  fout->Write();')
p.code(6,code)
p.append(5,'<p>本例要求两条 addback hit 的能量均不低于 30 keV，代表晶体编号不同，避免同一晶体重复脉冲的组合。循环保留两个坐标顺序；若全部 pair 都通过选择，一个 <em>M</em> 重事件贡献 <em>M(M−1)</em> 行，而不是 <em>M</em> 行。</p>')
p.append(11,r'<p>prompt 与 random 矩阵在这里用于对照结构，尚未相减。若随机时间差密度与接受度在两个窗口中相同，才可按总宽度使用 $\alpha=360/5200$；本例 3 μs 分组使大时间差的 pair 接受度改变，定量相减应先确定有效暴露比例。避免把 prompt 尾部或真实 delayed 级联放入 random 窗。</p>')
p.code(16,p.code(16).replace('TH2D *hgg = (TH2D*)','TH2 *hgg = (TH2*)').replace('ProjectionX("hproj")','ProjectionX("hproj",1,hgg->GetNbinsY())'))
p.code(22,p.code(22).replace('>>hgg(','>>hgg_gate_view('))
p.paragraph(25,'如果 peak 窗',r'<p>这里三个窗等宽且中心对称，代码定义 $G_{\rm side}=(G_L+G_R)/2$，再做 $G_{\rm net}=G_P-(G_L+G_R)/2$。这一平均能估计局部线性本底在中心 peak 窗下的贡献；side gate 不能包含其他峰。若窗宽或位置不对称，应按宽度和本底斜率重新归一化。</p>')
p.append(25,r'<p>忽略不同窗之间的事件相关性时，逐 bin 有 $\sigma^2_{\rm net}=N_P+(N_L+N_R)/4$，ROOT 的 <code>Sumw2</code>、<code>Scale</code> 和 <code>Add</code> 会传播这些项。多重事件可同时贡献多个 pair，因此该式不是所有积分量的完整事件级误差；特别不能把矩阵两侧的镜像计数视作独立样本。</p>')
p.code(27,p.code(27).replace('TH1D','TH1').replace('hpeak->Draw();','hpeak->Draw("hist");').replace('800,1000','850,700'))
finish(p)

p=Page(PAGES[24],current=True)
p.replace('$\\gamma-\\gamma$ 对称矩阵的整体减本底方法：Radware approach','5.2 γ-γ 对称矩阵的整体减本底：Radware approach',indices=[0])
code=p.code(1).replace('double emax = 1530.0','double emax = 1500.0')
code=code.replace('  tree->SetBranchAddress("ahit", &ahit);','  if (tree->GetMaximum("ahit")>MAXHIT) throw std::runtime_error("Increase MAXHIT before reading");\n  tree->SetBranchAddress("ahit", &ahit);')
code=code.replace('int nhit = std::min(ahit, MAXHIT);','int nhit = ahit; // 容量已在读取数组之前检查，不截断 hit')
code=code.replace('    if (ientry % 100000 == 0)', '    if (ientry % 2000000 == 0)')
code=code.replace('  TFile *fout = new TFile(outfile, "recreate");','  std::cout << "Prompt matrix fills = " << hgg->GetEntries()\n            << "; regular-bin sum = " << hgg->Integral() << std::endl;\n  TFile *fout = new TFile(outfile, "recreate");')
p.code(1,code)
p.append(0,'<p>本节与 5.1 使用相同的 30 keV 阈值、180 ns prompt 半宽和不同代表晶体条件。矩阵每轴 0–1500 keV、1 keV/bin；全矩阵填充数与普通 bin 内的计数分别输出，区间外事例留在 overflow，不纳入下面的投影及归一化。</p>')
p.code(4,p.code(4)+'\nhdt_sym->Draw("hist");\nc1->Draw();')
p.code(6,p.code(6).replace('%jsroot off','%jsroot on'))
p.code(9,p.code(9).replace('ProjectionX("hproj")','ProjectionX("hproj",1,hgg->GetNbinsY())'))
p.replace('D.C. Radford, Nucl. Instr. Meth. A361(1995)306','D. C. Radford, “Background subtraction from in-beam HPGe coincidence data sets,” Nuclear Instruments and Methods A 361 (1995) 306–316. DOI: 10.1016/0168-9002(95)00184-0.',indices=[12])
p.append(12,'<p><a href="Radford.pdf">原论文</a>给出了这个近似的推导及适用条件。上面的响应分解先讨论真符合；若输入 prompt 矩阵仍含随机的 peak–peak 组合，它们也会进入 peak–peak 成分，不能靠这一个公式自动识别。</p>')
code=p.code(14).replace('ProjectionX("hproj")','ProjectionX("hproj",1,hgg->GetNbinsY())')
code=re.sub(r'    if \(Pi < 0\) Pi = 0;\n    if \(pi < 0\) pi = 0;\n    if \(pi > Pi\) pi = Pi;','',code)
code=re.sub(r'      if \(Pj < 0\) Pj = 0;\n      if \(pj < 0\) pj = 0;\n      if \(pj > Pj\) pj = Pj;','',code)
code=code.replace('      if (Bij < 0) Bij = 0;','      // 保留模型计算结果，不把扣除后的负波动截为零。')
code=code.replace('hggb->SetBinError(ix, iy, std::sqrt(Bij));','hggb->SetBinError(ix, iy, 0.0); // 条件误差：未包含从本矩阵估计 B 的不确定度')
code=code.replace('  double T = hproj->Integral();','  double T = hproj->Integral();\n  if (T<=0) throw std::runtime_error("Empty projection");')
p.code(14,code)
p.code(20,p.code(20).replace('gPad->SetLogz();','gPad->SetLogz(0); // 线性颜色轴保留负波动'))
p.code(23,p.code(23).replace('gPad->SetLogy();','gPad->SetLogy(0);').replace('ProjectionX("hproj_raw")','ProjectionX("hproj_raw",1,hgg_input->GetNbinsY())').replace('ProjectionX("hproj_net")','ProjectionX("hproj_net",1,hgg_radware->GetNbinsY())'))
p.md(24,r'<p>扣除后连续平台应降低，主要峰应保留；若出现成片负结构，应检查一维本底估计与全局近似，而非把负值删掉。单个负 bin 也可能只是统计波动。</p><p>本底 $B$ 从同一个矩阵估计，因此不能把它当作独立 Poisson 计数、直接给出 $\sqrt{B}$ 误差。应有 $$\mathrm{Var}(M-B)=\mathrm{Var}(M)+\mathrm{Var}(B)-2\mathrm{Cov}(M,B).$$本例主要演示本底形状，代码保留原计数的条件误差，没有计算后两项。若定量提取弱峰强度，可按原始事件重抽样、每次重建矩阵和本底，以估计完整统计误差；一维本底模型选择的影响需另行比较。</p><p>降低真实实验本底仍然重要，例如使用 anti-Compton shield、粒子或 recoil 符合条件；数值减本底不能替代这些物理选择。</p>')
p.md(27,'<p>比较三幅图中的连续条带和局部符合点。约 (80,80) keV 的结构与 <sup>133</sup>Ba 的低能级联有关；约 (80,121) keV 的不同核素交叉结构用于检查残余本底。全局扣除可改变这些点的强度，但某个交叉点减弱或消失本身，不证明时间偶然符合已被正确扣除。</p>')
p.code(29,p.code(29).replace('int bin2 = hgg->GetXaxis()->FindBin(gateE + gateWidth);','// 上边界不重复包含恰好落在下一 bin 起点的区间。\n  int bin2 = hgg->GetXaxis()->FindBin(std::nextafter(gateE+gateWidth,-INFINITY));'))
p.md(39,'<p><code>gate(160)</code> 和 <code>gate(80)</code> 的连续本底与纵轴尺度不同，视觉上的峰高不能直接比较。对于已经对称填充的矩阵，同一个 80×160 keV 矩形区域与它的转置计数应相同。因此不能由“一边看起来有峰，另一边看不见”断定不符合，应比较对应区域、局部本底及可能的加和峰污染。</p>')
p.paragraph(45,'检查符合关系时不要只看一个方向。','<p>反向 gate 可帮助检查峰重叠、邻近本底和选择条件，但对称矩阵的镜像不是独立证据。确认弱符合还需比较 random 窗、局部 side gate 和能级关系，不能只依赖反向谱中是否看见同一个峰。</p>')
p.replace('Radware 方法本身不能区分不同反应道。','本节使用的基本全局公式不自动区分不同反应道。',indices=[46])
p.append(46,'<p>原论文还讨论了针对 E2 bump 等相关连续本底的修正。因此“存在相关本底”不是弃用这一方法的理由，而是进一步检验和改进本底模型的依据；本例保留基本公式，便于先理解 total projection、peak 成分与二维本底的关系。</p>')
p.replace('原则上，偶然符合时间窗的选择应紧挨着符合时间窗的两个对称时间窗。','偶然符合窗可选在 prompt 两侧，但应避开峰尾及 delayed 结构。上面的时间窗宽度比要求两个区域具有相同的随机时间差密度和接受度；存在有限 event window 或非均匀束流时间结构时，要改用有效暴露量的比例。',indices=[46])
p.replace('所有符合关系应用反向开窗交叉检查。','用反向开窗检查峰重叠与本底，并结合 side gate 及已知级联关系判断。',indices=[47])
finish(p)
