"""Resolve prose split across HTML tags and retain link anchors."""
from lecture_editor import Page,fragment
p=Page('chapt3/3.2_TTree_Branch_with_Dynamic_Array.html',current=True)
if any(t.get_text().strip().startswith('上面的') for t in p.container(0).find_all('p')):
    p.paragraph(0,'上面的', '<p>上述数组容量 384 对应三个 128 条探测器；事件中的有效长度由 xhit、yhit 给出，写进 ROOT leaflist。下文改用当前 S4 数据的容量 48，以及 phit/rhit 演示。</p>')
p.save()
p=Page('chapt3/3.5_DSSD_FB_correlation_II_DSSD1_multi-path.html',current=True)
if any(t.get_text().strip().startswith('To combine them consistently') for t in p.container(0).find_all('p')):
    p.paragraph(0,'To combine them consistently','<p>若各路径候选确实独立，可以采用 inverse-variance 标量组合。路径复用了事例或共享有误差的参考时，应纳入路径间的 covariance；“来自不同路径”本身不等于独立。</p>')
p.replace('until the strip parameters become stable.','这里只描述如何产生候选，不应反复使用同一批数据来缩小误差。')
p.save()
p=Page('chapt2/2.1_PPAC_analysis.html',current=True)
p.paragraph(17,'实验中的 time-sum','<p>参考：H. Kumagai et al., <a href="https://arxiv.org/abs/1311.0215">Development of Parallel Plate Avalanche Counter PPAC for BigRIPS fragment separator</a>, arXiv:1311.0215 (2013)。文中讨论了 delay-line time-sum 与 δ-ray 效应。</p>')
p.save()
