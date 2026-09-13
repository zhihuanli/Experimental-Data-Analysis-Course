#include <TSpectrum.h>
#include <TH1.h>
#include <TROOT.h>
#include <TPolyMarker.h>
#include <TLatex.h>
#include <TString.h>
#include <map>
#include <vector>
#include <iostream>
using namespace std;
TH1 *h = nullptr, *hb = nullptr;

void peaks(TString hname, vector<Double_t> &pe, Double_t thres=0.05, int backsub=1)
{
  Int_t nfound;
  Double_t *xpeaks = NULL, *ypeaks = NULL;
  pe.clear();

  multimap<Double_t, Double_t> me;   // key: ypeaks, value: xpeaks

  TH1 *source = dynamic_cast<TH1*>(gROOT->FindObject(hname));
  h = source ? static_cast<TH1*>(source->Clone(hname+"_search")) : nullptr;
  if(!h) {
    cout << "Histogram " << hname << " not found." << endl;
    return;
  }

  TSpectrum *sp = new TSpectrum(500);

  if(backsub) {
    hb = (TH1F*)sp->Background(h, 80);
    h->Add(hb, -1);
  }

  nfound = sp->Search(h, 2, "", thres);

  TPolyMarker *pm = (TPolyMarker*)h->GetListOfFunctions()->FindObject("TPolyMarker");
  if(pm) {
    pm->SetMarkerStyle(32);
    pm->SetMarkerColor(kGreen);
    pm->SetMarkerSize(0.4);
  }

  xpeaks = sp->GetPositionX();
  ypeaks = sp->GetPositionY();

  for(int j=0; j<nfound; j++) {
    me.emplace(ypeaks[j], xpeaks[j]);

    TLatex *tex = new TLatex(xpeaks[j], ypeaks[j], Form("%.0f", xpeaks[j]));
    tex->SetTextFont(13);
    tex->SetTextSize(0.02);
    tex->SetTextAlign(12);
    tex->SetTextAngle(90);
    tex->SetTextColor(kRed);
    tex->Draw();
  }

  for(auto ie = me.rbegin(); ie != me.rend(); ++ie) {
    cout << ie->second << " " << ie->first << endl;
    pe.push_back(ie->second);
  }

  delete sp;
}

