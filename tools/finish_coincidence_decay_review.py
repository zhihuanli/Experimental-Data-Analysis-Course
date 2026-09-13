"""Small final corrections after inspecting the native executions."""
import sys
import nbformat
from bs4 import BeautifulSoup
from lecture_editor import ROOT, PAGES, Page

numbers=[int(x) for x in sys.argv[1:]] or [20,24,25,26]
for number in numbers:
    path=(ROOT/PAGES[number]).with_suffix('.ipynb')
    n=nbformat.read(path,4)
    if number==24 and not any('jsroot_large_output import' in c.source for c in n.cells):
        n.cells.insert(1,nbformat.v4.new_code_cell('%python from jsroot_large_output import enable; enable()'))
        n.cells[0].source+='<p>运行环境：同目录的 <a href="jsroot_large_output.py">JSROOT 输出兼容文件</a>用于处理 ROOT 6.40 大矩阵的无损压缩；下面的初始化只影响 notebook 显示传输，不改变 bin、误差或分析结果。图仍由 <code>%jsroot on</code> 自然输出。</p>'
    for c in n.cells:
        if number==21 and c.cell_type=='code' and 'void fit_all_clusters_pair' in c.source:
            c.source='%%cpp -d\n'+(ROOT/'chapt4/pair_timewalk_correction.C').read_text()
        if number in [20,21] and c.cell_type=='markdown' and '拟合区外属于外推' in c.source and 'C_s=' not in c.source:
            c.source+='<p>若某条晶体与参考晶体没有足够的直接符合统计，可通过有效中间通道传递：$C_s=t_{\\rm off,sj}+C_j$。代码先固定参考为零，再沿有效 pair 逐步求出其余 offset；多条路径可用于检查一致性。完全不连通的通道才保留未修正标记。</p>'
        if number==21 and c.cell_type=='markdown' and '输出保留' in c.source and 'C_s=' not in c.source:
            c.source+='<p>参考传递使用 $C_s=t_{\\rm off,sj}+C_j$；没有直接 pair 时通过已知通道连接，不因缺少单个 pair 就放弃该晶体的修正。可用其他有效 pair 检查闭合差。</p>'
        if number==20 and c.cell_type=='markdown':
            s=BeautifulSoup(c.source,'html.parser')
            for p in s.find_all('p'):
                if p.get_text().strip().startswith('经过这种处理后，最终文件中的'):
                    p.clear();p.append('这里的代码完成 cluster 内 time walk 和高能 offset 修正。跨 cluster 的常数 offset D_c 仍需单独检查，当前程序没有自动求解和扣除它；cluster 内的时间差谱不能代替跨 cluster 检查。')
            c.source=str(s)
        if number==20 and c.cell_type=='code' and 'tree->Scan("ghit:int(gid/7)' in c.source and 'TFile' not in c.source:
            c.source='''tree->Draw(">>highMult","ghit>10","entrylist");
TEntryList *highMult=(TEntryList*)gDirectory->Get("highMult");
cout << "Events with ghit>10 = " << highMult->GetN() << endl;
tree->SetScanField(0);
for (Long64_t i=0;i<std::min(Long64_t(3),highMult->GetN());++i)
    tree->Scan("ghit:int(gid/7):gid%7:ge:gt","","",1,highMult->GetEntry(i));'''
        if number==24 and c.cell_type=='markdown' and 'gate \\ peak' in c.source:
            pass
        if number==24 and c.cell_type=='code' and 'void zoom2D' in c.source:
            c.source='''%%cpp -d
void zoom2D(TH2D *h, double xmin, double xmax,
            double ymin, double ymax, const char *opt="colz")
{
    // 复制指定范围的完整 bin；不 rebin，不修改用于分析的原矩阵。
    auto x=h->GetXaxis(), y=h->GetYaxis();
    int x1=x->FindBin(xmin), x2=x->FindBin(std::nextafter(xmax,-INFINITY));
    int y1=y->FindBin(ymin), y2=y->FindBin(std::nextafter(ymax,-INFINITY));
    TH2D *view=new TH2D(Form("%s_zoom",h->GetName()),h->GetTitle(),
        x2-x1+1,x->GetBinLowEdge(x1),x->GetBinUpEdge(x2),
        y2-y1+1,y->GetBinLowEdge(y1),y->GetBinUpEdge(y2));
    view->SetDirectory(nullptr);
    view->GetXaxis()->SetTitle("Energy (keV)");
    view->GetYaxis()->SetTitle("Energy (keV)");
    for (int i=x1;i<=x2;++i) for (int j=y1;j<=y2;++j) {
        view->SetBinContent(i-x1+1,j-y1+1,h->GetBinContent(i,j));
        view->SetBinError(i-x1+1,j-y1+1,h->GetBinError(i,j));
    }
    view->SetStats(0);
    view->Draw(opt);
}'''
        if number==24 and c.cell_type=='markdown' and '<table' in c.source and '133' in c.source:
            if '79.6 和 81.0' not in c.source:
                c.source+='<p>表中的 80 keV gate 同时覆盖约 79.6 和 81.0 keV 两条跃迁；(80,80) 对应它们的级联，不是两条相同能量跃迁。160.6 keV 附近既可能有直接跃迁，也可能有 79.6+81.0 keV 的加和贡献，需要结合 addback 前后和级联关系辨别。能级关系可核对 <a href="https://gammaray.inl.gov/SiteAssets/catalogs/ge/pdf/ba133.pdf">INL 的 133Ba 数据及衰变纲图</a>。</p>'
        if number==25:
            c.source=c.source.replace('文件中的能量已刻度为 keV，timestamp 已换算为 ns。本节不再对这些量重复做 ADC 道值的 dithering；整数原始道值的连续化在上游刻度时完成。','alpha.root 中 DSSD 能量单位为 keV，mwpc.root 的幅度仍为 channel；两者 timestamp 的单位均为 ns。这里直接使用已刻度的 DSSD 能量，MWPC 幅度仅用于符合标记，不另作连续能量刻度。整数道值的 dithering 应在相应通道的连续刻度之前做一次，不在这些下游关联步骤中重复。')
            if c.cell_type=='code' and 'TH2I *hxystrip' in c.source:
                c.source=c.source.replace('128,0,128,48,0,48','48,-0.5,47.5,128,-0.5,127.5')
            if c.cell_type=='code' and 'TH1I *hnhit' in c.source:
                c.source=c.source.replace('5,0,5','6,-0.5,5.5').replace('hnhit->Draw("colz")','hnhit->Draw("hist")')
            if c.cell_type=='code' and 'hxystrip->Draw' in c.source and 'SetLogy(0)' not in c.source:
                c.source=c.source.replace('hxystrip->Draw','c1->SetLogx(0);\nc1->SetLogy(0);\nhxystrip->SetStats(0);\nhxystrip->Draw')
            if c.cell_type=='markdown' and '唯一对应' in c.source and 'xstrip 对应' not in c.source:
                c.source+='<p>本文件约定 <code>side=0</code> 为 front（48 条），<code>side=1</code> 为 back（128 条）；输出 <code>xstrip</code> 对应 front，<code>ystrip</code> 对应 back。位置图沿用这一顺序，每条占一个 bin。</p>'
        if number==26:
            c.source=c.source.replace('ystrip:xstrip>>hxypos(128,-0.5,127.5,48,-0.5,47.5)','ystrip:xstrip>>hxypos(48,-0.5,47.5,128,-0.5,127.5)')
            if c.cell_type=='markdown' and '这里本底区与衰变拟合区不重叠' in c.source:
                c.source=c.source.replace('这里本底区与衰变拟合区不重叠，采用一阶误差传播。','这里本底区与衰变拟合区不重叠，先忽略 all-pairs 共享事例带来的相关性，采用一阶误差传播。高注入率时需按完整注入—衰变记录评估这种相关性，不能只靠缩小拟合误差。')
            if c.cell_type=='code' and 'TF1 *fdecay' in c.source:
                for h in ['hdtAc211a','hdtAc211d']:
                    if h+'->Draw("hist");' in c.source:
                        c.source=c.source.replace(h+'->Draw("hist");',h+'->SetTitle("^{211}Ac;Correlation time (ms);Counts / 100 ms");\n'+h+'->Draw("hist");')
    if number==20:
        duplicate=[i for i,c in enumerate(n.cells) if c.cell_type=='code' and 'TEntryList *highMult' in c.source]
        for i in duplicate[1:]:
            n.cells[i].source=Page(PAGES[20]).code(37)
    if number==25 and not any(c.cell_type=='code' and 'hxystrip->Draw' in c.source for c in n.cells):
        pos=next(i for i,c in enumerate(n.cells) if c.cell_type=='code' and 'hxyfbc->Draw' in c.source)+1
        n.cells.insert(pos,nbformat.v4.new_code_cell('''c1->Clear();
hxystrip->Draw("colz");
c1->Draw();
cout << "Position plot: entries / regular-bin sum = "
     << hxystrip->GetEntries() << " / " << hxystrip->Integral() << endl;'''))
    nbformat.write(n,path)
