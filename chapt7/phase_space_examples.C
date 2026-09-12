// Section 4.2: run from the directory containing the input ROOT files.
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

#include "TFile.h"
#include "TTree.h"
#include "TGenPhaseSpace.h"
#include "TLorentzVector.h"
#include "TVector3.h"
#include "TMath.h"
#include "TRandom3.h"
#include "TCanvas.h"
#include "TH1D.h"
#include "TH2D.h"
#include "TStyle.h"

#include <iostream>
#include <cmath>

double PhiDeg(const TLorentzVector &p)
{
    double phi = p.Phi() * TMath::RadToDeg();
    if (phi < 0.0) phi += 360.0;
    return phi;
}

void gen_direct_3alpha(Long64_t N = 500000)
{
    // ------------------------------------------------------------
    // Units:
    //   internal calculation: GeV
    //   stored kinetic energy: MeV
    //   stored angles: degree
    //
    // Reaction:
    //   p + 11B -> 12C*(16.62 MeV, 2-) -> alpha + alpha + alpha
    //
    // The three alpha particles are stored in the order returned by
    // TGenPhaseSpace. No event-by-event reordering is applied.
    // ------------------------------------------------------------

    gRandom->SetSeed(4201); // reproducible phase-space sequence

    const double mp     = 0.9382720813;  // GeV
    const double mAlpha = 3.727379378;   // GeV

    // 12C*(16.62 MeV), Q value relative to 3-alpha threshold
    const double Q3a   = 0.009345;       // GeV
    const double mC12s = 3.0 * mAlpha + Q3a;

    // Moving frame corresponding to proton beam energy Ep = 0.675 MeV
    const double Tp    = 0.000675;       // GeV
    const double pBeam = std::sqrt(Tp * (Tp + 2.0 * mp));
    const double EMove = std::sqrt(mC12s * mC12s + pBeam * pBeam);

    TVector3 betaMove(0.0, 0.0, pBeam / EMove);

    // 12C* rest frame
    TLorentzVector C12_rest(0.0, 0.0, 0.0, mC12s);

    TGenPhaseSpace gen;
    double masses[3] = {mAlpha, mAlpha, mAlpha};

    if (!gen.SetDecay(C12_rest, 3, masses)) {
        std::cerr << "SetDecay failed for direct decay." << std::endl;
        return;
    }

    TFile *fout = new TFile("direct_3alpha.root", "RECREATE");
    TTree *tree = new TTree("events", "Direct 3alpha decay");

    double T_rest[3], theta_rest[3], phi_rest[3];
    double T_move[3], theta_move[3], phi_move[3];
    double weight;

    tree->Branch("T_rest",     T_rest,     "T_rest[3]/D");
    tree->Branch("theta_rest", theta_rest, "theta_rest[3]/D");
    tree->Branch("phi_rest",   phi_rest,   "phi_rest[3]/D");

    tree->Branch("T_move",     T_move,     "T_move[3]/D");
    tree->Branch("theta_move", theta_move, "theta_move[3]/D");
    tree->Branch("phi_move",   phi_move,   "phi_move[3]/D");

    tree->Branch("weight",     &weight,    "weight/D");

    for (Long64_t iev = 0; iev < N; ++iev) {

        weight = gen.Generate();

        for (int i = 0; i < 3; ++i) {

            TLorentzVector aRest = *gen.GetDecay(i);

            // In 12C* rest frame
            T_rest[i]     = (aRest.E() - mAlpha) * 1000.0;
            theta_rest[i] = aRest.Theta() * TMath::RadToDeg();
            phi_rest[i]   = PhiDeg(aRest);

            // In moving frame
            TLorentzVector aMove = aRest;
            aMove.Boost(betaMove);

            T_move[i]     = (aMove.E() - mAlpha) * 1000.0;
            theta_move[i] = aMove.Theta() * TMath::RadToDeg();
            phi_move[i]   = PhiDeg(aMove);
        }

        tree->Fill();
    }

    tree->Write();
    fout->Close();

    std::cout << "Wrote direct_3alpha.root with " << N << " events." << std::endl;
}

void gen_sequential_3alpha(Long64_t N = 500000)
{
    // ------------------------------------------------------------
    // Units:
    //   internal calculation: GeV
    //   stored kinetic energy: MeV
    //   stored angles: degree
    //
    // Reaction:
    //   p + 11B -> 12C*(16.62 MeV, 2-)
    //             -> alpha0 + 8Be(2+)
    //             -> alpha0 + alpha1 + alpha2
    //
    // alpha[0] = primary alpha from 12C* decay
    // alpha[1], alpha[2] = two alphas from 8Be decay
    //
    // Randomly permute the final labels before storing the event.
    // ------------------------------------------------------------

    const double mp     = 0.9382720813;  // GeV
    const double mAlpha = 3.727379378;   // GeV

    // 12C*(16.62 MeV), Q value relative to 3-alpha threshold
    const double Q3a   = 0.009345;       // GeV
    const double mC12s = 3.0 * mAlpha + Q3a;

    // Moving frame corresponding to proton beam energy Ep = 0.675 MeV
    const double Tp    = 0.000675;       // GeV
    const double pBeam = std::sqrt(Tp * (Tp + 2.0 * mp));
    const double EMove = std::sqrt(mC12s * mC12s + pBeam * pBeam);

    TVector3 betaMove(0.0, 0.0, pBeam / EMove);

    // 8Be(2+) parameters
    const double E8gs_above_2a = 0.00009184;  // GeV
    const double Ex8_2plus     = 0.003030;    // GeV
    const double Gamma8_2plus  = 0.001513;    // GeV

    const double m8_mean = 2.0 * mAlpha + E8gs_above_2a + Ex8_2plus;
    const double m8_min  = 2.0 * mAlpha;
    const double m8_max  = mC12s - mAlpha;

    TLorentzVector C12_rest(0.0, 0.0, 0.0, mC12s);

    TGenPhaseSpace gen1;
    TGenPhaseSpace gen2;
    TRandom3 rng(4202); // intermediate mass and label permutation
    gRandom->SetSeed(4203); // TGenPhaseSpace uses gRandom

    TFile *fout = new TFile("sequential_3alpha.root", "RECREATE");
    TTree *tree = new TTree("events", "Sequential 3alpha decay");

    double T_rest[3], theta_rest[3], phi_rest[3];
    double T_move[3], theta_move[3], phi_move[3];
    double weight;

    tree->Branch("T_rest",     T_rest,     "T_rest[3]/D");
    tree->Branch("theta_rest", theta_rest, "theta_rest[3]/D");
    tree->Branch("phi_rest",   phi_rest,   "phi_rest[3]/D");

    tree->Branch("T_move",     T_move,     "T_move[3]/D");
    tree->Branch("theta_move", theta_move, "theta_move[3]/D");
    tree->Branch("phi_move",   phi_move,   "phi_move[3]/D");

    tree->Branch("weight",     &weight,    "weight/D");

    for (Long64_t iev = 0; iev < N; ++iev) {

        // Sample 8Be(2+) mass with a truncated Breit-Wigner distribution
        double m8 = 0.0;

        while (true) {
            double u = rng.Uniform();
            m8 = m8_mean + 0.5 * Gamma8_2plus * std::tan(TMath::Pi() * (u - 0.5));

            if (m8 > m8_min && m8 < m8_max) break;
        }

        // First decay:
        // 12C* -> alpha0 + 8Be
        double masses1[2] = {mAlpha, m8};

        if (!gen1.SetDecay(C12_rest, 2, masses1)) {
            --iev;
            continue;
        }

        double w1 = gen1.Generate();

        TLorentzVector alpha[3];

        alpha[0] = *gen1.GetDecay(0);
        TLorentzVector be8 = *gen1.GetDecay(1);

        // Second decay:
        // 8Be -> alpha1 + alpha2
        double masses2[2] = {mAlpha, mAlpha};

        if (!gen2.SetDecay(be8, 2, masses2)) {
            --iev;
            continue;
        }

        double w2 = gen2.Generate();

        alpha[1] = *gen2.GetDecay(0);
        alpha[2] = *gen2.GetDecay(1);

        weight = w1 * w2;
        // --------------------------------------------------------
        // Random permutation to erase generator labels
        // --------------------------------------------------------
        for (int k = 2; k > 0; --k) {
            int j = int(rng.Uniform() * (k + 1));
            TLorentzVector tmp = alpha[k];
            alpha[k] = alpha[j];
            alpha[j] = tmp;
        }

        for (int i = 0; i < 3; ++i) {

            TLorentzVector aRest = alpha[i];

            // In 12C* rest frame
            T_rest[i]     = (aRest.E() - mAlpha) * 1000.0;
            theta_rest[i] = aRest.Theta() * TMath::RadToDeg();
            phi_rest[i]   = PhiDeg(aRest);

            // In moving frame
            TLorentzVector aMove = aRest;
            aMove.Boost(betaMove);

            T_move[i]     = (aMove.E() - mAlpha) * 1000.0;
            theta_move[i] = aMove.Theta() * TMath::RadToDeg();
            phi_move[i]   = PhiDeg(aMove);
        }

        tree->Fill();
    }

    tree->Write();
    fout->Close();

    std::cout << "Wrote sequential_3alpha.root with " << N << " events." << std::endl;
}

TCanvas *c = nullptr;

void plot_3alpha_correlations(const char *filename, const char *tag)
{
    TFile *fin = TFile::Open(filename);
    if (!fin || fin->IsZombie()) throw std::runtime_error("Cannot open input ROOT file");
    TTree *tree = fin->Get<TTree>("events");
    if (!tree) throw std::runtime_error("Missing events tree");

    gStyle->SetOptStat(0);
    gStyle->SetPadLeftMargin(0.15);
    gStyle->SetPadRightMargin(0.14);

    if (c) {
        delete c;
        c = nullptr;
    }

    c = new TCanvas("c", "c", 900, 450);

    c->Divide(2, 1);

    c->cd(1);
    gPad->SetRightMargin(0.14);

    TH2D *h_rest_01 = new TH2D(
        Form("h_rest_01_%s", tag),
        Form("%s: rest frame [0]-[1];T_{0} (MeV);T_{1} (MeV)", tag), 260, 0.0, 9, 260, 0.0, 9);

    tree->Draw(
        Form("T_rest[1]:T_rest[0]>>h_rest_01_%s", tag), "weight", "colz");


    c->cd(2);
    gPad->SetRightMargin(0.14);

    TH2D *h_move_01 = new TH2D(
        Form("h_move_01_%s", tag),
        Form("%s: moving frame [0]-[1];T_{0} (MeV);T_{1} (MeV)", tag), 260, 0.0, 9, 260, 0.0, 9);

    tree->Draw(
        Form("T_move[1]:T_move[0]>>h_move_01_%s", tag), "weight", "colz");


    c->Draw();
}

void plot_all_alpha_spectra(const char *filename, const char *tag)
{
    TFile *fin = TFile::Open(filename);
    if (!fin || fin->IsZombie()) throw std::runtime_error("Cannot open input ROOT file");
    TTree *tree = fin->Get<TTree>("events");
    if (!tree) throw std::runtime_error("Missing events tree");

    gStyle->SetOptStat(0);
    gStyle->SetPadLeftMargin(0.15);
    gStyle->SetPadRightMargin(0.14);

    if (c) {
        delete c;
        c = nullptr;
    }

    c = new TCanvas("c", "c", 900, 450);

    c->Divide(2, 1);

    c->cd(1);

    TH1D *h_rest = new TH1D(
        Form("h_all_rest_%s", tag),
        Form("%s: all alpha, rest frame;T_{#alpha} (MeV);Sum of weights", tag), 260, 0.0, 9);

    tree->Draw(Form("T_rest>>h_all_rest_%s", tag),  "weight", "hist");
    h_rest->Draw("hist");

    c->cd(2);

    TH1D *h_move = new TH1D(
        Form("h_all_move_%s", tag),
        Form("%s: all alpha, moving frame;T_{#alpha} (MeV);Sum of weights", tag), 260, 0.0, 9);

    tree->Draw(Form("T_move>>h_all_move_%s", tag),  "weight", "hist");
    h_move->Draw("hist");

    c->Draw();
}

void phase_space_examples()
{
gROOT->SetBatch(kTRUE);
gStyle->SetOptStat(0);
gSystem->mkdir("chapter4_figures", kTRUE);
gen_direct_3alpha();
gen_sequential_3alpha();
plot_all_alpha_spectra("direct_3alpha.root", "Direct");
((TCanvas*)gROOT->FindObject("c"))->SaveAs("chapter4_figures/phase_direct_energy.png");
plot_all_alpha_spectra("sequential_3alpha.root", "Sequential");
((TCanvas*)gROOT->FindObject("c"))->SaveAs("chapter4_figures/phase_sequential_energy.png");
plot_3alpha_correlations("direct_3alpha.root", "Direct");
((TCanvas*)gROOT->FindObject("c"))->SaveAs("chapter4_figures/phase_direct_correlation.png");
plot_3alpha_correlations("sequential_3alpha.root", "Sequential");
((TCanvas*)gROOT->FindObject("c"))->SaveAs("chapter4_figures/phase_sequential_correlation.png");
}
