"""Resolve cross-span prose/code inconsistencies after execution, preserving outputs."""
from lecture_editor import ROOT, PAGES, Page, pre, fragment
import re

p=Page(PAGES[0],current=True)
p.replace('对于 0-50 MeV 范围内的反冲质子，其电子等效能量','在该经验模型中，电子等效能量')
p.replace('入射深度 (z_true)','入射深度 (depth_true) 与实际路径 (path_true)')
p.replace('tree->Write();  // 将缓冲区内的所有事件批量压缩并写入磁盘','tree->Write();  // 写入尚未落盘的内容及树的元数据')
for a in p.soup.find_all('a',href=True):
    if '0029554X79904173' in a['href']:
        a['href']='https://scholarworks.iu.edu/dspace/items/a4d7e87e-a7c7-4375-870a-f06df5f8b6e1'
for tag in p.container(0).find_all(['p','li']):
    txt=tag.get_text()
    if txt.strip()=='入射深度 (z_true)':tag.string='入射深度 (depth_true) 与实际路径 (path_true)'
    if txt.startswith('对于 0-50 MeV'):
        tag.replace_with(fragment('<p>这里用下列经验响应描述质子光输出与能量的非线性关系：</p>'))
p.save()

p=Page(PAGES[2],current=True)
p.replace('浮点精度的浮点数 (double)','用 double 保存的浮点数')
p.replace('精度是 12-bit','数字编码为 12-bit')
p.paragraph(0,'例如量程 0-4V','<p>理想 0–4 V 量程对应 4096 个码，Gain=4096/4000=1.024 ch/mV。未加 pedestal 时，2.5 V 对应 2560 ch。</p>')
for tag in list(p.container(0).select('p,li')):
    text=tag.get_text()
    if text.startswith('在硬件上给输入端'):
        tag.replace_with(fragment('<p>可加入直流偏置把 pedestal 均值移到正道值，如 140 ch，以减少负向噪声被量程截断；这不保证任意噪声样本都在量程内。</p>'))
    elif text.startswith('Pedestal 并不是'):
        tag.replace_with(fragment('<p>无物理信号时，读数仍有分布。其均值用来扣除 pedestal offset，宽度反映噪声；是否近似 Gaussian 应从数据检查。扣除均值不等于消除了逐事例噪声。</p>'))
    elif text.startswith('Overflow (上溢)'):
        tag.replace_with(fragment('<li>本模拟把超量程值记为最大码。真实模块可能另有 overflow 状态或编码，应按模块说明处理。</li>'))
    elif text.startswith('束流/时钟触发'):
        tag.replace_with(fragment('<li>束流/时钟触发用于监测基线。本模拟把 pid=3 设为无物理信号事件；真实的时钟触发仍可能与粒子信号偶然重叠。</li>'))
p.replace('Int_t pid;       // 0:G, 1:N, 2:LP, 3:Pedestal','// 复用已有 pid：0:G, 1:N, 2:LP, 3:Pedestal')
p.replace('opt->Branch("pid", &pid, "pid/I");','// pid 分支已在原模拟中建立，不再重复声明。')
p.replace('LP 假设能量全沉积','此处直接指定 LP 的示意光输出分布（MeVee）')
p.replace('tree->Fill(); // 只有满足触发条件才存入 Tree','opt->Fill(); // 只有满足触发条件才存入 Tree')
p.save()

p=Page(PAGES[5],current=True)
for tag in list(p.container(1).select('p,li')):
    text=tag.get_text()
    if ('权重' in text and ('绝对不能' in text or '不能直接' in text or '真实误差' in text)):
        tag.replace_with(fragment('<p>对同一参数的独立测量，可按 inverse variance 组合。束斑位置等逐事例变化的物理量还含真实分布宽度，应区别处理。</p>'))
p.save()

p=Page(PAGES[6],current=True)
for tag in list(p.container(0).select('p,li')):
    if tag.get_text().startswith('编译与链接的严格分离'):
        tag.replace_with(fragment('<li>本例将编译选项放在 CPPFLAGS/CXXFLAGS，将链接库放在 LDLIBS。库通常放在源文件或目标文件之后，避免静态库符号解析的顺序问题；变量名本身没有特殊语法含义。</li>'))
p.replace('安全关闭：处理完后务必 Close() 文件，确保数据从内存完全写入磁盘。。','处理完成后写入输出文件，再关闭文件。')
p.save()

p=Page(PAGES[7],current=True)
# Remove the illustrative constructor for an obsolete signature; retain the
# initializer-list explanation with the actual parameters of this project.
p.replace('tracking(tree_in), run(run_number), fOutTree(tree_out)','tracking(input), fOutTree(output)')
p.replace('run(run_number) 与 fOutTree(tree_out)','fOutTree(output)')
p.replace('run 和 fOutTree','fOutTree')
for tag in list(p.container(0).find_all('pre')):
    if 'ana(int run_number' in tag.get_text():
        tag.replace_with(fragment(pre('ana(TTree* input, TTree* output) : tracking(input), fOutTree(output) {}')))
p.save()

p=Page(PAGES[8],current=True)
for tag in list(p.container(6).select('p')):
    if '实时查看每个参数的分布极其耗时' in tag.get_text():
        tag.replace_with(fragment('<p>反复查看大型 TTree 的同一分布会重复读取数据。可把常用直方图与树一起保存，或另存为 hist001.root，供日常检查；按具体数据量决定是否缓存。</p>'))
    elif '秒级' in tag.get_text():
        tag.replace_with(fragment('<p>保存可复用的中间量，可以减少后续改变选择条件时的重复计算。</p>'))
p.save()

p=Page(PAGES[9],current=True)
for i in [5,9]:
    for code in p.container(i).find_all('pre'):
        txt=code.get_text().replace('```cpp','').replace('```','')
        code.replace_with(fragment(pre(txt)))
p.replace('vector<Double_t> 用来保存某一条 Pie 谱上全部候选峰的位置','vector<Double_t> 用来保存某一条 Pie 谱上找到的候选峰位置')
p.save()

p=Page(PAGES[17],current=True)
changes={
 'vector::assign(v1.begin(), v2.end());':'vector::assign(v1.begin(), v1.end());',
 'bool SortDS(dssd &a, dssd &b)':'bool SortDS(const dssd &a, const dssd &b)',
 'return Long64_t(a.e - b.e) == 0 && a.id == b.id;':'return a.id == b.id && a.e == b.e && a.t == b.t;',
 'int dt = Long64_t(it->t - b[0].t);':'double dt = it->t - referenceTime;',
 'if (b.size() > 0) {':'if (b.size() > 0) {\n    const double referenceTime = b[0].t; // 删除元素前保存参考时间',
 'Double_t d1t[32], d2t[32], d3t[32]; // xt':'// 本节参考文件没有时间分支。',
 'int hit = min(x->size(), y->size());':'size_t hit = std::min(x->size(), y->size());',
 'for (int i = 0; i < hit; i++)':'for (size_t i = 0; i < hit; i++)',
}
for a,b in changes.items():p.replace(a,b)
for block in p.container(0).find_all('pre'):
    if 'CPPFLAGS' in block.get_text():
        block.replace_with(fragment(pre((ROOT/'chapt3/code/code1/makefile').read_text())))
p.save()
