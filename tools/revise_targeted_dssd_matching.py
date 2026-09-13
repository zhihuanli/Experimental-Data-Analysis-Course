"""Turn the existing multiplicity examples into explicit candidate tests."""
from lecture_editor import Page,ROOT,pre
import re

p=Page('chapt3/3.6_DSSD_Multiplicity_Analysis.html')
p.md(0,'''<h1>3.6 DSSD multiplicity：从条的组合到粒子候选</h1><p>本节沿着“两面幅度和 → multiplicity 相关 offset → 相邻条 → 候选配对”的顺序，判断一片 DSSD 中有几个粒子、位置在哪里、每个粒子分配多少能量。</p><p><code>data/cal_16C.root</code> 保存逐条的相对刻度结果。以 DSSD1 为例：</p>'''+pre('Int_t x1hit, y1hit;       // 超过阈值的条数\nInt_t x1[32], y1[32];     // 条号；有效长度由 x1hit/y1hit 给出\nDouble_t x1e[32], y1e[32];// 相对幅度，还不是 MeV\nDouble_t x1es, y1es;     // 两面相对幅度和\nInt_t x1m, y1m;           // 相邻条的连通组数')+'''<p><code>xhit</code> 不等于粒子数；<code>xm</code> 也只是空间连通组数。两个相邻 hit 可能来自一个粒子的 sharing，也可能来自两个相邻粒子，不能先无条件合并再当成答案。</p>''')
p.md(2,'<h2>1. 两面总幅度的一致性</h2>')
p.md(4,'<h3>条的 multiplicity</h3><p>先比较 X、Y 两面有效条数。两面 hit 数不同不一定意味着数据无效。</p>')
p.md(6,'<h3>两面幅度和的差</h3><p>差值不总在零附近，而出现相隔近似固定幅度的结构。接着查看它与两面 hit 数之差的关系。</p>')
p.md(8,'<h3>幅度和之差与 multiplicity 之差</h3><p>观察不同 hit 数差对应的中心位置，检查是否可由共同 offset 描述。</p>')
p.md(10,r'''<h3>共同 offset 为什么要逐条修正？</h3>
<p>设相对归一后的单条幅度为 $A_i'$，绝对能量还需共同变换 $E_i=kA_i'+b$。若两面有效条数为 $m_x,m_y$，
$$xes=\sum_{i=1}^{m_x}A'_{x_i},\qquad yes=\sum_{j=1}^{m_y}A'_{y_j},$$
则两面能量和为
$$E_x=k\,xes+m_xb,\qquad E_y=k\,yes+m_yb.$$
对于电荷收集完整的事例 $E_x=E_y$，因此
$$xes-yes=(m_y-m_x)\frac{b}{k}.$$</p>
<p>上图的斜率给出共同 offset 的线索。本参考刻度采用 $b/k=-25,-25,-30$，分别对应 DSSD1、2、3。把每条幅度加上 $b/k$ 后再求和，避免两面条数不同产生人为偏移。这些数值属于本参考刻度；重新求相对刻度后需重新检查。</p>''')
# Keep the original detector-response figure embedded in this cell.
figs=''.join(str(x) for x in p.container(13).find_all('img'))
p.md(13,r'''<h3>相邻条信号与剩余趋势</h3>
<p>共同 offset 修正后仍有随幅度变化的 residual。邻条耦合、阈值以下未记录的共享电荷及收集不完整，都可能造成这种趋势；仅凭幅度和不能区分这些机制。</p>
<p>原图展示几类相邻条关联：A 区有 sharing 条带，B、C 区为一强一弱的相关信号，D 区在 pedestal 附近。右图放大弱信号区域，显示弱信号可随主信号增加。若弱信号低于读出阈值，相应电荷与 hit 数就不在记录中。</p>'''+figs+'''<p>当前谱中约 40/6000≈0.67% 的残余偏移，在总能量上不大，但对要求数个幅度单位精度的配对仍可能重要。下面的 gate 保留了这项实验特征；不通过修改事件幅度把它“拉直”。</p>''')
p.md(14,r'''<h3>两面总能量 gate</h3><p>在 $xesc$ 对 $(xesc-yesc)$ 的图上，沿主条带选择候选。文件 <code>cutd1esc.cut</code> 等保存的是本参考数据使用的多边形。这个 gate 检查<strong>全事件的能量和</strong>，并未决定单个粒子的 x-y 对应。</p>''')
p.md(17,r'''<h2>2. 把每种分类当成待检验的假设</h2>
<p>下面保留原有拓扑图，但读图时先说清：哪些 hit 归为一个粒子，哪些两面信号互相配对。条号检查相邻关系；能量关系检验候选。这里的 <code>x1ec0</code> 指第 0 个 X hit 修正后的幅度，并不指第 0 条。</p>
<table><thead><tr><th>候选</th><th>检验量</th><th>需要比较的替代假设</th></tr></thead><tbody>
<tr><td>X、Y 各两条，各自对应一个粒子</td><td>$r_1=X_0-Y_0,\ r_2=X_1-Y_1$</td><td>交换 Y：$X_0-Y_1,\ X_1-Y_0$</td></tr>
<tr><td>X 两条，Y 三条中的 a、b 共享</td><td>$r_1=X_i-(Y_a+Y_b),\ r_2=X_{1-i}-Y_c$</td><td>枚举相邻的 a、b，并对 i=0、1 都检验</td></tr>
<tr><td>两面各三条，三粒子</td><td>三个 $X_i-Y_{\pi(i)}$</td><td>三条 Y 的全部 6 个排列</td></tr>
</tbody></table>
<p><strong>斜条带本身不是正确配对的证据。</strong>前面已经限制两面能量和，所以两粒子的 $r_1+r_2\approx0$；错误配对也可落在负斜率线上。需要两个 residual 同时接近零，并检查是否还有其他候选也通过。共享条求和后，组的能量顺序可能变化，不能继续假定原先按单条能量排序的下标就是配对顺序。</p>
<p>以下图分别展示若干候选的 residual，而不是自动完成分类。稍后用一个完整的两条对三条实例，把这种检验写成可执行的判断。</p>''')
p.md(21,'<h3>X 两条、Y 三条：尝试 Y 侧的 sharing 组</h3><p>三个面板组分别尝试 (0,1)、(1,2)、(0,2)。括号里是 hit 下标；对应条号相邻才允许求和。图中只显示一种对应，实际判断还要交换两个 X 候选。</p>')
p.md(23,'<h3>X 三条、Y 两条</h3><p>与上一种情况对称，在 X 面枚举相邻组，并比较两种与 Y 的对应关系。</p>')
p.md(25,'<h3>两面各三条</h3><p>先显示按当前能量顺序直接配对的三个 residual 之间的关系。三粒子判断要检验三项，同时比较 6 种排列；只看其中一对接近零还不够。</p>')
pair23=(ROOT/'chapt3/dssd_pairing.h').read_text()
function=pair23[pair23.index('inline int Pair23'):pair23.index('// 相邻两层')].strip()
p.insert_before(27,[
('md',r'''<h2>3. 可运行实例：X 两条、Y 三条</h2>
<p>选择 DSSD2 中两条 X 互不相邻、Y 恰有一个相邻双条组的事例，检验“两粒子，其中一个在 Y 面 sharing”的模型。不先加总能量 gate，以便看见全部几何候选的 residual。</p>
<p>对每个相邻组，计算 <code>rGroup</code> 和 <code>rSingle</code>，并尝试 X 的两种对应。下面的函数返回通过条件的候选数。一次求和包含几条，就逐条扣几次共同 offset，不能只给整个组扣一次。</p>'''),
('md',pre(function)+'''<p><code>tolerance</code> 是两个 residual 各自允许的绝对差。下面以相对幅度 15 为演示值，结合候选分布检查；它不是已标定的 3σ，也不是所有幅度和 multiplicity 都通用的宽度。精细分析可由干净样本确定随幅度与共享条数变化的匹配宽度。</p>'''),
('md',r'''<h3>输入、状态与输出</h3><p>完整事件循环见 <a href="reconstruct_two_particles.C">reconstruct_two_particles.C</a>，配对函数见 <a href="dssd_pairing.h">dssd_pairing.h</a>。输入为 <code>data/cal_16C.root</code>，输出另存为 <code>two_particle_candidates.root</code>。</p>
<ul><li><code>nCandidates=1</code>：在本两粒子模型中唯一，记录两个粒子的条号、幅度和 residual。</li><li><code>nCandidates=0</code> 或大于 1：保留无解或多解状态，<code>hit=0</code> 表示本例未给出确定重建，不表示物理上没有粒子。</li></ul>
<p>X 面两个分开的 hit 提供两个粒子的幅度；Y 共享组暂以较大幅度条定位，并保存其成员 <code>ymask</code>，不声称取得了亚条位置分辨。这里只检验一种两粒子拓扑，三粒子共条等替代模型仍由后面的作业讨论。</p>'''),
('code',r'''
gROOT->ProcessLine(".L reconstruct_two_particles.C");
gROOT->ProcessLine("reconstruct_two_particles(15);");
TFile *fCandidates=new TFile("two_particle_candidates.root");
TTree *candidateTree=fCandidates->Get<TTree>("tree");
candidateTree->Scan("source_entry:nCandidates:hit:x:y:e:residual","hit==2","",3);
'''),
('md','<h3>候选分布与通过选择的唯一解</h3><p>左图每个几何假设贡献一个点，右图每个唯一通过的事例贡献一个点。右图集中在零附近是筛选条件的结果，不是独立证明；需要同时看左图及打印的无解、多解计数。</p>'),
('code',r'''
TCanvas *cCandidates=new TCanvas("cCandidates","Two-by-three reconstruction",1000,400);
cCandidates->Divide(2,1);
cCandidates->cd(1);
fCandidates->Get<TH2>("hCandidates")->Draw("colz"); gPad->SetLogz();
cCandidates->cd(2);
fCandidates->Get<TH2>("hUnique")->Draw("colz"); gPad->SetLogz();
cCandidates->Draw();
''')])
p.md(27,r'''<h2>作业</h2>
<p>把上面的候选检验推广到两面各三条的事例：分别考虑三粒子的不同排列，以及一侧或两侧发生 sharing 的两粒子假设。参照原有 residual 图，比较哪些候选能同时满足各粒子的能量关系，再统计唯一解、多解和无解。</p>
<p>对于 X 两条、Y 三条的三粒子假设，还需考虑两粒子共用一条 X。此时 $X_{\rm shared}\approx Y_a+Y_b$，两个粒子的幅度可取来自能分辨它们的 Y 面；不能把完整的 $X_{\rm shared}$ 分别赋给两粒子，否则能量重复计数。</p>
<p>在新 ROOT 文件中保存每层的粒子候选 <code>hit,e[hit],x[hit],y[hit]</code>、重建类别、候选数和原事例编号。不要求仅凭本节信息给所有拓扑强行唯一解；保存未解决的状态，后续可引入层间位置关系检验。原始和参考文件保留不变。</p>''')
p.refresh();p.save()

p=Page('chapt3/3.7_DSSD_data_analysis.html')
p.replace('3.6 节已经完成单片内部的相对刻度统一与 multiplicity 相关能量偏移修正，因此本节可以直接在粒子层面讨论探测器间关联。','本节使用提供的完整参考重建文件 evt_16C.root，在单片相对幅度尺度上讨论层间关联。3.6 的可运行实例只覆盖一种拓扑，不是该完整参考文件的全部生成算法。')
p.md(2,'<h2>1. 相邻探测器的幅度关联</h2><p>先看所有事例，再选择每层一个或两个 hit。这里 <code>Draw("e1:e2")</code> 按数组下标组成点，不会判断是否来自同一个粒子。图中连续分布可能含误配、散射、反应或电荷收集不完整，不能只从二维图决定来源。</p>')
p.md(7,'<h3>每层各两个 hit</h3><p>两个粒子在不同厚度的探测器内沉积能量的大小次序可能不同。因此两层各自按能量排序后，第 0 个 hit 不一定属于同一个粒子。先画未经重配的图，后面用位置检查两种对应关系。</p>')
p.md(9,'<h2>2. 位置关联</h2><h3>每层一个 hit</h3>')
p.md(14,'<h3>位置相容选择后的幅度关联</h3><p>先看每层一个 hit 的样本，观察位置条件对连续分布的影响。</p>')
p.md(16,'<h3>每层两个 hit：仍按原下标筛选</h3><p>下面的数组 cut 可逐对保留当前下标下的位置相容点；它没有尝试交换配对，也没有保证一个事例的两个粒子都已匹配。</p>')
layer=(ROOT/'chapt3/dssd_pairing.h').read_text()
func=layer[layer.index('inline int PairLayers'):layer.index('#endif')].strip()
p.insert_before(18,[
('md',r'''<h2>3. 明确完成两粒子的层间配对</h2>
<p>以 DSSD2–DSSD3 为例，一个事例只有两种一一对应：直接 $(0\to0,1\to1)$ 与交换 $(0\to1,1\to0)$。每种对应都要求<strong>两个粒子</strong>在两个方向的条号差不超过 2；同一个下游 hit 不重复分配。</p>
<p>这个位置范围沿用前面单击样本的观察，是本例的几何相容条件。实际装置若有平移、旋转或较大入射角，应先把 strip 坐标转成实验室坐标，再按实际几何预测位置，不能把 ±2 条当作普适条件。</p>'''),
('md',pre(func)+'''<p>返回 0 或 1 时采用对应排列；返回 −1 表示无相容解，−2 表示两种都相容。能量接近或位置过近的粒子可能多解，不能仅为保留事例而强行指定。</p>'''),
('md','<h3>运行事件循环并保留对应关系</h3><p><a href="match_dssd_layers.C">match_dssd_layers.C</a> 使用上面的函数，输出 <code>matched_layers23.root</code>。保存输入文件的行号、原 <code>jentry</code>、状态和 <code>partner[i]</code>，其中 partner 是 DSSD2 第 i 个粒子对应的 DSSD3 下标。所有输入事例都保留；不属于本例 two-by-two 类的状态为 −3。</p>'),
('code',r'''
gROOT->ProcessLine(".L match_dssd_layers.C");
gROOT->ProcessLine("match_dssd_layers(2);");
TFile *fMatched=new TFile("matched_layers23.root");
TTree *matched=fMatched->Get<TTree>("tree");
matched->Scan("file_entry:source_entry:status:partner:de:ee","status==1","",3);
'''),
('md','<h3>用同一批事例比较配对前后</h3><p>两图都只使用得到唯一几何解的事例，每个事例都画两个点。左图按原数组下标，右图使用 partner 重新对应，因此图的差别来自重配，不是额外删去某些点。其他类、多解与无解的计数已在上面单列。</p>'),
('code',r'''
TCanvas *cMatched=new TCanvas("cMatched","Layer matching comparison",1000,430);
cMatched->Divide(2,1);
cMatched->cd(1); fMatched->Get<TH2>("hBefore")->Draw("colz"); gPad->SetLogz();
cMatched->cd(2); fMatched->Get<TH2>("hAfter")->Draw("colz"); gPad->SetLogz();
cMatched->Draw();
''')])
p.md(18,r'''<h2>4. 绝对能量刻度</h2><p>目前坐标仍是各层自己的相对幅度 $a_d$。对每个粒子，前面的共同 offset 已按条数修正并加和，理想线性模型下还需确定各层共同增益，使 $E_d=k_d a_d$；如果重新引入非零 offset，要说明它作用于单条还是重建粒子，不能重复修正。</p>
<p>用已知粒子种类、有效硅厚度和入射方向计算理论 ΔE–E 曲线，再与经过配对的实验条带比较，可以约束增益。峰位标准、已知入射能量或独立厚度测量提供额外约束；不要把能量增益、厚度、粒子种类都任意浮动后认作唯一刻度。</p>
<p>本节完成层间关联的实例，没有从未知粒子混合条带直接给出 MeV 参数。相对幅度可以先用于观察和筛选；需要报告绝对能量或与能量损失计算作定量比较时，再使用独立验证的绝对刻度。</p>''')
p.md(19,'<h3>回看原始重建记录</h3><p>抽查几行，确认条号、幅度与数组顺序。上面的事件循环已打印一个实际需要交换的事例及其对应位置。</p>')
p.code(20,p.code(20).replace('100,1','5,1'))
p.md(21,'<p>跨层位置条件提供了本节可直接使用的约束。若仍有多个候选，可在完成能量刻度后加入已知粒子的 ΔE–E 关系，或加入同一实验中独立测得的靶点约束。第二章 PPAC 与这里不是同一组逐事件数据，不能把两个文件直接拼接进行这项验证。</p>')
p.refresh();p.save()
