#include "ana.h"
using namespace std;

void ana::SetBranchInput()
{
  br_x1v = NULL; //给指针初始化, 这一步必需。
  br_x2v = NULL;
  br_x3v = NULL;
  br_y1v = NULL;
  br_y2v = NULL;
  br_y3v = NULL;
  ipt->SetBranchAddress("x1v", &br_x1v); //将变量指向对应Branch的地址
  ipt->SetBranchAddress("x2v", &br_x2v);
  ipt->SetBranchAddress("x3v", &br_x3v);
  ipt->SetBranchAddress("y1v", &br_y1v);
  ipt->SetBranchAddress("y2v", &br_y2v);
  ipt->SetBranchAddress("y3v", &br_y3v);
  ipt->SetBranchAddress("sx1e", &sx1e);  
  ipt->SetBranchAddress("sx2e", &sx2e);  
  ipt->SetBranchAddress("sx3e", &sx3e);  
  ipt->SetBranchAddress("sy1e", &sy1e);  
  ipt->SetBranchAddress("sy2e", &sy2e);  
  ipt->SetBranchAddress("sy3e", &sy3e);  
}

void ana::BranchOutput()
{ 
  opt->Branch("d1",&d1);
  opt->Branch("d2",&d2);
  opt->Branch("d3",&d3);
}

bool SortDS(dssd &a,dssd &b)
{
  return a.e > b.e;
}

void ana::GetDSSD(vector<dssd> *x, vector<dssd> *y, vector<DSSD> &xy)
{
 int hit=min(x->size(),y->size());
 xy.clear();
 DSSD dxy;
 for(int i=0;i<hit;i++) {
     double xe=(*x)[i].e;//按照下标读取vector内的值 
     double ye=(*y)[i].e;
     int ix=(*x)[i].id;
     int iy=(*y)[i].id;     
     if(abs(xe-ye)<50) {
         dxy.xe=xe;
         dxy.ye=ye;
         dxy.xid=ix;
         dxy.yid=iy;
         xy.push_back(dxy);
     }
 }     
}

void ana::Analysis()
{
  SetBranchInput();
  BranchOutput();
  if (ipt == 0) return;
  Long64_t nentries = ipt->GetEntriesFast();
  for (Long64_t jentry=0; jentry<nentries;jentry++) {
    ipt->GetEntry(jentry);
    sort(br_x1v->begin(),br_x1v->end(),SortDS);
    sort(br_y1v->begin(),br_y1v->end(),SortDS);  
    sort(br_x2v->begin(),br_x2v->end(),SortDS);
    sort(br_y2v->begin(),br_y2v->end(),SortDS);
    sort(br_x3v->begin(),br_x3v->end(),SortDS);
    sort(br_y3v->begin(),br_y3v->end(),SortDS);
    GetDSSD(br_x1v,br_y1v,d1);
    GetDSSD(br_x2v,br_y2v,d2);
    GetDSSD(br_x3v,br_y3v,d3);
    if(d1.size()>0 || d2.size()>0 || d3.size()>0)
        opt->Fill();
      
    if((jentry) % 1000 == 0) {
      printf("Process %.2f %, %dk / %dk\r",Double_t(jentry)/nentries*100.,
	     int(jentry/1000), int(nentries/1000));
      fflush(stdout);
    }
  }
}
