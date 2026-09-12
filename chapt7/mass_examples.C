// Section 4.3: run from the directory containing the input ROOT files.
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

TCanvas *c = new TCanvas("c", "c", 700, 500);
c->SetLeftMargin(0.15);

const double m_alpha = 3.727379378;      // GeV

const double c12_threshold = 0.0072747;  // GeV = 7.2747 MeV
const double m_c12_gs = 3.0 * m_alpha - c12_threshold;

const double be8_gs_excess = 0.00009184; // GeV = 91.84 keV
const double m_be8_gs = 2.0 * m_alpha + be8_gs_excess;

TLorentzVector MakeAlphaP4(double T_mev, double theta_deg, double phi_deg)
{
    double T  = T_mev / 1000.0;   // MeV -> GeV
    double E  = T + m_alpha;
    double p  = std::sqrt(T * T + 2.0 * m_alpha * T);

    double th = theta_deg * TMath::DegToRad();
    double ph = phi_deg   * TMath::DegToRad();

    double px = p * std::sin(th) * std::cos(ph);
    double py = p * std::sin(th) * std::sin(ph);
    double pz = p * std::cos(th);

    return TLorentzVector(px, py, pz, E);
}

void excitation_energy_12c_from_3alpha()
{
    TFile *f = TFile::Open("direct_3alpha.root");
    if (!f || f->IsZombie()) throw std::runtime_error("Run Section 4.2 first: input file missing");
    TTree *tr = (TTree*)f->Get("events");

    double T_rest[3];
    double theta_rest[3];
    double phi_rest[3];
    double weight;

    tr->SetBranchAddress("T_rest", T_rest);
    tr->SetBranchAddress("theta_rest", theta_rest);
    tr->SetBranchAddress("phi_rest", phi_rest);
    tr->SetBranchAddress("weight", &weight);

    TH1F *h = new TH1F(
        "h",
        "Excitation energy of ^{12}C*;E_{x}(MeV);Sum of weights",
        240, 0.0, 20.0
    );

    double maxEnergyError = 0.0; // MeV: compare each event with the fixed input
    double maxMomentum = 0.0;    // MeV/c: total momentum in the parent rest frame

    Long64_t nentries = tr->GetEntries();

    for (Long64_t i = 0; i < nentries; ++i) {
        tr->GetEntry(i);

        TLorentzVector p1 = MakeAlphaP4(T_rest[0], theta_rest[0], phi_rest[0]);
        TLorentzVector p2 = MakeAlphaP4(T_rest[1], theta_rest[1], phi_rest[1]);
        TLorentzVector p3 = MakeAlphaP4(T_rest[2], theta_rest[2], phi_rest[2]);

        double m3a = (p1 + p2 + p3).M();            // GeV
        double ex  = (m3a - m_c12_gs) * 1000.0;    // MeV

        maxEnergyError = std::max(maxEnergyError, std::abs(ex - 16.6197));
        maxMomentum = std::max(maxMomentum, (p1+p2+p3).P()*1000.0);
        h->Fill(ex, weight);
    }
    std::cout << "Reconstructed Ex = " << h->GetMean() << " MeV" << std::endl;
    std::cout << "Max |Ex - input| = " << maxEnergyError << " MeV" << std::endl;
    std::cout << "Max |sum p_rest| = " << maxMomentum << " MeV/c" << std::endl;
    h->Draw("hist");
    c->Draw();
}

void missing_mass_excitation_energy_be8()
{
    TFile *f1 = TFile::Open("direct_3alpha.root");
    if (!f1 || f1->IsZombie()) throw std::runtime_error("Run Section 4.2 first: input file missing");
    TTree *tr1 = (TTree*)f1->Get("events");

    TFile *f2 = TFile::Open("sequential_3alpha.root");
    if (!f2 || f2->IsZombie()) throw std::runtime_error("Run Section 4.2 first: input file missing");
    TTree *tr2 = (TTree*)f2->Get("events");

    double T_move[3];
    double theta_move[3];
    double phi_move[3];
    double weight;

    TH1F *h_dir = new TH1F(
        "h_dir",
        "Missing-mass excitation energy relative to ^{8}Be(g.s.);E_{x}(MeV);Sum of weights",
        240, -0.5, 10.0
    );

    TH1F *h_seq = new TH1F(
        "h_seq",
        "Missing-mass excitation energy relative to ^{8}Be(g.s.);E_{x}(MeV);Sum of weights",
        240, -0.5, 10.0
    );

    tr1->SetBranchAddress("T_move", T_move);
    tr1->SetBranchAddress("theta_move", theta_move);
    tr1->SetBranchAddress("phi_move", phi_move);
    tr1->SetBranchAddress("weight", &weight);

    Long64_t n1 = tr1->GetEntries();

    for (Long64_t i = 0; i < n1; ++i) {
        tr1->GetEntry(i);

        TLorentzVector p1 = MakeAlphaP4(T_move[0], theta_move[0], phi_move[0]);
        TLorentzVector p2 = MakeAlphaP4(T_move[1], theta_move[1], phi_move[1]);
        TLorentzVector p3 = MakeAlphaP4(T_move[2], theta_move[2], phi_move[2]);
        TLorentzVector p_total = p1 + p2 + p3;

        double ex1 = ((p_total - p1).M() - m_be8_gs) * 1000.0; // recoil against alpha 1
        double ex2 = ((p_total - p2).M() - m_be8_gs) * 1000.0; // recoil against alpha 2
        double ex3 = ((p_total - p3).M() - m_be8_gs) * 1000.0; // recoil against alpha 3

        h_dir->Fill(ex1, weight);
        h_dir->Fill(ex2, weight);
        h_dir->Fill(ex3, weight);
    }

    tr2->SetBranchAddress("T_move", T_move);
    tr2->SetBranchAddress("theta_move", theta_move);
    tr2->SetBranchAddress("phi_move", phi_move);
    tr2->SetBranchAddress("weight", &weight);

    Long64_t n2 = tr2->GetEntries();

    for (Long64_t i = 0; i < n2; ++i) {
        tr2->GetEntry(i);

        TLorentzVector p1 = MakeAlphaP4(T_move[0], theta_move[0], phi_move[0]);
        TLorentzVector p2 = MakeAlphaP4(T_move[1], theta_move[1], phi_move[1]);
        TLorentzVector p3 = MakeAlphaP4(T_move[2], theta_move[2], phi_move[2]);

        TLorentzVector p_total = p1 + p2 + p3;

        double ex1 = ((p_total - p1).M() - m_be8_gs) * 1000.0;
        double ex2 = ((p_total - p2).M() - m_be8_gs) * 1000.0;
        double ex3 = ((p_total - p3).M() - m_be8_gs) * 1000.0;

        h_seq->Fill(ex1, weight);
        h_seq->Fill(ex2, weight);
        h_seq->Fill(ex3, weight);
    }

    h_dir->Scale(1.0 / h_dir->Integral());
    h_seq->Scale(1.0 / h_seq->Integral());
    h_dir->GetYaxis()->SetTitle("Fraction of weighted pairs / bin");
    h_seq->GetYaxis()->SetTitle("Fraction of weighted pairs / bin");
    h_seq->SetMaximum(1.1*std::max(h_dir->GetMaximum(), h_seq->GetMaximum()));

    h_dir->SetLineColor(kBlue);
    h_seq->SetLineColor(kRed);

    c->Clear();
    gStyle->SetOptStat(0);

    h_seq->Draw("hist");
    h_dir->Draw("hist same");

    TLegend *leg = new TLegend(0.58, 0.72, 0.88, 0.88);
    leg->AddEntry(h_dir, "Direct", "l");
    leg->AddEntry(h_seq, "Sequential", "l");
    leg->Draw();
    c->Draw();
}

void dalitz_plot_3alpha()
{
    TFile *f1 = TFile::Open("direct_3alpha.root");
    if (!f1 || f1->IsZombie()) throw std::runtime_error("Run Section 4.2 first: input file missing");
    TTree *tr1 = (TTree*)f1->Get("events");

    TFile *f2 = TFile::Open("sequential_3alpha.root");
    if (!f2 || f2->IsZombie()) throw std::runtime_error("Run Section 4.2 first: input file missing");
    TTree *tr2 = (TTree*)f2->Get("events");

    double T_rest[3];
    double theta_rest[3];
    double phi_rest[3];
    double weight;

    TH2F *h_dir = new TH2F(
        "h_dir",
        "Dalitz plot: direct decay;x;y",
        250, -1.4, 1.4,
        250, -1.4, 1.4
    );

    TH2F *h_seq = new TH2F(
        "h_seq",
        "Dalitz plot: sequential decay;x;y",
        250, -1.4, 1.4,
        250, -1.4, 1.4
    );

    tr1->SetBranchAddress("T_rest", T_rest);
    tr1->SetBranchAddress("theta_rest", theta_rest);
    tr1->SetBranchAddress("phi_rest", phi_rest);
    tr1->SetBranchAddress("weight", &weight);

    Long64_t n1 = tr1->GetEntries();

    for (Long64_t i = 0; i < n1; ++i) {
        tr1->GetEntry(i);

        double T1 = T_rest[0];
        double T2 = T_rest[1];
        double T3 = T_rest[2];
        double Tsum = T1 + T2 + T3;

        if (Tsum <= 0.0) continue;

        double e1 = T1 / Tsum;
        double e2 = T2 / Tsum;
        double e3 = T3 / Tsum;

        double x = std::sqrt(3.0) * (e1 - e2);
        double y = 2.0 * e3 - e1 - e2;

        h_dir->Fill(x, y, weight);
    }

    tr2->SetBranchAddress("T_rest", T_rest);
    tr2->SetBranchAddress("theta_rest", theta_rest);
    tr2->SetBranchAddress("phi_rest", phi_rest);
    tr2->SetBranchAddress("weight", &weight);

    Long64_t n2 = tr2->GetEntries();

    for (Long64_t i = 0; i < n2; ++i) {
        tr2->GetEntry(i);

        double T1 = T_rest[0];
        double T2 = T_rest[1];
        double T3 = T_rest[2];
        double Tsum = T1 + T2 + T3;

        if (Tsum <= 0.0) continue;

        double e1 = T1 / Tsum;
        double e2 = T2 / Tsum;
        double e3 = T3 / Tsum;

        double x = std::sqrt(3.0) * (e1 - e2);
        double y = 2.0 * e3 - e1 - e2;

        h_seq->Fill(x, y, weight);
    }
    gStyle->SetOptStat(0);
    gStyle->SetPadLeftMargin(0.14);
    gStyle->SetPadRightMargin(0.15);

    if (c) { delete c; c = nullptr; }
    TCanvas *c1 = new TCanvas("c1", "Dalitz direct", 700, 700);
    h_dir->Draw("colz");


    TCanvas *c2 = new TCanvas("c2", "Dalitz sequential", 700, 700);
    h_seq->Draw("colz");
}

void mass_examples()
{
gROOT->SetBatch(kTRUE);
gStyle->SetOptStat(0);
gSystem->mkdir("chapter4_figures", kTRUE);
excitation_energy_12c_from_3alpha();
((TCanvas*)gROOT->FindObject("c"))->SaveAs("chapter4_figures/mass_c12.png");
missing_mass_excitation_energy_be8();
((TCanvas*)gROOT->FindObject("c"))->SaveAs("chapter4_figures/mass_missing_pairs.png");
dalitz_plot_3alpha();
((TCanvas*)gROOT->FindObject("c1"))->Draw();
((TCanvas*)gROOT->FindObject("c1"))->SaveAs("chapter4_figures/mass_dalitz_direct.png");
((TCanvas*)gROOT->FindObject("c2"))->Draw();
((TCanvas*)gROOT->FindObject("c2"))->SaveAs("chapter4_figures/mass_dalitz_sequential.png");
}
