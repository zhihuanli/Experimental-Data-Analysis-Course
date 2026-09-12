// Section 4.5: run from the directory containing the input ROOT files.
#include <iostream>
#include <fstream>
#include <vector>
#include <cmath>
#include <algorithm>
#include <stdexcept>
#include "TFile.h"
#include "TTree.h"
#include "TParameter.h"
#include "TGenPhaseSpace.h"
#include "TLorentzVector.h"
#include "TVector3.h"
#include "TMath.h"
#include "TRandom3.h"
#include "TCanvas.h"
#include "TH1D.h"
#include "TH2D.h"
#include "TH1F.h"
#include "TH2F.h"
#include "TLegend.h"
#include "TLine.h"
#include "TStyle.h"

#include <cmath>
#include <algorithm>
#include "TFile.h"
#include "TTree.h"
#include "TParameter.h"
#include "TMath.h"
#include "TVector3.h"
#include "TLorentzVector.h"
#include "TCanvas.h"
#include "TH1F.h"
#include "TH2F.h"
#include "TLegend.h"
#include "TLine.h"
#include "TStyle.h"

// 以下两个画布在后面的显示单元中继续使用。
TCanvas *c1 = nullptr;
TCanvas *c2 = nullptr;

struct Kine {
    double mH1, mC12, mHe4, mBe10, mC14, ekBeamMean;

    double mRecoil(int pid) const { return pid == 1 ? mH1 : mC12; }
    double Qgs(int pid) const { return mC14 - mHe4 - mBe10; }
    double P(double ek, double m) const { return std::sqrt(ek*ek + 2*m*ek); }

    double m(int pid, int i, double ex) const {
        double mass[] = {mHe4, mBe10, mRecoil(pid), mBe10 + ex};
        return mass[i];
    }

    TVector3 pv(int pid, int i, double ek[], double th[], double ph[], double ex) const {
        TVector3 v;
        v.SetMagThetaPhi(P(ek[i], m(pid,i,ex)), th[i]*TMath::DegToRad(), ph[i]*TMath::DegToRad());
        return v;
    }

    TLorentzVector lv(int pid, int i, double ek[], double th[], double ph[], double ex) const {
        return TLorentzVector(pv(pid,i,ek,th,ph,ex), ek[i] + m(pid,i,ex));
    }

    double Qevt(double ek[], double ekBeam) const { return ek[0]+ek[1]+ek[2] - ekBeam; }
    double Qmean(double ek[]) const { return ek[0]+ek[1]+ek[2] - ekBeamMean; }

    double Q3(int pid, double ek[], double th[], double ph[], double ex) const {
        TVector3 p = pv(pid,0,ek,th,ph,ex) + pv(pid,1,ek,th,ph,ex) + pv(pid,2,ek,th,ph,ex);
        return ek[0]+ek[1]+ek[2] - (std::sqrt(mC14*mC14 + p.Mag2()) - mC14);
    }

    double Q2(int pid, double ek[], double th[], double ph[], double ex) const {
        TVector3 pR = TVector3(0,0,P(ekBeamMean,mC14)) - pv(pid,0,ek,th,ph,ex) - pv(pid,1,ek,th,ph,ex);
        double mR = mRecoil(pid);
        return ek[0]+ek[1] + (std::sqrt(mR*mR + pR.Mag2()) - mR) - ekBeamMean;
    }

    double ExInv(int pid, double ek[], double th[], double ph[], double ex) const {
        return (lv(pid,0,ek,th,ph,ex) + lv(pid,1,ek,th,ph,ex)).M() - mC14;
    }
};

void DrawQAnalysis()
{
    TFile *f = TFile::Open("C14_CHn_He4Be10x.root");
    if (!f || f->IsZombie()) throw std::runtime_error("Run Section 4.4 first");
    TTree *t = f->Get<TTree>("tree");
    if (!t) throw std::runtime_error("Missing tree");

    Kine K;
    const double u = 1000.0; // 文件中质量为 GeV，转换为 MeV；动能分支已经是 MeV
    K.mH1        = ((TParameter<Double_t>*)f->Get("massH1"))->GetVal() * u;
    K.mC12       = ((TParameter<Double_t>*)f->Get("massC12"))->GetVal() * u;
    K.mHe4       = ((TParameter<Double_t>*)f->Get("massHe4"))->GetVal() * u;
    K.mBe10      = ((TParameter<Double_t>*)f->Get("massBe10"))->GetVal() * u;
    K.mC14       = ((TParameter<Double_t>*)f->Get("massC14"))->GetVal() * u;
    K.ekBeamMean = ((TParameter<Double_t>*)f->Get("ekBeamMean"))->GetVal();

    Int_t pid;
    Double_t ekBeam, exBe10, w;
    Double_t ek[4], th[4], ph[4];
    t->SetBranchAddress("processID",    &pid);
    t->SetBranchAddress("ekBeam",       &ekBeam);
    t->SetBranchAddress("exBe10",       &exBe10);
    t->SetBranchAddress("weight_total", &w);
    t->SetBranchAddress("ek",           ek);
    t->SetBranchAddress("theta",        th);
    t->SetBranchAddress("phi",          ph);

    // 直方图: [0]=H, [1]=C
    TH1F *hQ[4][2], *hEx[3][2];
    TH2F *hInvQ[2], *hInvQ2[2];
    const char *qn[] = {"Qevt","Qmean","Q3","Q2"};
    for (int i = 0; i < 4; ++i) {
        hQ[i][0] = new TH1F(Form("%s_H",qn[i]), Form("%s;Q [MeV];counts",qn[i]), 500,-35,5);
        hQ[i][1] = new TH1F(Form("%s_C",qn[i]), Form("%s;Q [MeV];counts",qn[i]), 500,-35,5);
    }
    const char *en[] = {"ExTrue","ExQ3","ExQ2"};
    for (int i = 0; i < 3; ++i) {
        hEx[i][0] = new TH1F(Form("%s_H",en[i]), "H: E_{x}(^{10}Be);E_{x} [MeV];counts", 300,-5,10);
        hEx[i][1] = new TH1F(Form("%s_C",en[i]), "C: E_{x}(^{10}Be);E_{x} [MeV];counts", 300,-5,10);
    }
    hInvQ[0]  = new TH2F("InvQ_H",  "H: inv.mass vs Q3;Q3 [MeV];E_{x}(^{14}C) [MeV]", 200,-20,5, 200,8,22);
    hInvQ[1]  = new TH2F("InvQ_C",  "C: inv.mass vs Q3;Q3 [MeV];E_{x}(^{14}C) [MeV]", 200,-20,5, 200,8,22);
    hInvQ2[0] = new TH2F("InvQ2_H", "H: inv.mass vs Q2;Q2 [MeV];E_{x}(^{14}C) [MeV]", 200,-20,5, 200,8,22);
    hInvQ2[1] = new TH2F("InvQ2_C", "C: inv.mass vs Q2;Q2 [MeV];E_{x}(^{14}C) [MeV]", 200,-20,5, 200,8,22);

    // 填充
    for (Long64_t i = 0; i < t->GetEntriesFast(); ++i) {
        t->GetEntry(i);
        int j = (pid == 1) ? 0 : 1;

        double q3 = K.Q3(pid, ek, th, ph, exBe10);
        double q2 = K.Q2(pid, ek, th, ph, exBe10);
        hQ[0][j]->Fill(K.Qevt(ek, ekBeam), w);
        hQ[1][j]->Fill(K.Qmean(ek), w);
        hQ[2][j]->Fill(q3, w);
        hQ[3][j]->Fill(q2, w);

        hEx[0][j]->Fill(exBe10, w);
        hEx[1][j]->Fill(K.Qgs(pid) - q3, w);
        hEx[2][j]->Fill(K.Qgs(pid) - q2, w);

        hInvQ[j]->Fill(q3, K.ExInv(pid, ek, th, ph, exBe10), w);
        hInvQ2[j]->Fill(q2, K.ExInv(pid, ek, th, ph, exBe10), w);
    }

    std::cout << "Qgs = " << K.Qgs(1) << " MeV; events = " << t->GetEntries() << std::endl;

    // 画图
    gStyle->SetOptStat(0);
    int colH = kBlue+1, colC = kRed+1;

    auto vline = [](double x, double y1, double y2, int col, int sty=2) {
        TLine *l = new TLine(x,y1,x,y2);
        l->SetLineColor(col); l->SetLineStyle(sty); l->Draw();
    };

    // ================ c1: Q 值谱对比 (2x2, logy) ================
    c1 = new TCanvas("c1","Q",900,900);
    c1->Divide(2,2);
    for (int i = 0; i < 4; ++i) {
        c1->cd(i+1); gPad->SetLogy();
        hQ[i][0]->SetLineColor(colH);
        hQ[i][1]->SetLineColor(colC);
        double ymax = 2*std::max(hQ[i][0]->GetMaximum(), hQ[i][1]->GetMaximum());
        hQ[i][0]->SetMinimum(0.5); hQ[i][0]->SetMaximum(ymax);
        hQ[i][0]->Draw("hist"); hQ[i][1]->Draw("hist same");
        vline(K.Qgs(1), 0.5, ymax, colH); vline(K.Qgs(1)-3.368, 0.5, ymax, colH, 3);
        vline(K.Qgs(2), 0.5, ymax, colC); vline(K.Qgs(2)-3.368, 0.5, ymax, colC, 3);
        if (i == 0) {
            TLegend *leg = new TLegend(0.15,0.75,0.45,0.88);
            leg->AddEntry(hQ[i][0], "H target", "l");
            leg->AddEntry(hQ[i][1], "C target", "l");
            leg->Draw();
        }
    }

    // ================ c2: 激发能验证 + 不变质量关联 (3x2) ================
    c2 = new TCanvas("c2","Ex",900,1200);
    c2->Divide(2,3);

    // --- 第一行: E_x(10Be) 重建 (logy) ---
    for (int j = 0; j < 2; ++j) {
        c2->cd(j+1); gPad->SetLogy();
        hEx[0][j]->SetLineColor(kBlack);
        hEx[1][j]->SetLineColor(kRed+1);
        hEx[2][j]->SetLineColor(kBlue+1); hEx[2][j]->SetLineStyle(2);
        double ymax = 2.0*std::max({hEx[0][j]->GetMaximum(), hEx[1][j]->GetMaximum(), hEx[2][j]->GetMaximum()});
        hEx[0][j]->SetMinimum(0.5); hEx[0][j]->SetMaximum(ymax);
        hEx[0][j]->Draw("hist"); hEx[1][j]->Draw("hist same"); hEx[2][j]->Draw("hist same");
        TLegend *leg = new TLegend(0.55,0.7,0.88,0.88);
        leg->AddEntry(hEx[0][j], "true", "l");
        leg->AddEntry(hEx[1][j], "from Q3", "l");
        leg->AddEntry(hEx[2][j], "from Q2", "l");
        leg->Draw();
    }

    // --- 第二行: inv.mass vs Q2 ---
    for (int j = 0; j < 2; ++j) {
        c2->cd(j+3); gPad->SetRightMargin(0.12);
        hInvQ2[j]->Draw("colz");
        int p = j+1;
        vline(K.Qgs(p), 8, 22, kWhite); vline(K.Qgs(p)-3.368, 8, 22, kMagenta+1);
    }
    // --- 第三行: inv.mass vs Q3 ---
    for (int j = 0; j < 2; ++j) {
        c2->cd(j+5); gPad->SetRightMargin(0.12);
        hInvQ[j]->Draw("colz");
        int p = j+1;
        vline(K.Qgs(p), 8, 22, kWhite); vline(K.Qgs(p)-3.368, 8, 22, kMagenta+1);
    }


}

void q_reconstruction()
{
gROOT->SetBatch(kTRUE);
gStyle->SetOptStat(0);
gSystem->mkdir("chapter4_figures", kTRUE);
DrawQAnalysis();
((TCanvas*)gROOT->FindObject("c1"))->Draw();
((TCanvas*)gROOT->FindObject("c1"))->SaveAs("chapter4_figures/q_methods.png");
((TCanvas*)gROOT->FindObject("c2"))->Draw();
((TCanvas*)gROOT->FindObject("c2"))->SaveAs("chapter4_figures/q_excitation.png");
}
