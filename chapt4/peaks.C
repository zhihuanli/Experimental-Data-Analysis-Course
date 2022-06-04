
TH1D *h=NULL,*hb=NULL;
Int_t nfound;
Double_t *xpeaks=NULL, *ypeaks=NULL;
TSpectrum *s=NULL;
void peaks(TString hname, Double_t thres=0.005,int backsub=0)
{
  h=(TH1D*)gROOT->FindObject(hname);
  if(!s) s=new TSpectrum(500);
  if(backsub) {
    hb=(TH1D*)s->Background(h,80,"same");
    h->Add(h,hb,1,-1);   
  }
  h->Sumw2(0);
  h->SetStats(0);
  h->SetFillColor(kCyan);
  nfound=s->Search(h,2,"",thres); 
  TPolyMarker *pm=(TPolyMarker *)
    h->GetListOfFunctions()->FindObject("TPolyMarker");
  pm->SetMarkerStyle(32);
  pm->SetMarkerColor(kGreen);
  pm->SetMarkerSize(0.4);
  xpeaks=s->GetPositionX();
  ypeaks=s->GetPositionY();
  for(int j=0;j<nfound;j++) {
    stringstream ss;
    ss<<xpeaks[j];
    TString s1=ss.str();
    TLatex *tex=new TLatex(xpeaks[j],ypeaks[j],s1);
    //cout<<xpeaks[j]<<endl;
    tex->SetTextFont(13);
    tex->SetTextSize(14);
    tex->SetTextAlign(12);
    tex->SetTextAngle(90);
    tex->SetTextColor(kRed);
    tex->Draw();
  }
}
