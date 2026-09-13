//////////////////////////////////////////////////////////
// This class has been automatically generated on
// Sun Sep 13 09:54:23 2026 by ROOT version 6.40.02
// from TTree tree/tree
// found on file: /Users/zhli/Desktop/course/code-new/data/chapt2/f8ppac001.root
//////////////////////////////////////////////////////////

#ifndef tracking_h
#define tracking_h

#include <TROOT.h>
#include <TH2.h>
#include <TChain.h>
#include <TFile.h>

// Header file for the classes stored in the TTree if any.

class tracking {
public :
   Double_t xx[3], xz[3], yy[3], yz[3], dx[3], dy[3];
   Double_t xx2b[2], yy2b[2], xz2b, yz2b, anode2b;
   Double_t tx,ty,theta_x,theta_y,sigma_tx,sigma_ty,sigma_thetax,sigma_thetay,c2nx,c2ny;
   Long64_t source_entry;
   void SetBranch(TTree *tree);
   void TrackInit();
   void SetTrace(TH2D *h, Double_t k, Double_t b, Int_t min, Int_t max);

   TTree          *fChain;   ///<!pointer to the analyzed TTree or TChain
   Int_t           fCurrent; ///<!current Tree number in a TChain

// Fixed size dimensions of array or collections stored in the TTree if any.

   // Declaration of leaf types
   Float_t         PPACF8[5][5];
   Float_t         F8PPACRawData[5][5];
   Int_t           beamTrig;
   Int_t           must2Trig;
   Float_t         targetX;
   Float_t         targetY;

   // List of branches
   TBranch        *b_PPACF8;   ///<!
   TBranch        *b_F8PPACRawData;   ///<!
   TBranch        *b_beamTrig;   ///<!
   TBranch        *b_must2Trig;   ///<!
   TBranch        *b_targetX;   ///<!
   TBranch        *b_targetY;   ///<!

   tracking(TTree *tree=0);
   virtual ~tracking();
   virtual Int_t    Cut(Long64_t entry);
   virtual Int_t    GetEntry(Long64_t entry);
   virtual Long64_t LoadTree(Long64_t entry);
   virtual void     Init(TTree *tree);
   virtual void     Loop(TTree *tree);
   virtual bool     Notify();
   virtual void     Show(Long64_t entry = -1);
};

#endif

#ifdef tracking_cxx
tracking::tracking(TTree *tree) : fChain(0)
{
// if parameter tree is not specified (or zero), connect the file
// used to generate this class and read the Tree.
   if (tree == 0) {
      TFile *f = (TFile*)gROOT->GetListOfFiles()->FindObject("../../f8ppac001.root");
      if (!f || !f->IsOpen()) {
         f = new TFile("../../f8ppac001.root");
      }
      f->GetObject("tree",tree);

   }
   Init(tree);
}

tracking::~tracking()
{
   if (!fChain) return;
   delete fChain->GetCurrentFile();
}

Int_t tracking::GetEntry(Long64_t entry)
{
// Read contents of entry.
   if (!fChain) return 0;
   return fChain->GetEntry(entry);
}
Long64_t tracking::LoadTree(Long64_t entry)
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

void tracking::Init(TTree *tree)
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

   fChain->SetBranchAddress("PPACF8", PPACF8, &b_PPACF8);
   fChain->SetBranchAddress("F8PPACRawData", F8PPACRawData, &b_F8PPACRawData);
   fChain->SetBranchAddress("beamTrig", &beamTrig, &b_beamTrig);
   fChain->SetBranchAddress("must2Trig", &must2Trig, &b_must2Trig);
   fChain->SetBranchAddress("targetX", &targetX, &b_targetX);
   fChain->SetBranchAddress("targetY", &targetY, &b_targetY);
   Notify();
}

bool tracking::Notify()
{
   // The Notify() function is called when a new file is opened. This
   // can be for a new TTree in a TChain. It is normally not necessary to make changes
   // to the generated code, but the routine can be extended by the
   // user if needed. The return value is currently not used.

   return true;
}

void tracking::Show(Long64_t entry)
{
// Print contents of entry.
// If entry is not specified, print current entry
   if (!fChain) return;
   fChain->Show(entry);
}
Int_t tracking::Cut(Long64_t entry)
{
// This function may be called from Loop.
// returns  1 if entry is accepted.
// returns -1 otherwise.
   return 1;
}
#endif // #ifdef tracking_cxx
