"""Small consistency fixes on the executed pages; keep their results."""
from lecture_editor import ROOT, PAGES, Page, pre, fragment

p=Page(PAGES[6],current=True)
p.paragraph(0,'安全关闭：','<li>完成事件循环后调用 <code>output.Write()</code>。离开作用域时文件对象自动关闭。</li>')
p.paragraph(0,'编译与链接指令：','<li>编译与链接指令：<code>$(CXX) $(CPPFLAGS) $(CXXFLAGS) $(SOURCES) $(LDLIBS) -o $@</code>。这里把编译和链接合并为一步，<code>$@</code> 是目标文件名 tracking。</li>')
p.paragraph(0,'wildcard 文件自动扫描：','<p><code>$(wildcard src/*.cpp src/*.C)</code> 列出源文件；<code>$(wildcard include/*.h)</code> 列出头文件，作为重新构建的依赖。</p>')
p.paragraph(0,'DIR_INC 路径包含规则：','<p><code>-Iinclude</code> 指定头文件搜索目录，因此源文件中可以写 <code>#include "tracking.h"</code>。</p>')
p.replace('源文件 (.C / .cpp)：”','源文件 (.C / .cpp)：')
p.save()

p=Page(PAGES[8],current=True)
p.paragraph(1,'避免重复计算，','<li>避免重复计算：改变末端的 Cut 或拟合区间时，读取已保存的刻度结果，不必重复解码和刻度。</li>')
p.paragraph(14,'在此阶段，每个处理步骤','<p>本阶段用刻度后的信号重建物理量。选择条件会改变样本及其接受度，应与重建结果一起记录，供后续效率修正使用。</p>')
p.paragraph(14,'符合时间窗口选取','<li>符合时间窗口选取（Time Window Cut）：围绕探测器时间差的 prompt 峰选择事件，以降低 random coincidence。本底仍可能落在窗口内，必要时用旁侧时间区间估计。</li>')
p.paragraph(14,'该阶段的一个显著特征','<p>重建后可只保留后续分析需要的量以减少重复读取，同时保留能追溯到原事件的编号。</p>')
# Promote the existing directory example to an executable cell, at the same
# place in the lecture. The following diagrams and readback cells stay in order.
md=p.container(7)
if md is not None:
    source=md.find('pre').get_text()
    source='gRandom->SetSeed(2501); // 固定示例的随机数种子\n'+source
    images=''.join(str(img) for img in md.find_all('img'))
    cell=p.cells[7]
    cell.clear();cell['class']=['jp-Cell','jp-CodeCell']
    cell.append(fragment('<div class="jp-Cell-inputWrapper"><div class="jp-InputArea"><div class="jp-InputArea-editor"></div></div></div>'))
    p.code(7,source)
    p.container(8).insert(0,fragment('<p>写入后的目录结构：</p>'+images))
    (ROOT/'chapt2/directories.C').write_text('{\n'+source+'\n}\n')
p.save()
