#include "ana.h"
using namespace std;
void ana::SetOutBranch()
{
  opt->Branch("x1v",&x1v);
  opt->Branch("x2v",&x2v);
  opt->Branch("x3v",&x3v);
  opt->Branch("y1v",&y1v);
  opt->Branch("y2v",&y2v);
  opt->Branch("y3v",&y3v);
  opt->Branch("sx1e",&sx1e,"sx1e");
  opt->Branch("sx2e",&sx2e,"sx2e");
  opt->Branch("sx3e",&sx3e,"sx3e");
  opt->Branch("sy1e",&sy1e,"sy1e");
  opt->Branch("sy2e",&sy2e,"sy2e");
  opt->Branch("sy3e",&sy3e,"sy3e");

}

void ana::ProcessDS(Double_t ee[32], vector<dssd> &vec)
{
   vec.clear();
    dssd ds;
    for(int i=0;i<32;i++) {
      if(ee[i]<1) continue;
	ds.id=i;
	ds.e=ee[i];
	vec.push_back(ds);
    }
}
void ana::Analysis()
{
  SetOutBranch();
  if (fChain == 0) return;
  Long64_t nentries = fChain->GetEntriesFast();
  Long64_t nbytes = 0, nb = 0;
  for (Long64_t jentry=0; jentry<nentries;jentry++) {
    Long64_t ientry = LoadTree(jentry);
    if (ientry < 0) break;
    nb = fChain->GetEntry(jentry);   nbytes += nb;
    ProcessDS(d1x,x1v);
    ProcessDS(d1y,y1v);
    ProcessDS(d2x,x2v);
    ProcessDS(d2y,y2v);
    ProcessDS(d3x,x3v);
    ProcessDS(d3y,y3v);
    bool b1=x1v.size()>0 || y1v.size()>0;
    bool b2=x2v.size()>0 || y2v.size()>0;
    bool b3=x3v.size()>0 || x3v.size()>0;
    if(b1||b2||b3) opt->Fill();

    if((jentry) % 1000 == 0) {
      printf("Process %.2f % %dk / %dk\r",Double_t(jentry)/nentries*100.,
	     int(jentry/1000), int(nentries/1000));
      fflush(stdout);
    }
  }
}
