//////////////////////////////////////////////////////////
// This class has been automatically generated on
// Sun Sep 13 09:58:30 2026 by ROOT version 6.40.02
// from TTree tree/tree must2
// found on file: run0005.root
//////////////////////////////////////////////////////////

#ifndef ppac_h
#define ppac_h

#include <TROOT.h>
#include <TChain.h>
#include <TFile.h>

// Header file for the classes stored in the TTree if any.

class ppac {
public :
   TTree          *fChain;   ///<!pointer to the analyzed TTree or TChain
   Int_t           fCurrent; ///<!current Tree number in a TChain

// Fixed size dimensions of array or collections stored in the TTree if any.

   // Declaration of leaf types
   Int_t           beamTrig;
   Int_t           must2Trig[8];
   Float_t         PPACF5[5][5];
   Float_t         PPACF8[5][5];
   Float_t         PPACF9[5][5];
   Float_t         FPPosition[12][4];
   Float_t         F5PPACRawData[5][10];
   Float_t         F8PPACRawData[5][10];
   Float_t         F9PPACRawData[5][10];
   Float_t         F10PPACRawData[5][10];
   Float_t         F11PPACRawData[5][10];
   Float_t         F3PlaRawData[4];
   Float_t         F7PlaRawData[4];
   Float_t         F11PlaRawData[4];
   Float_t         F11ICRawData[10];
   Float_t         TOF[8];
   Float_t         AoQ[9][4];

   // List of branches
   TBranch        *b_beamTrig;   ///<!
   TBranch        *b_must2Trig;   ///<!
   TBranch        *b_PPACF5;   ///<!
   TBranch        *b_PPACF8;   ///<!
   TBranch        *b_PPACF9;   ///<!
   TBranch        *b_FPPosition;   ///<!
   TBranch        *b_F5PPACRawData;   ///<!
   TBranch        *b_F8PPACRawData;   ///<!
   TBranch        *b_F9PPACRawData;   ///<!
   TBranch        *b_F10PPACRawData;   ///<!
   TBranch        *b_F11PPACRawData;   ///<!
   TBranch        *b_F3PlaRawData;   ///<!
   TBranch        *b_F7PlaRawData;   ///<!
   TBranch        *b_F11PlaRawData;   ///<!
   TBranch        *b_F11ICRawData;   ///<!
   TBranch        *b_TOF;   ///<!
   TBranch        *b_AoQ;   ///<!

   ppac(TTree *tree=0);
   virtual ~ppac();
   virtual Int_t    Cut(Long64_t entry);
   virtual Int_t    GetEntry(Long64_t entry);
   virtual Long64_t LoadTree(Long64_t entry);
   virtual void     Init(TTree *tree);
   virtual void     Loop();
   virtual bool     Notify();
   virtual void     Show(Long64_t entry = -1);
};

#endif

#ifdef ppac_cxx
ppac::ppac(TTree *tree) : fChain(0)
{
// if parameter tree is not specified (or zero), connect the file
// used to generate this class and read the Tree.
   if (tree == 0) {
      TFile *f = (TFile*)gROOT->GetListOfFiles()->FindObject("run0005.root");
      if (!f || !f->IsOpen()) {
         f = new TFile("run0005.root");
      }
      f->GetObject("tree",tree);

   }
   Init(tree);
}

ppac::~ppac()
{
   if (!fChain) return;
   delete fChain->GetCurrentFile();
}

Int_t ppac::GetEntry(Long64_t entry)
{
// Read contents of entry.
   if (!fChain) return 0;
   return fChain->GetEntry(entry);
}
Long64_t ppac::LoadTree(Long64_t entry)
{
// Set the environment to read one entry
   if (!fChain) return -5;
   Long64_t centry = fChain->LoadTree(entry);
   if (centry < 0) return centry;
   if (fChain->GetTreeNumber() != fCurrent) {
      fCurrent = fChain->GetTreeNumber();
      Notify();
   }
   return centry;
}

void ppac::Init(TTree *tree)
{
   // The Init() function is called when the selector needs to initialize
   // a new tree or chain. Typically here the branch addresses and branch
   // pointers of the tree will be set.
   // It is normally not necessary to make changes to the generated
   // code, but the routine can be extended by the user if needed.

   // Set branch addresses and branch pointers
   if (!tree) return;
   fChain = tree;
   fCurrent = -1;
   fChain->SetMakeClass(1);

   fChain->SetBranchAddress("beamTrig", &beamTrig, &b_beamTrig);
   fChain->SetBranchAddress("must2Trig", must2Trig, &b_must2Trig);
   fChain->SetBranchAddress("PPACF5", PPACF5, &b_PPACF5);
   fChain->SetBranchAddress("PPACF8", PPACF8, &b_PPACF8);
   fChain->SetBranchAddress("PPACF9", PPACF9, &b_PPACF9);
   fChain->SetBranchAddress("FPPosition", FPPosition, &b_FPPosition);
   fChain->SetBranchAddress("F5PPACRawData", F5PPACRawData, &b_F5PPACRawData);
   fChain->SetBranchAddress("F8PPACRawData", F8PPACRawData, &b_F8PPACRawData);
   fChain->SetBranchAddress("F9PPACRawData", F9PPACRawData, &b_F9PPACRawData);
   fChain->SetBranchAddress("F10PPACRawData", F10PPACRawData, &b_F10PPACRawData);
   fChain->SetBranchAddress("F11PPACRawData", F11PPACRawData, &b_F11PPACRawData);
   fChain->SetBranchAddress("F3PlaRawData", F3PlaRawData, &b_F3PlaRawData);
   fChain->SetBranchAddress("F7PlaRawData", F7PlaRawData, &b_F7PlaRawData);
   fChain->SetBranchAddress("F11PlaRawData", F11PlaRawData, &b_F11PlaRawData);
   fChain->SetBranchAddress("F11ICRawData", F11ICRawData, &b_F11ICRawData);
   fChain->SetBranchAddress("TOF", TOF, &b_TOF);
   fChain->SetBranchAddress("AoQ", AoQ, &b_AoQ);
   Notify();
}

bool ppac::Notify()
{
   // The Notify() function is called when a new file is opened. This
   // can be for a new TTree in a TChain. It is normally not necessary to make changes
   // to the generated code, but the routine can be extended by the
   // user if needed. The return value is currently not used.

   return true;
}

void ppac::Show(Long64_t entry)
{
// Print contents of entry.
// If entry is not specified, print current entry
   if (!fChain) return;
   fChain->Show(entry);
}
Int_t ppac::Cut(Long64_t entry)
{
// This function may be called from Loop.
// returns  1 if entry is accepted.
// returns -1 otherwise.
   return 1;
}
#endif // #ifdef ppac_cxx
