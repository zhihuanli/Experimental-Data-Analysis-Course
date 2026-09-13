"""Small plot readability corrections after inspecting ROOT output."""
from lecture_editor import Page
p=Page('chapt1/Integration_in_TH1_and_TF1.html',current=True)
p.patch_code(13,'hSB->Draw("hist");','hSB->SetMinimum(0); // 让单独的 signal 分量也能显示\nhSB->Draw("hist");')
p.save()
p=Page('chapt3/3.5_DSSD_FB_correlation_II_DSSD1-new.html',current=True)
c=p.code(33).replace('"cye:cxe;cxe;cye"','"Normalized front-back;X relative amplitude;Y relative amplitude"')
c=c.replace('"cye-cxe;cxe;cye-cxe"','"Normalized residual;X relative amplitude;Y-X relative amplitude"')
c=c.replace('"Global check", 800, 400','"Global check", 1000, 430')
c=c.replace('c_check->cd(1); hxy->Draw("colz");','c_check->cd(1); gPad->SetLeftMargin(0.14); gPad->SetRightMargin(0.16); hxy->SetStats(0); hxy->Draw("colz");')
c=c.replace('c_check->cd(2); hdiff->Draw("colz");','c_check->cd(2); gPad->SetLeftMargin(0.14); gPad->SetRightMargin(0.16); hdiff->SetStats(0); hdiff->Draw("colz");')
p.code(33,c);p.save()
