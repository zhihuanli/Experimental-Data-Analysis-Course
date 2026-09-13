"""Targeted repairs to the accepted decay lessons; preserve their sequence."""
from pathlib import Path
import re
import nbformat
from lecture_editor import Page, ROOT, PAGES

def finish(page):
    page.refresh()
    page.save()
    path=(ROOT/page.path).with_suffix('.ipynb')
    n=nbformat.read(path,as_version=4)
    result=[]
    for c in n.cells:
        if c.cell_type=='code':
            c.source=c.source.replace('//%jsroot on','').strip()
            if not c.source: continue
            # A type declaration belongs outside the kernel's execution block.
            m=re.match(r'(?:[^\n]*\n)*?(struct\s+\w+\s*\{[^}]+\};)',c.source)
            if m:
                result.append(nbformat.v4.new_code_cell('%%cpp -d\n'+m[1]))
                c.source=c.source[m.end():].strip()
                if not c.source: continue
        result.append(c)
    n.cells=result
    if not any(c.cell_type=='code' and '%jsroot on' in c.source for c in n.cells):
        n.cells.insert(1,nbformat.v4.new_code_cell('%jsroot on'))
    nbformat.write(n,path)

p=Page(PAGES[25],current=True)
p.replace('衰变实验的数据分析 I - 基于 timestamp 的事件重构','6.1 衰变实验：基于 timestamp 的事件重构')
p.append(0,'<p>文件中的能量已刻度为 keV，timestamp 已换算为 ns。本节不再对这些量重复做 ADC 道值的 dithering；整数原始道值的连续化在上游刻度时完成。</p>')
p.code(1,p.code(1)+'\nTH1::AddDirectory(kFALSE); // 关闭文件后仍保留本节创建的检查谱\ntree->Print();')
for i in [13,17,36,40]:
    code=p.code(i)
    code=re.sub(r'(\w+)->first - twindow',r'(\1->first > twindow ? \1->first - twindow : 0)',code)
    p.code(i,code)
p.append(12,'<p>窗口下边界先限制到 0，避免 unsigned timestamp 减去较大窗口后下溢。时间差则分别转为 <code>Long64_t</code> 后相减。</p>')

# Consume the whole 200-ns group, even when its multiplicity exceeds two.
for i,count,it,prefix in [(21,'xhit','ifts','x'),(25,'yhit','ibts','y'),(27,'xhit','ifts','x')]:
    code=p.code(i)
    end='mapb' if i in [21,25] else 'mapf'
    code=code.replace(f'while({it} != {end}.end() && {count} < 2)',f'while({it} != {end}.end())')
    a=f'        {prefix}timestamp[{count}] = {it}->first;'
    b=f'        {prefix}energy[{count}] = {it}->second.energy;'
    start=code.index(a); stop=code.index(b)+len(b)
    block=code[start:stop]
    code=code[:start]+f'        if ({count} < 2) {{ // 只存前两条，但遍历完整时间窗\n'+block+'\n        }'+code[stop:]
    if i in [25,27]:
        counter='mby' if i==25 else 'mfx'
        code=code.replace(f'abs({prefix}strip[0]-{prefix}strip[1]) > 1',f'abs({prefix}strip[0]-{prefix}strip[1]) != 1')
        at=code.rfind('\n}')
        code=code[:at]+f'\n    if ({count}>2) {counter}[3]++; // 三重及更高 multiplicity 不拆成双重\n'+code[at:]
        code=re.sub(r'\n'+counter+r'\s*$',f'\ncout << "single / adjacent double / other double / >=3 groups: "\n     << {counter}[0] << " / " << {counter}[1] << " / "\n     << {counter}[2] << " / " << {counter}[3] << endl;',code)
    p.code(i,code)
p.replace('若两重事件的 strip 不相邻，则不合并。','若两重事件的 strip 不相邻（或重复同一条），本节不将其作为单粒子候选写入下一阶段，数量单独统计。',indices=[22])
p.append(22,'<p>内层循环遍历完整的 200 ns 时间窗，再按总 hit 数分类。不能读到两个 hit 就结束，否则一个三重组会被错误地拆成“双重 + 单重”。</p>')

code=p.code(29)
code=code.replace('"front-back position;y strip;x strip"','"front-back position;front strip;back strip"')
code=code.replace('multimap<ULong64_t, dssdxy> mapdssd;','multimap<ULong64_t, dssdxy> mapdssd;\nLong64_t ambiguousPairs = 0;')
needle='            hxyfbc->Fill(ifts->second.energy, ibts1->second.energy);'
code=code.replace(needle,'''            // 两个方向都只有一个能量相容的候选，才写入一个 DSSD 事件。
            int nback = 0, nfront = 0;
            for (auto ib=mapbn.lower_bound(tmin); ib!=ibts2; ++ib)
                if (abs(ifts->second.energy-ib->second.energy)<500) ++nback;
            ULong64_t lo = ibts1->first>twindow ? ibts1->first-twindow : 0;
            auto fend = mapfn.upper_bound(ibts1->first+twindow);
            for (auto jf=mapfn.lower_bound(lo); jf!=fend; ++jf)
                if (abs(jf->second.energy-ibts1->second.energy)<500) ++nfront;
            if (nback!=1 || nfront!=1) { ++ambiguousPairs; continue; }
'''+needle)
code=code.replace('hxystrip->Fill(xy.ystrip, xy.xstrip);','hxystrip->Fill(xy.xstrip, xy.ystrip);')
code+='\ncout << "Unique DSSD events = " << mapdssd.size()\n     << ", ambiguous candidate pairs = " << ambiguousPairs << endl;'
# Separate the type declaration from the executable cell.
struct=re.search(r'struct dssdxy\s*\{.*?\};',code,re.S)[0]
p.insert_before(29,[('code','%%cpp -d\n'+struct)])
p.code(29,code.replace(struct,''))
p.append(28,'<p>先画时间窗内全部候选的能量关联，再应用 <code>|Efront−Eback|&lt;500 keV</code>。写入事件时，还要求该 front 和 back 在双方的候选列表中唯一对应，避免同一个 hit 被重复用于多个 DSSD 事件。歧义候选单独计数；高计数率数据需进一步用第 3 章的多粒子重建方法处理。</p>')
p.code(32,'''c1->Clear();
TH1F *hfe = new TH1F("hfe","Reconstructed DSSD;Energy (keV);Counts / 10 keV",3000,0,30000);
for (const auto &hit : mapdssd) hfe->Fill(hit.second.energy);
hfe->Draw("hist");
c1->SetLogy(0);
c1->Draw();''')
p.replace('选取峰中心附近约 $\\pm 100$ ns 作为 MWPC-DSSD 符合窗口。','下面以峰中心附近 $\\pm 200$ ns 作为 MWPC-DSSD 符合窗口。',indices=[37])
code=p.code(40).replace('3500,0,30500','3000,0,30000')
a=code.index('    for( ; imts1 != imts2; imts1++)');b=code.index('    if(me < 0)',a)
code=code[:a]+'''    Long64_t nearest = twindow+1;
    for( ; imts1 != imts2; imts1++) {
        Long64_t dt = llabs(Long64_t(imts1->first)-Long64_t(tt));
        if (dt<nearest) { nearest=dt; me=imts1->second; }
    }
    if (me>0) { hmwec->Fill(me); hdsec->Fill(de); }

'''+code[b:]
code+='\ncout << "DSSD total / with MWPC / without MWPC = "\n     << hfe->GetEntries() << " / " << hdsec->GetEntries()\n     << " / " << hdsenc->GetEntries() << endl;'
p.code(40,code)
p.append(39,'<p>若窗口内有多个 MWPC hit，<code>me</code> 取时间差最小的一路；一个 DSSD 事件只填一次符合能谱。这里的分类依据是有没有 prompt MWPC 信号，不把最邻近关系当作唯一的物理身份判定。</p>')
p.md(43,'<p>与 DSSD 符合后，MWPC 谱中的部分高道值计数受到明显抑制。可进一步结合模块 overflow 状态判断其来源；仅凭符合谱中的缺失不能确定它们都是无效信号。</p><h3>与 MWPC 符合的 DSSD 能谱</h3>')
finish(p)

p=Page(PAGES[26],current=True)
p.replace('衰变实验的数据分析 II - 重离子和衰变事件的关联','6.2 衰变实验：注入—衰变的位置和时间关联')
p.code(1,p.code(1)+'\nTH1::SetDefaultSumw2();')
p.patch_code(7,'xstrip:ystrip>>hxypos(128,0,128,48,0,48)','ystrip:xstrip>>hxypos(128,-0.5,127.5,48,-0.5,47.5)')
p.append(10,'<p>下面实现的是 <strong>all-pairs correlation</strong>：每个注入与窗口内全部候选关联，不只选择最近一次注入。同一个衰变候选可能进入多个注入的列表。稳定束流和探测条件下，其随机关联部分可近似为平台；若改成“最近一次注入”或“第一个衰变”，选择本身就会改变时间分布，不能照搬同一平台模型。</p>')
p.patch_code(13,'if(bhit >= MAX_DEC_HIT) break;','if(bhit >= MAX_DEC_HIT) throw runtime_error("Increase MAX_DEC_HIT; candidate list exceeds capacity");')
p.patch_code(13,'if(bhit > 0) tout->Fill();','tout->Fill(); // 保留零候选的注入，避免改变注入计数分母')
p.append(12,'<p>实际保存区间是相对注入时间的 −10 s 至 +20 s。run 起止附近的注入可观测时间较短；当运行时间与窗口长度可比时，应统计各时间 bin 的有效注入暴露量，或选择前后记录完整的注入。缺失的记录时间不能当成零衰变计数。</p>')
p.replace('衰变时间必须','衰变时间必须') if False else None
p.replace('减去 20 个半衰期以后的平台本底','用远正时间区估计平台本底',indices=[24])
p.md(26,r'''<h3>指数 + 平台拟合</h3>
<p>先用远时间区估计平台 $B$，再固定该估计值拟合衰变部分。参数依次为本底高度、指数项初始高度和半衰期（ms）。本图 bin 宽为 100 ms，拟合从 100 ms 开始，跳过零点附近的整个首 bin；这不意味着仪器死时间为 100 ms。</p>
<p><code>L</code> 用于未扣本底的计数谱；<code>I</code> 用 bin 内函数平均值比较计数，<code>R</code> 使用给定范围，<code>S</code> 返回拟合结果。固定 $B$ 后得到的半衰期误差只包含条件拟合误差。下面把 $B$ 改为 $B\pm\sigma_B$ 分别重拟合，用半衰期变化估计本底统计误差的贡献：</p>
<p>$$\sigma_T^2\simeq\sigma_{T\mid B}^2+\left[\frac{T(B+\sigma_B)-T(B-\sigma_B)}2\right]^2.$$</p>
<p>这里本底区与衰变拟合区不重叠，采用一阶误差传播。更一般的做法是联合拟合信号区和本底区，让 $B$ 的不确定度及相关性一同进入拟合。</p>''')
for idx,num,hist,bg,value in [(27,1,'hdtAc211a','fp01','p01'),(36,2,'hdtAc211d','fp01d','p01d')]:
    p.code(idx,f'''TF1 *fdecay{num} = new TF1("fdecay{num}",
    "[0]+[1]*exp(-x*log(2.)/[2])",100,10000);
fdecay{num}->SetParNames("Background","Amplitude","Half-life (ms)");
fdecay{num}->FixParameter(0,{value});
fdecay{num}->SetParameter(1,600);
fdecay{num}->SetParameter(2,250); // 接近已知半衰期的初值，不是固定值
fdecay{num}->SetParLimits(1,0,1e6);
fdecay{num}->SetParLimits(2,1,20000);
TFitResultPtr result{num} = {hist}->Fit(fdecay{num},"SLIR");
if (int(result{num})!=0) throw runtime_error("Decay fit failed");
double half{num}=fdecay{num}->GetParameter(2), errFit{num}=fdecay{num}->GetParError(2);
double varied{num}[2];
for (int k=0;k<2;++k) {{
    TF1 trial(*fdecay{num});
    trial.FixParameter(0,{value}+(2*k-1)*{bg}->GetParError(0));
    if (int({hist}->Fit(&trial,"QLIRN"))!=0) throw runtime_error("Background variation fit failed");
    varied{num}[k]=trial.GetParameter(2);
}}
double errB{num}=abs(varied{num}[1]-varied{num}[0])/2;
cout << "Half-life = " << half{num} << " ms; conditional fit error = " << errFit{num}
     << ", background contribution = " << errB{num}
     << ", combined = " << hypot(errFit{num},errB{num}) << " ms" << endl;
{hist}->Draw("hist");
fdecay{num}->Draw("same");
c1->SetLogy();
c1->Draw();''')
p.append(35,'<p>仍按上面的固定平台方法，并传播负时间区平台估计的统计误差。两次半衰期拟合使用同一批正时间事例，结果相关，不能把两者当作独立测量再取加权平均。</p>')
p.append(28,'<p>对计数谱作本底扣除后，净 bin 可以为负。若两窗计数独立且缩放系数为 $a$，则 $\\mathrm{Var}(N_{net})=N_{signal}+a^2N_{background}$；不能再对净谱直接使用 Poisson likelihood。这里保存原始计数谱并用 <code>Sumw2</code> 传播求差误差。</p>')
p.replace('每一级 $\\alpha$ 的几何探测效率约为 $50\\%$，两级 $\\alpha$ 衰变同时被探测到的效率约为 $25\\%$。','在浅注入、各向同性发射且只计算向硅内部发射的全能事件这一简化图像下，每一级的几何接受度约为 $50\\%$，两级约为 $25\\%$。实际全能效率还取决于注入深度、阈值、能量窗、分支比和时间窗。',indices=[39])
p.replace('当前示范中时间范围仍偏短，因此只能用于观察关联，不能可靠拟合 $^{207}\\mathrm{Fr}$ 半衰期。','本例先展示两级关联。若用它提取半衰期，还需在拟合中计入有限时间窗和候选选择的影响。',indices=[39])
p.md(45,'<p>本例第二级候选统计较少，而且只选择时间顺序中的前两个候选，其时间分布受到候选选择和有限窗口影响。这里用于展示两级衰变关联；定量提取半衰期时，应建立与该选择一致的模型，而不是仅因窗口较短就认定原则上无法拟合。</p>')
p.md(46,'<h3 id="assignment">作业</h3><p>选择 $^{210}$Ra 的 α 能量区域，比较同一 pixel 与相邻 pixel 的关联时间谱，确定位置条件并提取半衰期。分别用远正时间区和负时间区估计本底，比较结果并给出半衰期及其误差。</p>')
finish(p)

p=Page(PAGES[27],current=True)
p.replace('Least Square 和 Likelihood fitting','低计数时间谱：Least-squares 与 Poisson likelihood')
p.md(11,'<p>使用 <code>L</code> 后，10 个 bin 都参与 Poisson likelihood，得到 $p_0=6/10=0.6$。零计数也是信息：若预期为 $\\mu$，观测到零的概率为 $e^{-\\mu}$。</p><p>对本章未扣本底、未加权的计数时间谱，使用 Poisson likelihood，尤其不要忽略低计数和空 bin。并非所有含空 bin 的图都可使用 <code>L</code>：本底相减后的净谱不服从 Poisson 分布。</p><p>参考：<a href="https://root.cern.ch/doc/master/classTH1.html">ROOT TH1::Fit</a>。</p>')
p.code(12,'cout << "Total counts = " << f->Integral() << ", bins = " << f->GetNbinsX() << endl;')
finish(p)
