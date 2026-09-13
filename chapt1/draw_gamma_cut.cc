void draw_gamma_cut() {
    TCutG *cut_gamma = new TCutG("cut_gamma", 9);
    cut_gamma->SetVarX("tL+tR");
    cut_gamma->SetVarY("sqrt(qL*qR)");

    cut_gamma->SetPoint(0, 140, 2);
    cut_gamma->SetPoint(1, 110, 25);
    cut_gamma->SetPoint(2, 100, 100);
    cut_gamma->SetPoint(3, 98, 500);
    cut_gamma->SetPoint(4, 85, 500);
    cut_gamma->SetPoint(5, 88, 100);
    cut_gamma->SetPoint(6, 95, 25);
    cut_gamma->SetPoint(7, 115, 2);
    cut_gamma->SetPoint(8, 140, 2);

    cut_gamma->SetLineColor(kRed);
    cut_gamma->SetLineWidth(1);
    cut_gamma->SetLineStyle(1);

    // 将对象添加到 ROOT 的特殊列表，确保全局可见
    gROOT->GetListOfSpecials()->Add(cut_gamma);

    // 注意：在分析代码中调用时，我们通常不需要它自动 Draw()
    // cut_gamma->Draw("L");
}
