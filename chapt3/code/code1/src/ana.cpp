#include "ana.h"
using namespace std;
void ana::SetOutBranch()
{
  opt->Branch("source_entry", &source_entry, "source_entry/L");
  opt->Branch("x1v",&x1v);
  opt->Branch("x2v",&x2v);
  opt->Branch("x3v",&x3v);
  opt->Branch("y1v",&y1v);
  opt->Branch("y2v",&y2v);
  opt->Branch("y3v",&y3v);
  opt->Branch("sx1e",&sx1e,"sx1e/D");
  opt->Branch("sx2e",&sx2e,"sx2e/D");
  opt->Branch("sx3e",&sx3e,"sx3e/D");
  opt->Branch("sy1e",&sy1e,"sy1e/D");
  opt->Branch("sy2e",&sy2e,"sy2e/D");
  opt->Branch("sy3e",&sy3e,"sy3e/D");

}

void ana::ProcessDS(const Double_t ee[32], vector<dssd> &vec)
{
    vec.clear(); // 每个事件重新建立 hit 列表
    for(int i=0; i<32; ++i) {
        if(ee[i]<1) continue;
        dssd hit;
        hit.id=i;
        hit.e=ee[i];
        vec.push_back(hit); // t 保持 NaN，输入没有时间信息
    }
}
void ana::Analysis()
{
  if (fChain == 0) return;
  SetOutBranch();
  Long64_t nentries = fChain->GetEntriesFast();
  for (Long64_t jentry=0; jentry<nentries;jentry++) {
    Long64_t ientry = LoadTree(jentry);
    if (ientry < 0) break;
    fChain->GetEntry(jentry);
    ProcessDS(d1x,x1v);
    ProcessDS(d1y,y1v);
    ProcessDS(d2x,x2v);
    ProcessDS(d2y,y2v);
    ProcessDS(d3x,x3v);
    ProcessDS(d3y,y3v);
    source_entry = jentry;
    opt->Fill(); // 保留空事件及事件对应关系


  }
}
