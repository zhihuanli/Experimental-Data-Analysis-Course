"""Keep the DSSD calibration sequence; make each transformation explicit."""
from lecture_editor import Page,ROOT,pre
import re

p=Page('chapt3/3.1_DSSD_energy_calibration_1.html')
for i,c in enumerate(p.cells):
 if p.container(i) is None:
  code=p.code(i)
  # Only known TH1 pointers, never TF1/TGraph or TCanvas.
  code=re.sub(r'\b(h0|hpeak|hbg|hx1|hx1e)->Draw\(\)',r'\1->Draw("hist")',code)
  code=re.sub(r'\b(h0|hpeak|hbg|hx1|hx1e)->Draw\("same"\)',r'\1->Draw("hist same")',code)
  p.code(i,code)
p.patch_code(8,'s->Search(hpeak, 2, "", 0.01)','s->Search(hpeak, 2, "nobackground nodraw", 0.01)')
p.patch_code(8,'hpeak->Draw("hist");','hpeak->Draw("hist");\nTPolyMarker *peakMarkers=(TPolyMarker*)hpeak->GetListOfFunctions()->FindObject("TPolyMarker");\nif(peakMarkers) peakMarkers->Draw();')
p.append(7,'''<p><code>Search</code> 默认包含本底处理。上一步已显式扣除本底，所以这里用 <code>nobackground</code>，避免重复扣除；<code>nodraw</code> 关闭自动绘图，由 <code>hist</code> 画谱，再显式叠加候选峰标记。hist 只改变显示，不删除直方图误差。参见 <a href="https://root.cern.ch/doc/master/classTSpectrum.html">TSpectrum::Search</a>。</p><p>自动寻峰给的是候选位置，不是精确 centroid。后面仍沿用“识别谱线 → 局部拟合 centroid → 能量刻度 → residual 检查”的顺序。</p>''')
p.md(9,'''<h3>保存与排序候选峰</h3><p><code>vector&lt;Double_t&gt;</code> 存候选位置，<code>push_back</code> 添加一个值。下面的 helper 用 <code>multimap&lt;Double_t,Double_t&gt;</code> 保存“峰高、峰位”，反向遍历得到峰高从大到小的序列；允许相同峰高，避免漏掉等高峰。实际对应哪条 α 谱线，还要结合能谱判断。</p>'''+pre('vector<Double_t> pe;\npe.push_back(993.0);\npe.push_back(1079.0);\n// 若要按位置从小到大排列：\nsort(pe.begin(),pe.end());'))
p.md(10,'<h3>可重复调用的寻峰函数</h3><p>函数只在直方图副本上扣本底，保留原始计数用于后面的峰拟合。<code>backsub=0</code> 表示输入已经扣过本底。</p>'+pre((ROOT/'chapt3/peaks.C').read_text()))
p.patch_code(24,'c1->Draw();','hx1->Draw("hist");\nfor(int i=0;i<4;++i) fg[i]->Draw("same");\nc1->Draw();')
p.save()

p=Page('chapt3/3.2_TTree_Branch_with_Dynamic_Array.html')
p.replace('但对 DSSD 这种稀疏事件来说，它并不适合后续分析。','后续若主要处理有效条，也可以转换为紧凑的 hit 列表。')
p.replace('固定数组的记录方式不仅造成内存和存储空间浪费，也不利于表达一个 DSSD 事件的整体特性，例如不方便一次检查一个 DSSD 中多条的能量信息。','固定数组的下标直接是 strip ID；hit 列表的下标则是本事件内的 hit 编号。两种结构都能使用，区别在于访问方式。')
p.replace('这样，数据结构和物理事件就是一致的。','这些仍是 strip hits；一个粒子可能产生多个 hit，后面还需重建粒子。')
p.replace('Double_t pec[48];','Double_t pee[48];')
p.replace('Double_t rec[48];','Double_t ree[48];')
p.replace('它比固定数组更适合后续所有相关分析。','注意 rid[0]=42 表示“第 0 个 hit 来自第 42 条”，不是“第 0 条”。')
p.append(13,'''<h3>排序不能拆开 hit</h3><p>若按能量排序，同一个 hit 的 strip ID、raw energy、calibrated energy 和 time 要一起移动。不能只排序能量数组，再用原来的条号。判断相邻条用 <code>abs(rid[i]-rid[j])==1</code>，不是 <code>j==i+1</code>。</p><p>最小的交换例子如下，<code>std::swap</code> 逐项保持对应关系。多个 hit 可先对索引排序，或采用 3.8 中的 hit 对象。</p>'''+pre('if (rhit==2 && ree[0]<ree[1]) {\n    std::swap(rid[0],rid[1]);\n    std::swap(rer[0],rer[1]);\n    std::swap(ree[0],ree[1]);\n    // 若记录了时间，也交换两个 hit 的时间。\n}'))
p.save()

p=Page('chapt3/3.3_DSSD_interstrip_correlation.html')
p.replace('These events should be reconstructed as valid cluster events rather than discarded.','对满足两侧能量一致性的 sharing 事例，可把相邻条合成 cluster，保留其能量；相邻条同时有信号本身还不足以确定 sharing。')
p.replace('This band corresponds to one particle sharing its energy between two adjacent strips.','这条负斜率带与同一粒子的电荷在两条间分配相符；后面用已知 α 能量检验加和结果。')
p.replace('The red spectrum contains events affected by adjacent-strip sharing, while the black spectrum contains isolated single-strip events.','红谱选择邻条有信号的事例，黑谱选择两侧邻条均无有效信号的事例。前者富集 sharing，但也可能含串扰或偶然符合。')
p.replace('Recent detector studies also show that interstrip events can be reconstructed effectively rather than treated as unusable events.','')
p.append(12,r'''<p>这里先把两条直线的斜率作等权平均，用于初步估计。可直接检查打印的两个斜率是否接近；若差异超出拟合不确定度，应先检查 cut、能量收集和模型，而不是把不一致隐藏在平均值中。两个已知能量可解增益和 $b_{13}+b_{14}$，不能分别给出两个 offset。</p>''')
p.code(13,p.code(13)+r'''
cout << "Band slopes: " << K13 << " +/- " << f1->GetParError(1)
     << ", " << K14 << " +/- " << f2->GetParError(1) << endl;
''')
p.save()

p=Page('chapt3/3.4_DSSD_FB_correlation_I_DSSD1-new.html')
p.md(0,r'''<h1>3.4 DSSD front-back 关联：pixel-pixel 相对刻度</h1>
<h2>两面信号为什么可以互相刻度？</h2>
<p>同一个粒子在一个 pixel 内沉积能量，两面收集到的电荷来自同一次能量沉积。对电荷收集完整的 single-pixel 事例，
$$E_{\rm true}=E_{x,i}=E_{y,j}.$$</p>
<p>电子学实际记录的是 ADC 幅度 $A_{x,i},A_{y,j}$。由于各条增益和 offset 不同，原始道值不必相等。选择 X 面的一条 $X_r$ 定义参考尺度：
$$E^{(\rm rel)}\equiv A_{x,r},\qquad k_{x,r}=1,\quad b_{x,r}=0.$$
其他条通过线性变换归一到这个尺度：
$$E_{x,i}^{(\rm rel)}=k_{x,i}A_{x,i}+b_{x,i},\qquad
E_{y,j}^{(\rm rel)}=k_{y,j}A_{y,j}+b_{y,j}.$$
正确配对的 single-pixel 事例应满足 $E_{x,i}^{(\rm rel)}\approx E_{y,j}^{(\rm rel)}$。本节求的是这些相对系数，还不是 MeV 刻度。</p>
<h2>从一个 pixel 向另一面传递参考尺度</h2>
<p>固定参考条 $X_{i^*}$，选取与 $Y_j$ 对应的事例，拟合
$$A_{x,i^*}=k_{y,j}A_{y,j}+b_{y,j}.$$
得到 $E_{y,j}^{(\rm rel)}=k_{y,j}A_{y,j}+b_{y,j}$ 后，可以选择已刻度的 $Y_{j^*}$，再拟合
$$E_{y,j^*}^{(\rm rel)}=k_{x,k}A_{x,k}+b_{x,k},$$
从而得到 $E_{x,k}^{(\rm rel)}=k_{x,k}A_{x,k}+b_{x,k}$。这种 pixel-pixel 方法直观，但每个交叉 pixel 都需要足够统计量。3.5 再把多个 pixel 合并到 strip-wise 拟合中。</p>
<h3>与后续多粒子配对的关系</h3>
<p>两粒子分别产生 $X_1,X_2$ 和 $Y_1,Y_2$ 时，仅凭条号不能区分直接与交换配对。归一后的
$$\Delta E=|E_x^{(\rm rel)}-E_y^{(\rm rel)}|$$
可用于检验候选。能量相近时仍可能多解，因此“选最小差”不能保证正确；3.6 会把候选数和配对状态明确保存。</p>''')
# Keep the setup's branch listing, translate the introductory part.
old=p.container(1)
branch=old.find('pre')
branchtext=branch.get_text() if branch else ''
p.md(1,r'''<h2>实验与输入文件</h2><p>本例使用 25 MeV/u 的 $^{16}$C 束流轰击 $^9$Be 靶，测量前向带电碎片。靶后零度方向的望远镜由三层 32×32 DSSD 和 CsI 组成，条宽约 2 mm、条间隔约 0.1 mm。</p><p><code>data/data_16C.root</code> 已去除 pedestal 事例，硬件触发要求 D1、D2 的 X 面 multiplicity≥2。下列 branch 同时提供按 strip ID 排列的原始数组与紧凑 hit 列表；本节从原始幅度的关联出发。</p>'''+pre(branchtext))
p.md(7,'<h2>Front-back 幅度关联</h2><p>先看 X[12] 与 Y[13] 的关联。主条带是建立相对刻度的依据；条带外既可能有 charge sharing，也可能有多个粒子形成的错误组合、阈值效应或其他本底。不能把全部离群点都归为 sharing。</p>')
p.md(9,'<h3>1. 先试两面各一个 hit</h3><p><code>xhit==1 &amp;&amp; yhit==1</code> 可以减少组合歧义。这里硬件偏向多击事件，这种选择的统计量有限，因此还要考察局部条件。</p>')
p.md(11,'<h3>2. 邻条无有效信号：local isolation</h3><p>对于 X[12] 检查 X[11]、X[13]，对于 Y[13] 检查 Y[12]、Y[14]。下面用邻条幅度小于 50 的条件作示例；这个软件阈值应结合各通道 pedestal 和噪声确定，不等同于所有通道已知的硬件阈值。</p><p>它排除了可见的邻条信号，但阈值以下的 sharing 仍可能存在。两条都 isolated，也不能证明它们一定来自同一个粒子；继续检查二维条带和 residual。</p>')
p.patch_code(12,'// no sharing','// 邻条无超过所选阈值的信号')
p.md(15,'''<h3>普通 least squares 与 ROB 拟合</h3><p>这里横轴为 Y[13] 的原始幅度，纵轴为 X[12] 的原始幅度，拟合 <code>X[12]=b+k*Y[13]</code>。普通 least squares 对远离主条带的点较敏感；ROOT 的 <code>ROB</code> 使用 least trimmed squares，以残差较小的子集估计直线。它适用于参数线性模型，不能把这个选项直接用于任意非线性 TF1。</p><p>下面比较两条线及各自的 residual，不预先认定某个拟合更好。ROB 也不能代替事件鉴别。参见 <a href="https://root.cern.ch/doc/master/fitLinearRobust_8C.html">ROOT robust fit 示例</a>。</p>''')
p.replace('Expected results for DSSD1','DSSD1 参考候选样本')
p.md(19,'''<h2>作业：保存 front-back 候选</h2><p>对三层 DSSD，参照上述邻条条件和二维主条带，保存可用于相对刻度的 x-y 候选组合。先在单击样本上观察主条带，再决定多击样本可采用的范围。</p><p>输出记录 <code>source_entry</code>、<code>ix</code>、<code>iy</code>、<code>xe</code>、<code>ye</code>。一个输入事例可以产生多个候选组合，所以不要把输出行数当成粒子数。<code>TCutG::IsInside(x,y)</code> 的参数顺序对应作图的横、纵轴。</p><p>事件循环的核心如下；输入分支的绑定和输出树建立沿用 1.2 的方法。</p>'''+pre(r'''
// 在输入的每个事例中，枚举满足局部条件的 X、Y 条。
for(int i=0;i<32;++i) {
    if(d1x[i]<200) continue;
    if(i>0 && d1x[i-1]>=50) continue;
    if(i<31 && d1x[i+1]>=50) continue;
    for(int j=0;j<32;++j) {
        if(d1y[j]<200) continue;
        if(j>0 && d1y[j-1]>=50) continue;
        if(j<31 && d1y[j+1]>=50) continue;
        // 本节画的是 X:Y，故横轴 Y、纵轴 X。
        if(!cutXY->IsInside(d1y[j],d1x[i])) continue;
        ix=i; iy=j; xe=d1x[i]; ye=d1y[j];
        source_entry=jentry;
        tout->Fill();
    }
}
''')+'<p>另存分析输出，不覆盖提供的原始数据。下面的 <code>data/d1xy.root</code> 是供 3.5 使用的参考候选文件。</p>')
p.save()

p=Page('chapt3/3.5_DSSD_FB_correlation_II_DSSD1-new.html')
p.md(0,'''<h1>3.5 DSSD front-back 关联：strip normalization</h1><p>3.4 用单个 pixel 建立两条间的对应关系。如果某些 pixel 事例很少，可以把已在共同尺度上的多条作为参考，集中统计量刻度另一面。本节保留三步传播：X[16] → Y[8–16] → 全部 X → 全部 Y。</p><p>参考条固定 <code>b=0,k=1</code>，其他条的系数相对于它确定。这样得到的是同一探测器内可比较的相对幅度，不是绝对能量。覆盖范围取决于实际有数据连接的条；没有可用数据的条不应被默认视为已刻度。</p>''')
p.md(3,'<h2>输入与参数表</h2><p><code>data/d1xy.root</code> 保存前一节方法得到的候选：<code>ix,iy</code> 是条号，<code>xe,ye</code> 是两条的 raw amplitude。选择降低了可见 sharing 和远离条带的组合，但样本仍需 residual 检查。</p>')
p.md(5,'<h3>先检查整体关联</h3><p>查看所有候选的 x-y 主条带和离群区域。这一步判断是否有可用的线性关联，不直接给出每条的刻度，也不能证明每个候选都正确。</p>')
p.md(7,'<h3>选择起始参考条</h3><p>统计各条的候选数。本例 X[16] 的统计量较好，并与 Y[8–16] 有较多交叉事例，因而采用这一区域开始传播。除了数量，也应查看幅度覆盖范围和 residual。</p>')
p.md(11,'<p>以下固定 X[16] 为参考，第一步刻度 Y[8–16]。</p>')
p.md(14,r'''<h2>先看一条 Y 如何得到 b、k</h2>
<p>以 Y[12] 为例，选择 <code>ix==16 &amp;&amp; iy==12</code>。横轴是待刻度 Y 的 raw amplitude，纵轴是已刻度 X 的参考幅度；初始参考 X[16] 的幅度就是 <code>xe</code>。因此 <code>pol1</code> 的截距、斜率可直接用于 $E_y^{(\rm rel)}=b_y+k_y A_y$，不要把两轴放反后仍使用同一组系数。</p>''')
p.insert_before(15,[
('code',r'''
tree->SetEstimate(tree->GetEntries()+1);
tree->Draw("xe:ye","ix==16 && iy==12","goff");
TGraph *gExample=new TGraph(tree->GetSelectedRows(),tree->GetV2(),tree->GetV1());
TCanvas *cStripExample=new TCanvas("cStripExample","One-strip normalization",700,430);
gExample->SetTitle("X[16] reference vs Y[12];Raw Y[12];Reference amplitude X[16]");
gExample->SetMarkerStyle(7);
gExample->Draw("AP");
gExample->Fit("pol1","Q ROB");
TF1 *fExample=gExample->GetFunction("pol1");
cout << "Y[12]: b=" << fExample->GetParameter(0) << ", k=" << fExample->GetParameter(1)
     << ", N=" << gExample->GetN() << endl;
cStripExample->Draw();
'''),
('md',r'''<h3>对多条重复相同操作</h3><p><code>parx[i][0/1]</code>、<code>pary[j][0/1]</code> 分别保存 <strong>b、k</strong>。<code>Ex</code>、<code>Ey</code> 按这两张表转换幅度。下面把例行操作分为收集关联点、拟合、画 residual 三部分。</p><p><code>fity</code> 使用已刻度 X 面作纵轴参考，求 Y 系数；<code>fitx</code> 则相反。无逐点误差的 TGraph 拟合输出 RSS/NDF 带有幅度平方单位，不能要求它接近 1 来评价拟合。</p>''')])
old=p.code(15)
# Split the existing tested algorithm without changing its point selection or fitting.
collect=old[:old.index('    cout << Form("%4s')]
collect=collect.replace('void fit(','void collectCorrelations(')
collect=collect.replace('    TGraph *g[32];\n    Int_t   npt[32];','')
collect+='}\n'
p.code(15,'%%cpp -d\nTGraph *g[32];\nInt_t npt[32];\n'+collect)
fitbody=old[old.index('    cout << Form("%4s'):old.index('    DrawResiduals(')]
# It still includes residual creation; move that out so the fit step stays readable.
rstart=fitbody.index('        gResiduals[id] = ')
rend=fitbody.index('        cout << Form("%4d',rstart)
residual=fitbody[rstart:rend]
fitbody=fitbody[:rstart]+fitbody[rend:]
fitcode='void fitCorrelations(Int_t id1, Int_t id2, TString fitmethod) {\n    TString sid = fitmethod=="fity" ? "iy":"ix";\n'+fitbody+'}\n'
rescode=r'''
void showResiduals(Int_t id1, Int_t id2, TString fitmethod) {
    TString sid=fitmethod=="fity" ? "iy":"ix";
    for(int id=id1;id<=id2;++id) {
        double b=fitmethod=="fity"?pary[id][0]:parx[id][0];
        double k=fitmethod=="fity"?pary[id][1]:parx[id][1];
        if(k<=0 || g[id]->GetN()<20) continue;
'''+residual+r'''
    }
    DrawResiduals(id1,id2,Form("c_res_%s",fitmethod.Data()));
    for(int i=0;i<32;++i) delete g[i];
}
void fit(Int_t ix1,Int_t ix2,Int_t iy1,Int_t iy2,TString method) {
    int first=method=="fity"?iy1:ix1, last=method=="fity"?iy2:ix2;
    collectCorrelations(ix1,ix2,iy1,iy2,method);
    fitCorrelations(first,last,method);
    showResiduals(first,last,method);
}
'''
p.insert_before(16,[
('md','<h3>拟合各条并更新系数</h3><p>只拟合至少有 20 个候选点的条，这是本例的最低数量检查，不保证幅度范围或拟合质量。参考 X[16] 始终保持 b=0、k=1，避免改变尺度定义。</p>'),
('code','%%cpp -d\n'+fitcode),
('md','<h3>查看 residual</h3><p>每个点计算“参考幅度 − 新刻度幅度”，在各条的图中检查是否有随幅度变化的弯曲或偏移。绘图使用拟合过的同一批点，属于一致性检查；独立 run 可用于进一步验证。</p>'),
('code','%%cpp -d\n'+rescode)])
p.md(16,'<p>现在三个调用按同一顺序收集、拟合并显示结果，物理选择与前面的单条例子相同。</p>')
p.md(17,'<h2>三步刻度</h2><h3>1. X[16] → Y[8–16]</h3><p>用初始参考条建立中央 Y 区域的共同尺度。</p>')
p.md(19,'<h3>2. Y[8–16] → 全部 X</h3><p>合并已经刻度的 Y 条，增加每条 X 的统计量。X[16] 不改变。</p>')
p.md(21,'<h3>3. 全部已刻度 X → 全部 Y</h3><p>再用有可用系数的 X 条完成其余 Y 条。</p>')
for i in (18,20,22):p.code(i,p.code(i)+'\ngResidualCanvas->Draw();')
p.md(23,'<h2>保存与读取参数</h2><p>文件前 32 行是 X，后 32 行是 Y，每行为 <code>strip b k</code>。无可用数据的条保持 k=0，后续跳过并报告；不能把恒等变换当成它的刻度。</p>')
p.md(26,r'''<h2>检查整体归一结果</h2><p>重新计算全部候选的 $E_x^{(\rm rel)}$ 和 $E_y^{(\rm rel)}$，查看二维主条带及 $E_y^{(\rm rel)}-E_x^{(\rm rel)}$ 是否在零附近、是否随幅度发生漂移。整体主条带正确不替代逐条检查；少数错误系数可能被高统计条掩盖。</p>''')
p.md(30,'''<h2>作业：三层 DSSD 的相对归一与 hit 列表</h2><p>参照三步方法求 DSSD1–3 的参数，检查各条 residual，保存参数。把 raw amplitude 转为相对幅度，选择幅度≥100 的条，分别按两面幅度从高到低排列，条号与幅度一起移动，写入新的 ROOT 文件。</p>'''+pre('Int_t x1hit, y1hit;\nInt_t x1[32], y1[32];\nDouble_t x1e[32], y1e[32];\nDouble_t x1es, y1es;\nInt_t x1m, y1m;')+'''<p>branch 的 leaflist 使用 <code>x1[x1hit]/I</code>、<code>x1e[x1hit]/D</code> 等形式。<code>x1es,y1es</code> 是通过阈值的相对幅度之和；<code>x1m,y1m</code> 只统计相邻有效条的连通组数，不代表已确定的粒子数。DSSD2、3 使用同样结构，保留源事例编号。3.6 再根据两面能量关系判断如何合并或配对。</p>''')
p.refresh();p.save()
