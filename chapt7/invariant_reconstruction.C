// Generated from 7.6 Invariant mass reconstruction.ipynb by tools/export_kinematics_macros.py.
// Run from chapt7; figures are drawn by ROOT, not replaced with image files.
#include <iostream>
#include <fstream>
#include <vector>
#include <cmath>
#include <algorithm>
#include <stdexcept>
#include <TROOT.h>
#include <TFile.h>
#include <TTree.h>
#include <TParameter.h>
#include <TGenPhaseSpace.h>
#include <TLorentzVector.h>
#include <TVector3.h>
#include <TMath.h>
#include <TRandom3.h>
#include <TCanvas.h>
#include <TH1D.h>
#include <TH2D.h>
#include <TH1F.h>
#include <TH2F.h>
#include <TLegend.h>
#include <TLine.h>
#include <TStyle.h>

TVector3 MeasuredMomentum(double kineticEnergy, double mass,
                          double thetaDeg, double phiDeg)
{
    double p = std::sqrt(kineticEnergy*kineticEnergy + 2.0*kineticEnergy*mass);
    TVector3 momentum;
    momentum.SetMagThetaPhi(p, thetaDeg*TMath::DegToRad(), phiDeg*TMath::DegToRad());
    return momentum; // MeV/c；动能与质量均用 MeV
}

void TargetID_CHn()
{
    TFile *f = TFile::Open("C14_CHn_He4Be10x.root");
    if (!f || f->IsZombie()) throw std::runtime_error("Run Section 4.4 first");
    TTree *tree = f->Get<TTree>("tree");
    if (!tree) throw std::runtime_error("Missing tree");

    gStyle->SetPadLeftMargin(0.15);
    gStyle->SetPadRightMargin(0.16);

    const double u  = 1000.0;          // mass: GeV -> MeV
    const double mu = 931.494;
    const double k  = 58.0 / 60.0;

    // masses and beam mean from TParameter
    double mHe4       = ((TParameter<Double_t>*)f->Get("massHe4"))->GetVal() * u;
    double mBe10      = ((TParameter<Double_t>*)f->Get("massBe10"))->GetVal() * u;
    double mC14       = ((TParameter<Double_t>*)f->Get("massC14"))->GetVal() * u;
    double ekBeamMean = ((TParameter<Double_t>*)f->Get("ekBeamMean"))->GetVal(); // MeV

    // branches
    Double_t ek[4], theta[4], phi[4];
    Double_t weight_total;

    tree->SetBranchAddress("ek",           ek);
    tree->SetBranchAddress("theta",        theta);
    tree->SetBranchAddress("phi",          phi);
    tree->SetBranchAddress("weight_total", &weight_total);

    TH2F *hEP = new TH2F("hEP", "Target identification;x = p_{miss}^{2}/(2m_{u}) [MeV];y = T_{beam}-T_{#alpha}-T_{Be} [MeV]", 400, 0, 80, 400, 0, 80);
    TH1F *hQ  = new TH1F("hQ",  "H-candidate gate;Q_{rec} [MeV];Sum of weights", 400, -20, -5);

    // mean beam momentum
    double pBeamMean = std::sqrt(ekBeamMean*ekBeamMean + 2.0*ekBeamMean*mC14);
    TVector3 pvBeam;
    pvBeam.SetMagThetaPhi(pBeamMean, 0.0, 0.0);

    Long64_t nentries = tree->GetEntriesFast();
    for (Long64_t i = 0; i < nentries; ++i) {
        tree->GetEntry(i);

        // alpha
        TVector3 pvAlpha = MeasuredMomentum(ek[0], mHe4, theta[0], phi[0]);

        // final 10Be
        TVector3 pvBe = MeasuredMomentum(ek[1], mBe10, theta[1], phi[1]);

        // missing recoil momentum
        double pRec = (pvBeam - pvAlpha - pvBe).Mag();

        double x = pRec * pRec / (2.0 * mu);
        double y = ekBeamMean - ek[0] - ek[1];

        hEP->Fill(x, y, weight_total);

        // H-target gate
        if (y <  9.5 + k*x) continue;
        if (y > 18.5 + k*x) continue;

        double Q = k*x - y;
        hQ->Fill(Q, weight_total);
    }

    TCanvas *c1 = new TCanvas("c1", "Target identification", 800, 400);
    c1->Divide(2, 1);

    c1->cd(1);
    hEP->Draw("colz");
    TLine *l1 = new TLine(0,  9.5, 60, 67.5);
    TLine *l2 = new TLine(0, 18.5, 60, 76.5);
    l1->Draw();
    l2->Draw();
    gPad->SetLogz();

    c1->cd(2);
    hQ->Draw("hist");

    c1->Draw();
}

void MassSpectrum_CHn()
{
    TFile *f = TFile::Open("C14_CHn_He4Be10x.root");
    if (!f || f->IsZombie()) throw std::runtime_error("Run Section 4.4 first");
    TTree *tree = f->Get<TTree>("tree");
    if (!tree) throw std::runtime_error("Missing tree");

    gStyle->SetPadLeftMargin(0.15);
    gStyle->SetPadRightMargin(0.16);

    const double u  = 1000.0;          // mass: GeV -> MeV
    const double mu = 931.494;
    const double k  = 58.0 / 60.0;

    // masses and beam mean from TParameter
    double mHe4       = ((TParameter<Double_t>*)f->Get("massHe4"))->GetVal() * u;
    double mBe10      = ((TParameter<Double_t>*)f->Get("massBe10"))->GetVal() * u;
    double mC14       = ((TParameter<Double_t>*)f->Get("massC14"))->GetVal() * u;
    double ekBeamMean = ((TParameter<Double_t>*)f->Get("ekBeamMean"))->GetVal(); // MeV

    // branches
    Double_t ek[4], theta[4], phi[4];
    Double_t exC14, weight_total;

    tree->SetBranchAddress("ek",           ek);
    tree->SetBranchAddress("theta",        theta);
    tree->SetBranchAddress("phi",          phi);
    tree->SetBranchAddress("exC14",        &exC14);
    tree->SetBranchAddress("weight_total", &weight_total);

    // 真值只用于评价下述选择，不参与门选。
    Int_t processID;
    Double_t exBe10;
    tree->SetBranchAddress("processID", &processID);
    tree->SetBranchAddress("exBe10", &exBe10);
    double selectedWeight=0, hWeight=0, correctBranchWeight=0;

    TH1F *hExcal  = new TH1F("hExcal",  "Reconstructed;E_{x}(^{14}C) [MeV];Sum of weights",   400, 12, 22);
    TH2F *hExcalQ = new TH2F("hExcalQ", "Reconstructed;E_{x}(^{14}C) [MeV];Q_{rec} [MeV]", 400, 12, 22, 400, -20, -5);
    TH1F *hEx     = new TH1F("hEx",     "Truth, same selected events;E_{x}(^{14}C) [MeV];Sum of weights", 400, 12, 22);
    TH2F *hExQ    = new TH2F("hExQ",    "Truth, same selected events;E_{x,true}(^{14}C) [MeV];Q_{rec} [MeV]",    400, 12, 22, 400, -20, -5);

    // mean beam momentum
    double pBeamMean = std::sqrt(ekBeamMean*ekBeamMean + 2.0*ekBeamMean*mC14);
    TVector3 pvBeam;
    pvBeam.SetMagThetaPhi(pBeamMean, 0.0, 0.0);

    Long64_t nentries = tree->GetEntriesFast();
    for (Long64_t i = 0; i < nentries; ++i) {
        tree->GetEntry(i);

        // step 1: use final alpha + final 10Be to do H gate
        TVector3 pvAlpha0 = MeasuredMomentum(ek[0], mHe4, theta[0], phi[0]);

        TVector3 pvBe0 = MeasuredMomentum(ek[1], mBe10, theta[1], phi[1]);

        double pRec = (pvBeam - pvAlpha0 - pvBe0).Mag();

        double x = pRec * pRec / (2.0 * mu);
        double y = ekBeamMean - ek[0] - ek[1];

        // H-target gate
        if (y <  9.5 + k*x) continue;
        if (y > 18.5 + k*x) continue;

        // reconstructed Q from x-y band
        double Q = k*x - y;

        // step 2: choose 10Be mass according to Q branch
        double mBeUse = -1.0;
        if (Q < -14.5) mBeUse = mBe10 + 3.368; // 10Be*(3.368)
        if (Q > -13.5) mBeUse = mBe10;         // 10Be(gs)

        // skip the transition region
        if (mBeUse < 0.0) continue;

        // step 3: build two-body invariant mass
        TVector3 pvAlpha = MeasuredMomentum(ek[0], mHe4, theta[0], phi[0]);

        TVector3 pvBe = MeasuredMomentum(ek[1], mBe10, theta[1], phi[1]);

        TLorentzVector lvAlpha(pvAlpha, ek[0] + mHe4);
        TLorentzVector lvBe   (pvBe,    ek[1] + mBeUse);

        double Minv = (lvAlpha + lvBe).M();
        double Ex   = Minv - mC14;

        hExcal->Fill(Ex, weight_total);
        hExcalQ->Fill(Ex, Q, weight_total);

        selectedWeight += weight_total;
        if (processID == 1) hWeight += weight_total;
        if ((Q < -14.5) == (exBe10 > 1.0)) correctBranchWeight += weight_total;

        // truth for comparison
        hEx->Fill(exC14, weight_total);
        hExQ->Fill(exC14, Q, weight_total);
    }
    if (selectedWeight > 0) {
        std::cout << "H fraction after both gates = " << hWeight/selectedWeight << std::endl;
        std::cout << "Correct branch fraction = " << correctBranchWeight/selectedWeight << std::endl;
    }

    TCanvas *c2 = new TCanvas("c2", "Invariant mass", 800, 800);
    c2->Divide(2, 2);

    c2->cd(1);
    hExcal->Draw("hist");

    c2->cd(2);
    hExcalQ->Draw("colz");
    gPad->SetLogz();

    c2->cd(3);
    hEx->Draw("hist");

    c2->cd(4);
    hExQ->Draw("colz");
    gPad->SetLogz();

    c2->Draw();
}

void invariant_reconstruction()
{
    TargetID_CHn();

    MassSpectrum_CHn();
}
