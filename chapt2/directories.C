{
gRandom->SetSeed(2501); // 固定示例的随机数种子
// 1. 创建用于存储直方图的 ROOT 文件
TFile *fout = new TFile("hist_test.root", "RECREATE");

// 2. 在根目录下创建一级目录 dir1 和 dir2
TDirectoryFile *dir1 = new TDirectoryFile("dir1", "ADC Spectra");
TDirectoryFile *dir2 = new TDirectoryFile("dir2", "TDC Spectra");

// 3. 在 dir1 下创建子目录 dir1sub
dir1->cd();
TDirectoryFile *dir1sub = new TDirectoryFile("dir1sub", "PPAC Detail");

// 4. 声明并初始化直方图 (注意在 new 之前切换到对应的目录)
TH1I *h0, *h1, *h2, *h1sub;

fout->cd();    // 回到根目录
h0 = new TH1I("h0", "Global Hist", 100, -3, 3);

dir1->cd();    // 进入 dir1
h1 = new TH1I("h1", "ADC Channel 1", 100, -3, 3);

dir1sub->cd(); // 进入子目录
h1sub = new TH1I("h1sub", "PPAC X pos", 100, -3, 3);

dir2->cd();    // 进入 dir2
h2 = new TH1I("h2", "TDC Channel 1", 100, -3, 3);

// 5. 填充数据 (实际分析中通常在 Event Loop 中进行)
h0->FillRandom("gaus", 10000);
h1->FillRandom("gaus", 10000);
h1sub->FillRandom("gaus", 10000);
h2->FillRandom("gaus", 10000);

// 6. 一次性将所有内存中的直方图按目录结构写入文件
fout->Write();
fout->Close();

}
