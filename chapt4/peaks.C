
TH1 *h=NULL,*hb=NULL;
Int_t nfound;
Double_t *xpeaks=NULL, *ypeaks=NULL;
TSpectrum *s=NULL;
void peaks(TString hname, Double_t thres=0.005,int backsub=0)
{
  h=dynamic_cast<TH1*>(gROOT->FindObject(hname));
  if (!h) throw std::runtime_error("Histogram not found");
  // 寻峰在副本上进行；保留输入谱的计数及 Sumw2 误差。
  TH1 *search=(TH1*)h->Clone(hname+"_search");
  search->SetDirectory(nullptr);
  if(!s) s=new TSpectrum(500);
  if(backsub) {
    hb=s->Background(search,80,"nosmoothing");
    search->Add(hb,-1);
    delete hb;
  }
  h->SetStats(0);
  h->SetFillColor(kCyan);
  nfound=s->Search(search,2,"goff",thres);
  h->Draw("hist");
  TPolyMarker *pm=(TPolyMarker *)
    search->GetListOfFunctions()->FindObject("TPolyMarker");
  if (pm) {
  pm->SetMarkerStyle(32);
  pm->SetMarkerColor(kGreen);
  pm->SetMarkerSize(0.4);
  }
  xpeaks=s->GetPositionX();
  ypeaks=s->GetPositionY();
  for(int j=0;j<nfound;j++) {
    stringstream ss;
    ss<<xpeaks[j];
    TString s1=ss.str();
    TLatex *tex=new TLatex(xpeaks[j],h->GetBinContent(h->FindBin(xpeaks[j])),s1);
    //cout<<xpeaks[j]<<endl;
    tex->SetTextFont(13);
    tex->SetTextSize(14);
    tex->SetTextAlign(12);
    tex->SetTextAngle(90);
    tex->SetTextColor(kRed);
    tex->Draw();
  }
  delete search;
}
