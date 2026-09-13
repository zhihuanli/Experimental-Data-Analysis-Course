#include <TFile.h>
#include <TTree.h>
#include <cmath>
#include <iostream>
void Analyze(double WL, double WR, double timeOffset) {
    TFile input("tree_hw_demo.root");
    TTree *tin = input.Get<TTree>("tree");
    double AL, AR, tL, tR;
    tin->SetBranchAddress("AL", &AL);
    tin->SetBranchAddress("AR", &AR);
    tin->SetBranchAddress("tL", &tL);
    tin->SetBranchAddress("tR", &tR);

    TFile output("calibrated.root", "RECREATE");
    TTree *tout = tin->CloneTree(0); // 保留原有分支，只复制结构
    double xt, xq, tof_cal;
    Long64_t entry;
    tout->Branch("source_entry", &entry, "source_entry/L");
    tout->Branch("xt", &xt, "xt/D");
    tout->Branch("xq", &xq, "xq/D");
    tout->Branch("tof_cal", &tof_cal, "tof_cal/D");
    for (entry=0; entry<tin->GetEntries(); ++entry) {
        tin->GetEntry(entry);
        if (AL<=0 || AR<=0) continue;
        double tl = tL-WL/std::sqrt(AL);
        double tr = tR-WR/std::sqrt(AR);
        xt = 0.075/2 * (tl-tr-(5.5-20.4)); // m
        xq = 3.8/2 * std::log(AR*10/(AL*15)); // m
        tof_cal = (tl+tr)/2 + timeOffset; // ns
        tout->Fill();
    }
    std::cout << "Input=" << tin->GetEntries() << ", output=" << tout->GetEntries() << '\n';
    tout->Write();
}
