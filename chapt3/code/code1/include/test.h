//////////////////////////////////////////////////////////
// This class has been automatically generated on
// Sat Jun 19 17:41:36 2021 by ROOT version 6.20/00
// from TTree tree/tree
// found on file: cal_16C.root
//////////////////////////////////////////////////////////

#ifndef test_h
#define test_h

#include <TROOT.h>
#include <TChain.h>
#include <TFile.h>

// Header file for the classes stored in the TTree if any.

class test {
public :
   TTree          *fChain;   //!pointer to the analyzed TTree or TChain
   Int_t           fCurrent; //!current Tree number in a TChain

// Fixed size dimensions of array or collections stored in the TTree if any.

   // Declaration of leaf types
   Double_t        d1x[32];
   Double_t        d1y[32];
   Double_t        d2x[32];
   Double_t        d2y[32];
   Double_t        d3x[32];
   Double_t        d3y[32];
   Int_t           x1hit;
   Double_t        x1e[13];   //[x1hit]
   Int_t           x1s[13];   //[x1hit]
   Double_t        sx1e;
   Int_t           y1hit;
   Double_t        y1e[13];   //[y1hit]
   Int_t           y1s[13];   //[y1hit]
   Double_t        sy1e;
   Int_t           x2hit;
   Double_t        x2e[8];   //[x2hit]
   Int_t           x2s[8];   //[x2hit]
   Double_t        sx2e;
   Int_t           y2hit;
   Double_t        y2e[8];   //[y2hit]
   Int_t           y2s[8];   //[y2hit]
   Double_t        sy2e;
   Int_t           x3hit;
   Double_t        x3e[6];   //[x3hit]
   Int_t           x3s[6];   //[x3hit]
   Double_t        sx3e;
   Int_t           y3hit;
   Double_t        y3e[8];   //[y3hit]
   Int_t           y3s[8];   //[y3hit]
   Double_t        sy3e;
   Double_t        d1z;
   Double_t        d2z;
   Double_t        d3z;
   Double_t        s1e;
   Double_t        s2e;
   Double_t        s3e;
   Double_t        c1e;
   Double_t        c2e;
   Double_t        c3e;
   Double_t        c4e;
   Double_t        tx;
   Double_t        ty;
   Double_t        tz;

   // List of branches
   TBranch        *b_d1x;   //!
   TBranch        *b_d1y;   //!
   TBranch        *b_d2x;   //!
   TBranch        *b_d2y;   //!
   TBranch        *b_d3x;   //!
   TBranch        *b_d3y;   //!
   TBranch        *b_x1hit;   //!
   TBranch        *b_x1e;   //!
   TBranch        *b_x1s;   //!
   TBranch        *b_sx1e;   //!
   TBranch        *b_y1hit;   //!
   TBranch        *b_y1e;   //!
   TBranch        *b_y1s;   //!
   TBranch        *b_sy1e;   //!
   TBranch        *b_x2hit;   //!
   TBranch        *b_x2e;   //!
   TBranch        *b_x2s;   //!
   TBranch        *b_sx2e;   //!
   TBranch        *b_y2hit;   //!
   TBranch        *b_y2e;   //!
   TBranch        *b_y2s;   //!
   TBranch        *b_sy2e;   //!
   TBranch        *b_x3hit;   //!
   TBranch        *b_x3e;   //!
   TBranch        *b_x3s;   //!
   TBranch        *b_sx3e;   //!
   TBranch        *b_y3hit;   //!
   TBranch        *b_y3e;   //!
   TBranch        *b_y3s;   //!
   TBranch        *b_sy3e;   //!
   TBranch        *b_d1z;   //!
   TBranch        *b_d2z;   //!
   TBranch        *b_d3z;   //!
   TBranch        *b_s1e;   //!
   TBranch        *b_s2e;   //!
   TBranch        *b_s3e;   //!
   TBranch        *b_c1e;   //!
   TBranch        *b_c2e;   //!
   TBranch        *b_c3e;   //!
   TBranch        *b_c4e;   //!
   TBranch        *b_tx;   //!
   TBranch        *b_ty;   //!
   TBranch        *b_tz;   //!

   test(TTree *tree=0);
   virtual ~test();
   virtual Int_t    Cut(Long64_t entry);
   virtual Int_t    GetEntry(Long64_t entry);
   virtual Long64_t LoadTree(Long64_t entry);
   virtual void     Init(TTree *tree);
   virtual void     Loop();
   virtual Bool_t   Notify();
   virtual void     Show(Long64_t entry = -1);
};

#endif

#ifdef test_cxx
test::test(TTree *tree) : fChain(0) 
{
// if parameter tree is not specified (or zero), connect the file
// used to generate this class and read the Tree.
   if (tree == 0) {
      TFile *f = (TFile*)gROOT->GetListOfFiles()->FindObject("cal_16C.root");
      if (!f || !f->IsOpen()) {
         f = new TFile("cal_16C.root");
      }
      f->GetObject("tree",tree);

   }
   Init(tree);
}

test::~test()
{
   if (!fChain) return;
   delete fChain->GetCurrentFile();
}

Int_t test::GetEntry(Long64_t entry)
{
// Read contents of entry.
   if (!fChain) return 0;
   return fChain->GetEntry(entry);
}
Long64_t test::LoadTree(Long64_t entry)
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

void test::Init(TTree *tree)
{
   // The Init() function is called when the selector needs to initialize
   // a new tree or chain. Typically here the branch addresses and branch
   // pointers of the tree will be set.
   // It is normally not necessary to make changes to the generated
   // code, but the routine can be extended by the user if needed.
   // Init() will be called many times when running on PROOF
   // (once per file to be processed).

   // Set branch addresses and branch pointers
   if (!tree) return;
   fChain = tree;
   fCurrent = -1;
   fChain->SetMakeClass(1);

   fChain->SetBranchAddress("d1x", d1x, &b_d1x);
   fChain->SetBranchAddress("d1y", d1y, &b_d1y);
   fChain->SetBranchAddress("d2x", d2x, &b_d2x);
   fChain->SetBranchAddress("d2y", d2y, &b_d2y);
   fChain->SetBranchAddress("d3x", d3x, &b_d3x);
   fChain->SetBranchAddress("d3y", d3y, &b_d3y);
   fChain->SetBranchAddress("x1hit", &x1hit, &b_x1hit);
   fChain->SetBranchAddress("x1e", x1e, &b_x1e);
   fChain->SetBranchAddress("x1s", x1s, &b_x1s);
   fChain->SetBranchAddress("sx1e", &sx1e, &b_sx1e);
   fChain->SetBranchAddress("y1hit", &y1hit, &b_y1hit);
   fChain->SetBranchAddress("y1e", y1e, &b_y1e);
   fChain->SetBranchAddress("y1s", y1s, &b_y1s);
   fChain->SetBranchAddress("sy1e", &sy1e, &b_sy1e);
   fChain->SetBranchAddress("x2hit", &x2hit, &b_x2hit);
   fChain->SetBranchAddress("x2e", x2e, &b_x2e);
   fChain->SetBranchAddress("x2s", x2s, &b_x2s);
   fChain->SetBranchAddress("sx2e", &sx2e, &b_sx2e);
   fChain->SetBranchAddress("y2hit", &y2hit, &b_y2hit);
   fChain->SetBranchAddress("y2e", y2e, &b_y2e);
   fChain->SetBranchAddress("y2s", y2s, &b_y2s);
   fChain->SetBranchAddress("sy2e", &sy2e, &b_sy2e);
   fChain->SetBranchAddress("x3hit", &x3hit, &b_x3hit);
   fChain->SetBranchAddress("x3e", x3e, &b_x3e);
   fChain->SetBranchAddress("x3s", x3s, &b_x3s);
   fChain->SetBranchAddress("sx3e", &sx3e, &b_sx3e);
   fChain->SetBranchAddress("y3hit", &y3hit, &b_y3hit);
   fChain->SetBranchAddress("y3e", y3e, &b_y3e);
   fChain->SetBranchAddress("y3s", y3s, &b_y3s);
   fChain->SetBranchAddress("sy3e", &sy3e, &b_sy3e);
   fChain->SetBranchAddress("d1z", &d1z, &b_d1z);
   fChain->SetBranchAddress("d2z", &d2z, &b_d2z);
   fChain->SetBranchAddress("d3z", &d3z, &b_d3z);
   fChain->SetBranchAddress("s1e", &s1e, &b_s1e);
   fChain->SetBranchAddress("s2e", &s2e, &b_s2e);
   fChain->SetBranchAddress("s3e", &s3e, &b_s3e);
   fChain->SetBranchAddress("c1e", &c1e, &b_c1e);
   fChain->SetBranchAddress("c2e", &c2e, &b_c2e);
   fChain->SetBranchAddress("c3e", &c3e, &b_c3e);
   fChain->SetBranchAddress("c4e", &c4e, &b_c4e);
   fChain->SetBranchAddress("tx", &tx, &b_tx);
   fChain->SetBranchAddress("ty", &ty, &b_ty);
   fChain->SetBranchAddress("tz", &tz, &b_tz);
   Notify();
}

Bool_t test::Notify()
{
   // The Notify() function is called when a new file is opened. This
   // can be either for a new TTree in a TChain or when when a new TTree
   // is started when using PROOF. It is normally not necessary to make changes
   // to the generated code, but the routine can be extended by the
   // user if needed. The return value is currently not used.

   return kTRUE;
}

void test::Show(Long64_t entry)
{
// Print contents of entry.
// If entry is not specified, print current entry
   if (!fChain) return;
   fChain->Show(entry);
}
Int_t test::Cut(Long64_t entry)
{
// This function may be called from Loop.
// returns  1 if entry is accepted.
// returns -1 otherwise.
   return 1;
}
#endif // #ifdef test_cxx
