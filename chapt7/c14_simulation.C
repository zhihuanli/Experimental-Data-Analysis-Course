// Section 4.4: run from the directory containing the input ROOT files.
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

#include <iostream>
#include <fstream>
#include <vector>
#include <cmath>

#include "TFile.h"
#include "TTree.h"
#include "TParameter.h"
#include "TRandom.h"
#include "TMath.h"
#include "TLorentzVector.h"
#include "TVector3.h"
#include "TGenPhaseSpace.h"

using namespace std;

//====================================================
// 数据结构
//====================================================
struct C14Level {
    double ex;     // MeV
    double width;  // MeV
    double br;     // 分支比
};

struct Be10Branch {
    double ex;                // MeV
    double br;                // 分支比
    vector<C14Level> levels;  // 该 10Be 支路下对应的 14C* 能级
};

//====================================================
// 质量读取
//====================================================
double getMass(int zz, int aa, const char* inputFile = "mass.txt")
{
    const double keV2GeV = 1.0e-6;

    ifstream inFile(inputFile);
    if (!inFile.is_open()) {
        cerr << "Cannot open mass file: " << inputFile << endl;
        return -1.0;
    }

    int Z, A;
    double m;
    while (inFile >> Z >> A >> m) {
        if (Z == zz && A == aa) return m * keV2GeV;
    }

    cerr << "Mass not found for Z=" << zz << ", A=" << aa << endl;
    return -1.0;
}

//====================================================
// 按分支比抽样
//====================================================
int SelectIndex(const vector<double>& ratios)
{
    double sum = 0.0;
    for (size_t i = 0; i < ratios.size(); ++i) sum += ratios[i];
    if (sum <= 0.0) return -1;

    double r = gRandom->Uniform(0.0, sum);
    double cumulative = 0.0;

    for (size_t i = 0; i < ratios.size(); ++i) {
        cumulative += ratios[i];
        if (r < cumulative) return (int)i;
    }

    return (int)ratios.size() - 1;
}

//====================================================
// 截断 Breit-Wigner 抽样
//====================================================
double SampleBreitWigner(double mean, double width,
                         double xmin, double xmax,
                         int maxRetry = 100)
{
    for (int i = 0; i < maxRetry; ++i) {
        double x = gRandom->BreitWigner(mean, width);
        if (x >= xmin && x < xmax) return x;
    }
    return -1.0;
}

//====================================================
// 能量分辨
//====================================================
double eRes(double eraw, bool addRes = true) // input: GeV
{
    if (!addRes) return eraw;

    const double keVtoGeV = 1.0e-6;
    const double GeVtokeV = 1.0e6;

    const double sig_noise   = 50.0;   // keV
    const double fano_factor = 0.12;
    const double omega       = 3.6e-3; // keV

    const double energy_keV = eraw * GeVtokeV;
    const double sig_int    = TMath::Sqrt(omega * fano_factor * energy_keV);
    const double sig_tot    = TMath::Sqrt(sig_noise * sig_noise + sig_int * sig_int);

    double smeared_keV = -1.0;
    do {
        smeared_keV = gRandom->Gaus(energy_keV, sig_tot);
    } while (smeared_keV <= 0.0);

    return smeared_keV * keVtoGeV;
}

//====================================================
// 角度分辨
//====================================================
TVector3 angleRes(const TVector3& pvraw, bool addRes = true)
{
    TVector3 dir = pvraw.Unit();
    if (!addRes) return dir;

    const double deg = TMath::Pi() / 180.0;
    const double delta = 1.0 * deg;

    double theta = dir.Theta();
    double phi   = dir.Phi();

    theta += gRandom->Uniform(-0.5 * delta, 0.5 * delta);
    phi   += gRandom->Uniform(-0.5 * delta, 0.5 * delta);

    if (theta < 0.0) theta = -theta;
    if (theta > TMath::Pi()) theta = 2.0 * TMath::Pi() - theta;

    TVector3 out;
    out.SetMagThetaPhi(1.0, theta, phi);
    return out.Unit();
}

//====================================================
// 填写末态粒子信息
//====================================================
void FillChargedParticle(const TLorentzVector& lv, double massGeV,
                         double& ekMeV, double& thetaDeg, double& phiDeg,
                         bool smearE = true, bool smearA = true)
{
    const double MeV = 1.0e3;
    const double RadToDeg = 180.0 / TMath::Pi();

    double Traw = lv.E() - massGeV;
    TVector3 dir = angleRes(lv.Vect(), smearA);

    ekMeV    = eRes(Traw, smearE) * MeV;
    thetaDeg = dir.Theta() * RadToDeg;
    phiDeg   = dir.Phi()   * RadToDeg;

    if (phiDeg < 0.0) phiDeg += 360.0;
}

//====================================================
// 清空每个事件的缓存
//====================================================
void ResetEvent(double ek[4], double theta[4], double phi[4],
                double weight[3], int& hasGamma,
                double& eGamma, double& weight_total,
                double& exBe10, double& exC14)
{
    for (int i = 0; i < 4; ++i) {
        ek[i]    = -999.0;
        theta[i] = -999.0;
        phi[i]   = -999.0;
    }

    for (int i = 0; i < 3; ++i) weight[i] = 1.0;

    hasGamma = 0;
    eGamma = 0.0;
    weight_total = 1.0;
    exBe10 = -999.0;
    exC14 = -999.0;
}

//====================================================
// 构造衰变表
//====================================================
vector<Be10Branch> BuildDecayTable()
{
    vector<Be10Branch> table;

    Be10Branch b0;
    b0.ex = 0.0;
    b0.br = 0.50;
    b0.levels.push_back({14.9, 0.10, 0.25});
    b0.levels.push_back({15.6, 0.18, 0.50});
    b0.levels.push_back({16.4, 0.14, 0.25});
    table.push_back(b0);

    Be10Branch b1;
    b1.ex = 3.368;
    b1.br = 0.50;
    b1.levels.push_back({17.3, 0.12, 0.50});
    b1.levels.push_back({18.5, 0.08, 0.50});
    table.push_back(b1);

    return table;
}

//====================================================
// 主程序
//====================================================
void Simulation()
{
    gRandom->SetSeed(4401); // 固定种子，便于复现教学结果

    const double GeV = 1.0e-3; // MeV -> GeV
    const double MeV = 1.0e3;  // GeV -> MeV

    const int PROCESS_H = 1;
    const int PROCESS_C = 2;

    const double exC14Min = 0.0;
    const double exC14Max = 30.0;
    const double thresholdGeV = 100.0e-6; // 100 keV

    // ------------------------------------------------------------
    // Ground-state masses (GeV)
    // ------------------------------------------------------------
    const double mH1    = getMass(1, 1);
    const double mHe4   = getMass(2, 4);
    const double mBe10  = getMass(4, 10);
    const double mC12   = getMass(6, 12);
    const double mC14   = getMass(6, 14);
    const double mGamma = 0.0;

    if (mH1 < 0 || mHe4 < 0 || mBe10 < 0 || mC12 < 0 || mC14 < 0) {
        cout << "Mass loading failed." << endl;
        return;
    }

    // ------------------------------------------------------------
    // 衰变分支表
    // ------------------------------------------------------------
    vector<Be10Branch> decayTable = BuildDecayTable();

    // ------------------------------------------------------------
    // Beam input
    // ------------------------------------------------------------
    const double ekBeamMean  = 317.1;         // MeV
    const double ekBeamSigma = 1.83 / 2.355;   // MeV

    // ------------------------------------------------------------
    // Statistics
    // ------------------------------------------------------------
    const Long64_t nEventEach = 1000000;

    // ------------------------------------------------------------
    // Output
    // ------------------------------------------------------------
    TFile* fout = new TFile("C14_CHn_He4Be10x.root", "recreate");
    TTree* tree = new TTree("tree", "toy MC for 14C on (CH)n target");

    Int_t processID;   // 1: H 靶, 2: C 靶
    Int_t hasGamma;    // 0: 无 gamma, 1: 有 gamma

    Double_t ekBeam;   // MeV
    Double_t ek[4];    // MeV
    Double_t theta[4]; // degree
    Double_t phi[4];   // degree

    Double_t exBe10;   // MeV
    Double_t exC14;    // MeV
    Double_t eGamma;   // MeV, lab frame

    Double_t weight[3];
    Double_t weight_total;

    tree->Branch("processID",    &processID,    "processID/I");
    tree->Branch("hasGamma",     &hasGamma,     "hasGamma/I");
    tree->Branch("ekBeam",       &ekBeam,       "ekBeam/D");
    tree->Branch("ek",           ek,            "ek[4]/D");
    tree->Branch("theta",        theta,         "theta[4]/D");
    tree->Branch("phi",          phi,           "phi[4]/D");
    tree->Branch("exBe10",       &exBe10,       "exBe10/D");
    tree->Branch("exC14",        &exC14,        "exC14/D");
    tree->Branch("eGamma",       &eGamma,       "eGamma/D");
    tree->Branch("weight",       weight,        "weight[3]/D");
    tree->Branch("weight_total", &weight_total, "weight_total/D");

    fout->cd();
    TParameter<Double_t>("massH1", mH1).Write();
    TParameter<Double_t>("massC12", mC12).Write();
    TParameter<Double_t>("massHe4", mHe4).Write();
    TParameter<Double_t>("massBe10", mBe10).Write();
    TParameter<Double_t>("massC14", mC14).Write();
    TParameter<Double_t>("ekBeamMean", ekBeamMean).Write();
    TParameter<Long64_t>("nEventEach", nEventEach).Write();

    // ------------------------------------------------------------
    // 两个过程写入同一个 TTree
    //
    // 统一约定：
    // ek[0],theta[0],phi[0] : alpha
    // ek[1],theta[1],phi[1] : final 10Be
    // ek[2],theta[2],phi[2] : recoil (H 靶为 p, C 靶为 12C)
    // ek[3],theta[3],phi[3] : gamma 退激前的 10Be*（仅 hasGamma=1 时有意义）
    // ------------------------------------------------------------
    for (int proc = PROCESS_H; proc <= PROCESS_C; ++proc) {
        Long64_t entriesBefore = tree->GetEntries();

        const double mTarget = (proc == PROCESS_H) ? mH1  : mC12;
        const double mRecoil = (proc == PROCESS_H) ? mH1  : mC12;

        TLorentzVector target(0.0, 0.0, 0.0, mTarget);

        for (Long64_t n = 0; n < nEventEach; ++n) {

            processID = proc;
            ResetEvent(ek, theta, phi, weight, hasGamma, eGamma, weight_total, exBe10, exC14);

            // ----------------------------------------------------
            // 1. Beam
            // ----------------------------------------------------
            double Tbeam_GeV = gRandom->Gaus(ekBeamMean * GeV, ekBeamSigma * GeV);
            if (Tbeam_GeV <= 0.0) continue;

            double Ebeam_GeV = Tbeam_GeV + mC14;
            double pbeam_GeV = TMath::Sqrt(Ebeam_GeV * Ebeam_GeV - mC14 * mC14);

            TLorentzVector beam(0.0, 0.0, pbeam_GeV, Ebeam_GeV);
            TLorentzVector compound = beam + target;

            // ----------------------------------------------------
            // 2. 选 10Be 支路
            // ----------------------------------------------------
            vector<double> be10Ratios;
            for (size_t i = 0; i < decayTable.size(); ++i) {
                be10Ratios.push_back(decayTable[i].br);
            }

            int iBe10 = SelectIndex(be10Ratios);
            if (iBe10 < 0) continue;

            exBe10 = decayTable[iBe10].ex;

            // ----------------------------------------------------
            // 3. 在选中的 10Be 支路下，再选 14C* 能级
            // ----------------------------------------------------
            vector<double> c14Ratios;
            for (size_t i = 0; i < decayTable[iBe10].levels.size(); ++i) {
                c14Ratios.push_back(decayTable[iBe10].levels[i].br);
            }

            int iC14 = SelectIndex(c14Ratios);
            if (iC14 < 0) continue;

            C14Level level = decayTable[iBe10].levels[iC14];
            exC14 = SampleBreitWigner(level.ex, level.width, exC14Min, exC14Max, 100);
            if (exC14 < 0.0) continue;

            // ----------------------------------------------------
            // 4. compound -> recoil + 14C*
            // ----------------------------------------------------
            TGenPhaseSpace decay1;
            double masses1[2] = {mRecoil, mC14 + exC14 * GeV};
            if (!decay1.SetDecay(compound, 2, masses1)) continue;

            weight[0] = decay1.Generate();
            TLorentzVector* recoil = decay1.GetDecay(0);
            TLorentzVector* c14x   = decay1.GetDecay(1);

            // ----------------------------------------------------
            // 5. 14C* -> alpha + 10Be*
            // ----------------------------------------------------
            TGenPhaseSpace decay2;
            double masses2[2] = {mHe4, mBe10 + exBe10 * GeV};
            if (!decay2.SetDecay(*c14x, 2, masses2)) continue;

            weight[1] = decay2.Generate();
            TLorentzVector* alpha = decay2.GetDecay(0);
            TLorentzVector* be10x = decay2.GetDecay(1);

            // ----------------------------------------------------
            // 6. 若 10Be 为激发态，则总是继续做 gamma 退激
            // ----------------------------------------------------
            TLorentzVector be10_final = *be10x;

            if (exBe10 > 1.0e-6) {
                TGenPhaseSpace decay3;
                double masses3[2] = {mBe10, mGamma};
                if (!decay3.SetDecay(*be10x, 2, masses3)) continue;

                weight[2] = decay3.Generate();

                TLorentzVector* be10  = decay3.GetDecay(0);
                TLorentzVector* gamma = decay3.GetDecay(1);

                be10_final = *be10;
                eGamma = gamma->E() * MeV; // 实验室系 gamma 能量
                hasGamma = 1;
            }

            weight_total = weight[0] * weight[1] * weight[2];

            // ----------------------------------------------------
            // 7. 阈值判断
            // ----------------------------------------------------
            double Traw_alpha  = alpha->E()  - mHe4;
            double Traw_recoil = recoil->E() - mRecoil;

            double Traw_be10 = 0.0;
            if (hasGamma) {
                Traw_be10 = be10_final.E() - mBe10;
            } else {
                Traw_be10 = be10x->E() - (mBe10 + exBe10 * GeV);
            }

            if (Traw_alpha  < thresholdGeV) continue;
            if (Traw_be10   < thresholdGeV) continue;
            if (Traw_recoil < thresholdGeV) continue;

            // ----------------------------------------------------
            // 8. 统一写树
            // ----------------------------------------------------
            FillChargedParticle(*alpha, mHe4, ek[0], theta[0], phi[0]);

            if (hasGamma) {
                FillChargedParticle(be10_final, mBe10, ek[1], theta[1], phi[1]);
                FillChargedParticle(*be10x, mBe10 + exBe10 * GeV,
                                    ek[3], theta[3], phi[3],
                                    false, false);
            } else {
                FillChargedParticle(*be10x, mBe10 + exBe10 * GeV,
                                    ek[1], theta[1], phi[1]);
            }

            FillChargedParticle(*recoil, mRecoil, ek[2], theta[2], phi[2]);

            ekBeam = Tbeam_GeV * MeV;
            tree->Fill();
        }
        cout << "processID=" << proc << ": attempted=" << nEventEach
             << ", saved=" << tree->GetEntries()-entriesBefore << endl;
    }

    tree->Write();
    fout->Close();

    cout << "Simulation finished: C14_CHn_He4Be10x.root" << endl;
}

void c14_simulation()
{
gROOT->SetBatch(kTRUE);
gStyle->SetOptStat(0);
gSystem->mkdir("chapter4_figures", kTRUE);
Simulation();
TFile *f = new TFile("C14_CHn_He4Be10x.root");
if (f->IsZombie()) throw std::runtime_error("Run Simulation first");
TTree *tree = f->Get<TTree>("tree");
tree->Print(); // 一行对应一个通过生成条件的事件
gStyle->SetOptStat(0);
gStyle->SetPalette(kBird);
gStyle->SetPadLeftMargin(0.15);
gStyle->SetPadRightMargin(0.16);
//====================================================
// c1: H/C target kinematics
// 2 rows x 3 cols, each pad ~300x300
//====================================================
TCanvas *c1 = new TCanvas("c1","H/C target kinematics",900,600);
c1->Divide(3,2);

// ---- H target ----
c1->cd(1);
gPad->SetRightMargin(0.12);
tree->Draw("ek[0]:theta[0]>>h1_H_a(300,0,120,300,0,140)",
           "(processID==1)*weight_total","colz");
((TH2*)gROOT->FindObject("h1_H_a"))->SetTitle("H: #alpha;#theta_{#alpha} [deg];E_{k,#alpha} [MeV]");

c1->cd(2);
gPad->SetRightMargin(0.12);
tree->Draw("ek[1]:theta[1]>>h1_H_b(300,0,120,300,0,260)",
           "(processID==1)*weight_total","colz");
((TH2*)gROOT->FindObject("h1_H_b"))->SetTitle("H: ^{10}Be;#theta_{^{10}Be} [deg];E_{k,^{10}Be} [MeV]");

c1->cd(3);
gPad->SetRightMargin(0.12);
tree->Draw("ek[2]:theta[2]>>h1_H_r(300,0,120,300,0,80)",
           "(processID==1)*weight_total","colz");
((TH2*)gROOT->FindObject("h1_H_r"))->SetTitle("H: recoil p;#theta_{recoil} [deg];E_{k,recoil} [MeV]");

// ---- C target ----
c1->cd(4);
gPad->SetRightMargin(0.12);
tree->Draw("ek[0]:theta[0]>>h1_C_a(300,0,120,300,0,140)",
           "(processID==2)*weight_total","colz");
((TH2*)gROOT->FindObject("h1_C_a"))->SetTitle("C: #alpha;#theta_{#alpha} [deg];E_{k,#alpha} [MeV]");

c1->cd(5);
gPad->SetRightMargin(0.12);
tree->Draw("ek[1]:theta[1]>>h1_C_b(300,0,120,300,0,260)",
           "(processID==2)*weight_total","colz");
((TH2*)gROOT->FindObject("h1_C_b"))->SetTitle("C: ^{10}Be;#theta_{^{10}Be} [deg];E_{k,^{10}Be} [MeV]");

c1->cd(6);
gPad->SetRightMargin(0.12);
tree->Draw("ek[2]:theta[2]>>h1_C_r(300,0,120,300,0,320)",
           "(processID==2)*weight_total","colz");
((TH2*)gROOT->FindObject("h1_C_r"))->SetTitle("C: recoil ^{12}C;#theta_{recoil} [deg];E_{k,recoil} [MeV]");

c1->Draw();
((TCanvas*)gROOT->FindObject("c1"))->SaveAs("chapter4_figures/c14_energy_angle.png");
TCanvas *c2 = new TCanvas("c2","Energy-energy correlations",600,600);
c2->Divide(2,2);

// ---- H target ----
c2->cd(1);
gPad->SetRightMargin(0.12);
tree->Draw("ek[1]:ek[0]>>h2_H_ab(300,0,140,300,0,260)",
           "(processID==1)*weight_total","colz");
((TH2*)gROOT->FindObject("h2_H_ab"))->SetTitle("H: E_{k}(^{10}Be) vs E_{k}(#alpha);E_{k,#alpha} [MeV];E_{k,^{10}Be} [MeV]");

c2->cd(2);
gPad->SetRightMargin(0.12);
tree->Draw("ek[2]:ek[0]>>h2_H_ar(300,0,140,300,0,80)",
           "(processID==1)*weight_total","colz");
((TH2*)gROOT->FindObject("h2_H_ar"))->SetTitle("H: E_{k}(recoil) vs E_{k}(#alpha);E_{k,#alpha} [MeV];E_{k,recoil} [MeV]");

// ---- C target ----
c2->cd(3);
gPad->SetRightMargin(0.12);
tree->Draw("ek[1]:ek[0]>>h2_C_ab(300,0,140,300,0,260)",
           "(processID==2)*weight_total","colz");
((TH2*)gROOT->FindObject("h2_C_ab"))->SetTitle("C: E_{k}(^{10}Be) vs E_{k}(#alpha);E_{k,#alpha} [MeV];E_{k,^{10}Be} [MeV]");

c2->cd(4);
gPad->SetRightMargin(0.12);
tree->Draw("ek[2]:ek[0]>>h2_C_ar(300,0,140,300,0,320)",
           "(processID==2)*weight_total","colz");
((TH2*)gROOT->FindObject("h2_C_ar"))->SetTitle("C: E_{k}(recoil) vs E_{k}(#alpha);E_{k,#alpha} [MeV];E_{k,recoil} [MeV]");

c2->Draw();
((TCanvas*)gROOT->FindObject("c2"))->SaveAs("chapter4_figures/c14_energy_correlation.png");
TCanvas *c3 = new TCanvas("c3","Angle-angle correlations",600,600);
c3->Divide(2,2);

// ---- H target ----
c3->cd(1);
gPad->SetRightMargin(0.12);
tree->Draw("theta[1]:theta[0]>>h3_H_ab(300,0,120,300,0,120)",
           "(processID==1)*weight_total","colz");
((TH2*)gROOT->FindObject("h3_H_ab"))->SetTitle("H: #theta(^{10}Be) vs #theta(#alpha);#theta_{#alpha} [deg];#theta_{^{10}Be} [deg]");

c3->cd(2);
gPad->SetRightMargin(0.12);
tree->Draw("theta[2]:theta[0]>>h3_H_ar(300,0,120,300,0,120)",
           "(processID==1)*weight_total","colz");
((TH2*)gROOT->FindObject("h3_H_ar"))->SetTitle("H: #theta(recoil) vs #theta(#alpha);#theta_{#alpha} [deg];#theta_{recoil} [deg]");

// ---- C target ----
c3->cd(3);
gPad->SetRightMargin(0.12);
tree->Draw("theta[1]:theta[0]>>h3_C_ab(300,0,120,300,0,120)",
           "(processID==2)*weight_total","colz");
((TH2*)gROOT->FindObject("h3_C_ab"))->SetTitle("C: #theta(^{10}Be) vs #theta(#alpha);#theta_{#alpha} [deg];#theta_{^{10}Be} [deg]");

c3->cd(4);
gPad->SetRightMargin(0.12);
tree->Draw("theta[2]:theta[0]>>h3_C_ar(300,0,120,300,0,120)",
           "(processID==2)*weight_total","colz");
((TH2*)gROOT->FindObject("h3_C_ar"))->SetTitle("C: #theta(recoil) vs #theta(#alpha);#theta_{#alpha} [deg];#theta_{recoil} [deg]");

c3->Draw();
((TCanvas*)gROOT->FindObject("c3"))->SaveAs("chapter4_figures/c14_angle_correlation.png");
TCanvas *c4 = new TCanvas("c4","Input structure check",900,900);
c4->Divide(2,2);

c4->cd(1);
tree->Draw("exC14>>h8_exC14_H(400,13,20)",
           "(processID==1)*weight_total","hist");
((TH1*)gROOT->FindObject("h8_exC14_H"))->SetTitle("H target: E_{x}(^{14}C);E_{x}(^{14}C) [MeV];weighted counts");

c4->cd(2);
tree->Draw("exC14>>h8_exC14_C(400,13,20)",
           "(processID==2)*weight_total","hist");
((TH1*)gROOT->FindObject("h8_exC14_C"))->SetTitle("C target: E_{x}(^{14}C);E_{x}(^{14}C) [MeV];weighted counts");

c4->cd(3);
tree->Draw("exBe10>>h8_exBe10(120,0,5)",
           "weight_total","hist");
((TH1*)gROOT->FindObject("h8_exBe10"))->SetTitle("^{10}Be excitation;E_{x}(^{10}Be) [MeV];weighted counts");

c4->cd(4);
tree->Draw("eGamma>>h8_g(300,0,10)",
           "(hasGamma==1)*weight_total","hist");
((TH1*)gROOT->FindObject("h8_g"))->SetTitle("#gamma energy in lab;E_{#gamma}^{lab} [MeV];weighted counts");

c4->Draw();
((TCanvas*)gROOT->FindObject("c4"))->SaveAs("chapter4_figures/c14_input_states.png");
}
