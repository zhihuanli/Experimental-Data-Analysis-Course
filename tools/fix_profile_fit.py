"""Keep all plotted events; fit only means with an estimable sample variance."""
from lecture_editor import Page,PAGES
p=Page(PAGES[1],current=True)
for i,side in [(7,'L'),(9,'R')]:
    code=f'''TGraphErrors *means{side} = new TGraphErrors;
for (int b=1; b<=prof{side}->GetNbinsX(); ++b) {{
    // 单个事件不能估计该 bin 的时间方差，因此不作为拟合点。
    if (prof{side}->GetBinEntries(b)<2 || prof{side}->GetBinError(b)<=0) continue;
    int n = means{side}->GetN();
    means{side}->SetPoint(n, prof{side}->GetBinCenter(b), prof{side}->GetBinContent(b));
    means{side}->SetPointError(n, 0, prof{side}->GetBinError(b));
}}
means{side}->Fit(fFit, "RQ");
fFit->Draw("same");'''
    p.patch_code(i,f'prof{side}->Fit(fFit, "RQ");',code)
p.append(6,'<p>拟合使用 Profile 的均值和均值误差。只有一个事件的 bin 无法从样本估计方差，故不把它作为加权拟合点；它仍保留在原始二维图和 Profile 中。下面用 TGraphErrors 明确列出参与拟合的均值点。</p>')
p.save()
