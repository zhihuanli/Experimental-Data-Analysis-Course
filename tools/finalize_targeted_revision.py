"""Last consistency pass, without replacing executed outputs."""
from lecture_editor import Page,ROOT,PAGES,pre,fragment
import re

for rel in PAGES[4:17]+PAGES[18:]:
    path=ROOT/rel
    p=Page(rel,current=True)
    # Preserve the course's existing assignment links after editing the headings.
    for h in p.soup.select('h1,h2,h3'):
        if h.get_text().strip().startswith(('作业','Assignment')) and not p.soup.find(id='assignment'):
            h['id']='assignment'
    p.save()

p=Page('chapt2/2.2_PPAC_tracking.html',current=True)
p.replace('tracking.root','tracking_demo.root',indices=[3])
p.replace('绝对探测效率','reference 样本内的响应效率')
p.replace('拟合卡方值（','拟合卡方值与 NDF（')
p.replace('chi2/ndf','NDF>0 时另存 chi2/ndf',indices=[33])
# Explain the actual interior-sample result without claiming it tests the physical edge.
for i in range(len(p.cells)):
    c=p.container(i)
    if c is not None and c.get_text().startswith('效率的含义'):
        p.append(i,'<p>本次运行中，内部 reference 区域的有效 x-y 读数全部通过物理边界 cut，故 εcut=1。这与刻意避开边缘的选择一致，不能据此推断边缘也没有损失；上游已删除的坐标还需回到 raw data 才能检查。</p>')
p.save()

p=Page('chapt3/3.2_TTree_Branch_with_Dynamic_Array.html',current=True)
for a,b in [('xdet[xhit]','xdet[384]'),('xid[xhit]','xid[384]'),('xe[xhit], xec[xhit]','xe[384], xec[384]'),
 ('ydet[yhit]','ydet[384]'),('yid[yhit]','yid[384]'),('ye[yhit], yec[yhit]','ye[384], yec[384]')]:
    p.replace(a,b,indices=[0])
p.replace('// 1-128','// 0-127',indices=[0])
p.replace('上面的 [xhit]、[yhit] 表示事件中有效元素个数；实际 C++ 内存数组要给出容量上限。','上述数组容量 384 对应三个 128 条探测器；事件中的有效长度由 xhit、yhit 给出，写进 ROOT leaflist。')
p.save()

p=Page('chapt3/3.1_DSSD_energy_calibration_1.html',current=True)
p.patch_code(24,'fg[i]->SetParameters(cpe[i], mpe[i], 4);','fg[i]->SetParameters(cpe[i], mpe[i], 4);\n    fg[i]->SetRange(mpe[i]-5,mpe[i]+8);\n    fg[i]->SetLineColor(kRed+1);\n    fg[i]->SetLineWidth(2);')
p.save()

p=Page('chapt3/3.5_DSSD_FB_correlation_II_DSSD1-new.html',current=True)
for i in range(len(p.cells)):
    if p.container(i) is None and p.code(i).strip().startswith('calibrateAndPlot('):
        p.code(i,p.code(i)+'\nTCanvas *cCheck=(TCanvas*)gROOT->GetListOfCanvases()->FindObject("c_check");\ncCheck->Draw();')
p.save()

p=Page('chapt3/3.5_DSSD_FB_correlation_II_DSSD1_multi-path.html',current=True)
c=p.container(0)
# Put the independence assumptions next to the formulas instead of contradicting them later.
for heading in list(c.find_all(['h2','h3','h4'])):
    if 'Explicit Uncertainty' in heading.get_text():
        heading.insert_after(fragment(r'''<p>下面四个逐项平方和是<strong>忽略相关项的近似</strong>，用于读懂参数如何传递。一般形式是 $C_v=J C_uJ^T$；同一次直线拟合的 slope 与 intercept 通常相关，完整计算需要它们的 covariance。参考条的 σ=0 仅表示相对单位被固定，不表示探测器没有测量误差。</p>'''))
p.replace('To combine them consistently, we use inverse-variance weighting: candidates with smaller propagated uncertainty receive larger weights.','若各候选确实独立，可以按 inverse variance 作标量组合。不同路径复用了事例或共享有误差的参考时，要先纳入路径间的 covariance；“来自不同路径”本身不等于独立。')
p.replace('until the strip parameters become stable. This provides a more explicit algorithmic generalization of the strip-normalization idea introduced in the main tutorial.','这个流程描述如何产生候选，不是把同一批 pixel 数据反复当作独立新信息来缩小误差。下面的实例只演示固定、互不重叠的路径，并保留每条路径内的参数 covariance。')
p.save()
