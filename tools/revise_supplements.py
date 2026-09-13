"""Repair original ROOT-reference examples without changing their sequence."""
from lecture_editor import ROOT,PAGES,Page,pre,fragment

p=Page(PAGES[1],current=True)
for i,side in [(7,'L'),(9,'R')]:
    old=f'TH2 *walk{side} = (TH2*)gROOT->FindObject("walk{side}");\nTProfile *prof{side} = walk{side}->ProfileX("prof{side}");'
    new=f'TProfile *prof{side} = new TProfile("prof{side}","Walk calibration;1/sqrt(A{side});Mean time (ns)",50,0,0.6);\ntree->Draw("t{side}:1/sqrt(A{side})>>prof{side}", center_cut, "prof");'
    p.patch_code(i,old,new)
p.paragraph(6,'TProfile 保存','<p>TProfile 直接保存每个横轴 bin 内的事件平均时间及其误差，拟合斜率给出 W。左图用 TH2 显示分布，右图用相同事件直接填充 TProfile，避免把纵轴 bin 中心当作原始时间。位置切片有有限宽度，幅度比也有噪声，因此这是近似校准，可比较不同切片的结果。示例中的 pid 用于展示已知粒子的响应，作业改用图形选择。</p>')
p.replace('const Double_t t0L - t0R = 5.5 - 20.4;','const Double_t t0L_t0R = 5.5 - 20.4;')
for node in list(p.soup.select('.jp-RenderedMarkdown li,.text_cell_render li')):
    if 'mean' in node.get_text() and '-26.27' in node.get_text():
        node.replace_with(fragment('<li><strong>左图：</strong>对几何飞行时间减去已扣除 walk 的平均时间作图，拟合中心值作为时间偏移；数值见代码输出。</li>'))
p.replace('此时尚未进行绝对时间校准','此时尚未进行绝对时间校准')
p.save()

p=Page('chapt1/ROOT_tips.html',current=True)
for a,b in [('“','"'),('”','"'),('b_MyBrancy','b_MyBranch'),('ntuple->','tree->'),('tr->','tree->')]:p.replace(a,b)
p.replace('Each file contains one tree called "T"','Each file contains one tree called "tree"')
p.replace('new TChain("chain", "chainname")','new TChain("tree")')
p.replace('zet<51")','zet<51");')
p.replace('counts >>+ h")','counts >>+ h");')
for block in p.container(1).find_all('pre'):
    if 'counts>>h(100' in block.get_text():
        block.replace_with(fragment(pre('tree->Draw("counts>>h(100,0,100)"); // 指定 nbin、xmin、xmax')))
for tag in list(p.container(1).select('p')):
    if 'bug' in tag.get_text():tag.replace_with(fragment('<p>默认 TH1F 的每个 bin 用 Float_t 存储；单位计数累加超过 2^24 后不再保持整数精确性。高统计量或加权数据可预先定义 TH1D。这是浮点表示精度，不是 10^5 处的 ROOT bug。</p>'))
p.replace('float array of V','double array of V')
p.replace('TGraph *gr = new TGraph','TGraph *gr = new TGraph')
for tag in list(p.container(2).select('p')):
    txt=tag.get_text()
    if 'fEstimate=10000' in txt:tag.replace_with(fragment('<p>GetV1/GetV2 等缓冲区由 GetEstimate() 控制，不能假定固定容量。Draw 前设置足够容量；数组分支展开后的行数可能多于事件数。数据指针会被下一次 Draw 更新，应及时复制。</p>'))
    elif 'greater than 10000' in txt:tag.replace_with(fragment('<p>下面的 SetEstimate 示例适用于每个事件只产生一行的 scalar 表达式。</p>'))
p.replace('tree->SetEstimate(tree->GetEntries());','tree->SetEstimate(tree->GetEntries()+1);')
p.replace('tree->Draw("py:px","pz>4");','tree->SetEstimate(tree->GetEntries()+1);\ntree->Draw("py:px","pz>4","goff");')
p.replace('gStyle->SetStatStyle(0);','gStyle->SetOptStat(0);')
p.replace('gStyle->SetPalette(1)','gStyle->SetPalette(kViridis);')
p.replace('h->Fill(x,y);','h->Fill(x[i],y[i]);')
p.replace('h->Draw("colz")','h->Draw("colz");')
p.replace('g->SetPoint(g->GetN(), x,y)','g->SetPoint(g->GetN(), x,y);')
p.replace('gROOT->ProcessLine("tree->Draw("x")");','gROOT->ProcessLine("tree->Draw(\\"x\\")");')
p.append(0,'<p>这些片段分别说明一种用法；输入文件、tree 名与变量名须与实际文件一致。使用 TChain 时，每个文件中对应 tree 的分支名和类型也应一致。</p>')
p.save()

p=Page(PAGES[18],current=True)
p.append(10,'<p>TH1::Integral 累加 bin content；TF1::Integral 积分连续函数。只有当函数表示“每个等宽 bin 的期望计数”时，后者才除以 bin width 来换算计数。若函数本来是计数密度，直接积分；变宽 bin 应逐 bin 处理。此例只比较积分定义，不是从这些点拟合得到 f。</p>')
p.append(12,'<p>这里把任意 x 区间扩展到完整 bin 的外边缘。FindBin 返回包含 x 的 bin；恰在边界时需先决定采用闭区间还是半开区间，不默认取部分 bin 计数。</p>')
p.save()

p=Page(PAGES[19],current=True)
p.patch_code(5,'hB->FillRandom("fB",50000);\nhS->FillRandom("fS",2000);\nhB->FillRandom("fB",50000);','gRandom->SetSeed(1901);\nhB->FillRandom("fB",100000);\nhS->FillRandom("fS",2000);')
p.patch_code(7,'hB->Draw("same");','hB->Draw("same");\nfSB->Draw("same"); // 联合拟合的总函数\nfB->SetLineStyle(2);\nfB->Draw("same");')
code=p.code(9)
for name in ['nhSB','nhB','nhS','nfB','nfS','nfSB']:code=code.replace('int '+name+'=','double '+name+'=')
p.code(9,code)
p.append(2,'<p>先画出设定的 signal、本底及总函数。随后 FillRandom 分别按函数形状抽样指定数量的事件；抽样数量由 FillRandom 的第二个参数决定，不等于初始函数的积分。</p>')
p.append(8,'<p>下面比较模拟中已知的 signal 计数、拟合 signal 的积分，以及总计数减去拟合本底。后两者是同一数据上的估计，并非独立测量。积分保留 double，避免把拟合值截断为整数。峰面积的误差传播见共用的 <a href="https://zhihuanli.github.io/Experimental-Method-in-Nuclear-Physics/tutorial/ROOT/ROOT_Tutorial_I_CPP.html">ROOT Tutorial I</a>。</p>')
p.save()
