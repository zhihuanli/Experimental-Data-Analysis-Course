#define ppac_cxx
#include "ppac.h"
#include <TH2.h>
#include <TStyle.h>
#include <TCanvas.h>

TH1D *h1 = new TH1D("h1", "h1", 2000, 0, 2000);
void ppac::Loop()
{
  if (!fChain) return;
  //new tree and root file
  TFile *opf = new TFile("ppac_demo.root", "recreate");
  TTree *tree = new TTree("tree", "ppac");

  Double_t txl, txr, tyd, tyu, ta;
  Double_t x, y;
  tree->Branch("txl", &txl, "txl/D");
  tree->Branch("txr", &txr, "txr/D");
  tree->Branch("tyd", &tyd, "tyd/D");
  tree->Branch("tyu", &tyu, "tyu/D");
  tree->Branch("ta",  &ta,  "ta/D");
  tree->Branch("x",   &x,   "x/D");
  tree->Branch("y",   &y,   "y/D");

    //TTree *fChain - Pointer pointing to the tree
   if (fChain == 0) return;

   Long64_t nentries = fChain->GetEntriesFast();

   Long64_t nbytes = 0, nb = 0;
   for (Long64_t jentry = 0; jentry < nentries; jentry++) {
      Long64_t ientry = LoadTree(jentry);
      if (ientry < 0) break;
      nb = fChain->GetEntry(jentry);   nbytes += nb;

     //user code
     h1->Fill(F8PPACRawData[0][1] + F8PPACRawData[0][0] - 2*F8PPACRawData[0][4]);

     txl = F8PPACRawData[0][0];
     txr = F8PPACRawData[0][1];
     tyd = F8PPACRawData[0][2];
     tyu = F8PPACRawData[0][3];
     ta = F8PPACRawData[0][4];

     bool bx = txl>0 && txr>0 && txl<4900 && txr<4900;
     bool by = tyu>0 && tyd>0 && tyu<4900 && tyd<4900;
     bool ba = ta<600 && ta>250;

     x =- 5000;
     y =- 5000;
     if(bx && by && ba) {
         x = txr - txl;
         y = tyu - tyd;
         tree->Fill();
     }
        if(jentry%100000 == 0) cout << "processing " << jentry << endl;
   }
    cout << "Input=" << nentries << ", selected=" << tree->GetEntries() << endl;
    tree->Write();
    opf->Close();
}

