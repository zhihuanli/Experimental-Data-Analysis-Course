// Section 4.1: run from the directory containing the input ROOT files.
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



void kinematics_examples()
{
gROOT->SetBatch(kTRUE);
gStyle->SetOptStat(0);
gSystem->mkdir("chapter4_figures", kTRUE);
{
TVector3 p(0.3, 0.4, 1.2); // GeV

    std::cout << "px = " << p.X() << std::endl;
    std::cout << "py = " << p.Y() << std::endl;
    std::cout << "pz = " << p.Z() << std::endl;

    std::cout << "|p| = " << p.Mag() << " GeV" << std::endl;
    std::cout << "pT  = " << p.Perp() << " GeV" << std::endl;

    std::cout << "theta = "
              << p.Theta()*TMath::RadToDeg()
              << " deg" << std::endl;

    std::cout << "phi = "
              << p.Phi()*TMath::RadToDeg()
              << " deg" << std::endl;

    TVector3 dir = p.Unit();
    std::cout << "|dir| = " << dir.Mag()  << std::endl;
}
{
TVector3 p1(0.2, 0.1, 1.0);
    TVector3 p2(-0.1, 0.3, 0.8);

    double angle = p1.Angle(p2);

    std::cout << "opening angle = "
              << angle*TMath::RadToDeg()
              << " deg" << std::endl;

    std::cout << "p1 dot p2 = "
              << p1.Dot(p2)
              << std::endl;
}
{
TLorentzVector ks;
    ks.SetPxPyPzE(0.0, 0.0, 1.5142, 1.5939);

    std::cout << "E  = " << ks.E()  << " GeV" << std::endl;
    std::cout << "pz = " << ks.Pz() << " GeV" << std::endl;
    std::cout << "M  = " << ks.M()  << " GeV" << std::endl;
    std::cout << "beta  = " << ks.Beta()  << std::endl;
    std::cout << "gamma = " << ks.Gamma() << std::endl;
}
{
const double mpi = 0.13957; // GeV

    TLorentzVector pion;
    pion.SetXYZM(0.10, -0.05, 0.40, mpi);

    std::cout << "E = " << pion.E() << " GeV" << std::endl;
    std::cout << "M = " << pion.M() << " GeV" << std::endl;
}
{
const double mAlpha = 3727.38; // MeV
    const double T = 5.0;          // MeV

    double theta = 40.0*TMath::DegToRad();
    double phi   = 30.0*TMath::DegToRad();

    double E = T + mAlpha;
    double p = std::sqrt(T*T + 2.0*mAlpha*T);

    TVector3 pvec;
    pvec.SetMagThetaPhi(p, theta, phi);

    TLorentzVector alpha;
    alpha.SetPxPyPzE(pvec.X(), pvec.Y(), pvec.Z(), E);

    std::cout << "M = " << alpha.M() << " MeV" << std::endl;
}
{
const double mpi = 0.13957; // GeV

    TLorentzVector piPlus;
    TLorentzVector piMinus;

    piPlus.SetXYZM(0.20, 0.10, 0.50, mpi);
    piMinus.SetXYZM(-0.15, -0.05, 0.30, mpi);

    TLorentzVector pair_pi = piPlus + piMinus;

    std::cout << "M(pi+ pi-) = "
              << pair_pi.M()
              << " GeV" << std::endl;
}
{
// Parent four-vector in the lab frame
    const double M  = 1.0;   // GeV
    const double pz = 2.0;   // GeV

    TLorentzVector parent_lab;
    parent_lab.SetPxPyPzE(0.0, 0.0, pz, std::sqrt(M*M + pz*pz));

    // Velocity of the parent in the lab
    TVector3 beta = parent_lab.BoostVector();

    // Daughter four-vector in the parent rest frame
    const double md = 0.2;   // GeV
    const double px = 0.3;   // GeV

    TLorentzVector daughter_rest;
    daughter_rest.SetPxPyPzE(px, 0.0, 0.0, std::sqrt(md*md + px*px));

    // Boost from parent rest frame to lab frame
    TLorentzVector daughter_lab = daughter_rest;
    daughter_lab.Boost(beta);

    // Boost back from lab frame to parent rest frame
    TLorentzVector daughter_back = daughter_lab;
    daughter_back.Boost(-beta);

    std::cout << "Daughter in parent rest frame:\n";
    std::cout << "  E  = " << daughter_rest.E()  << "\n";
    std::cout << "  px = " << daughter_rest.Px() << "\n";
    std::cout << "  py = " << daughter_rest.Py() << "\n";
    std::cout << "  pz = " << daughter_rest.Pz() << "\n";
    std::cout << "  M  = " << daughter_rest.M()  << "\n\n";

    std::cout << "Daughter in lab frame:\n";
    std::cout << "  E  = " << daughter_lab.E()  << "\n";
    std::cout << "  px = " << daughter_lab.Px() << "\n";
    std::cout << "  py = " << daughter_lab.Py() << "\n";
    std::cout << "  pz = " << daughter_lab.Pz() << "\n";
    std::cout << "  M  = " << daughter_lab.M()  << "\n\n";

    std::cout << "Boosted back to parent rest frame:\n";
    std::cout << "  E  = " << daughter_back.E()  << "\n";
    std::cout << "  px = " << daughter_back.Px() << "\n";
    std::cout << "  py = " << daughter_back.Py() << "\n";
    std::cout << "  pz = " << daughter_back.Pz() << "\n";
    std::cout << "  M  = " << daughter_back.M()  << "\n";
}
{
// Parent four-vector in the lab frame
    TLorentzVector parent_lab;
    parent_lab.SetPxPyPzE(0.0, 0.0, 2.0, std::sqrt(5.0));

    // Daughter four-vector measured in the lab frame
    TLorentzVector daughter_lab;
    daughter_lab.SetXYZM(0.3, 0.0, 0.8, 0.2);

    // Velocity of the parent in the lab frame
    TVector3 beta = parent_lab.BoostVector();

    // Boost daughter from lab frame to parent rest frame
    TLorentzVector daughter_rest = daughter_lab;
    daughter_rest.Boost(-beta);

    std::cout << "daughter mass = "
              << daughter_rest.M()
              << " GeV" << std::endl;

    std::cout << "theta in parent rest frame = "
              << daughter_rest.Theta()*TMath::RadToDeg()
              << " deg" << std::endl;
}
}
