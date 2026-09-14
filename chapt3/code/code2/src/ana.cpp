#include "ana.h"
#include <cmath>
using namespace std;

void ana::SetBranchInput()
{
  ipt->SetBranchAddress("source_entry", &source_entry);
  br_x1v = nullptr; // ROOT 读入后使指针指向对应的 vector
  br_x2v = nullptr;
  br_x3v = nullptr;
  br_y1v = nullptr;
  br_y2v = nullptr;
  br_y3v = nullptr;
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
  opt->Branch("source_entry", &source_entry, "source_entry/L");
  opt->Branch("d1",&d1);
  opt->Branch("d2",&d2);
  opt->Branch("d3",&d3);
}

bool SortDS(const dssd &a,const dssd &b)
{
  return a.e > b.e;
}

void ana::GetDSSD(vector<dssd> *x, vector<dssd> *y, vector<DSSD> &xy)
{
    xy.clear();
    const size_t nPairs=std::min(x->size(),y->size());
    for(size_t i=0; i<nPairs; ++i) {
        const dssd &xhit=(*x)[i]; // 引用完整 hit，条号和幅度保持对应
        const dssd &yhit=(*y)[i];
        if(std::abs(xhit.e-yhit.e)<50) {
            DSSD pair;
            pair.xid=xhit.id;
            pair.yid=yhit.id;
            pair.xe=xhit.e;
            pair.ye=yhit.e;
            xy.push_back(pair);
        }
    }
}

void ana::Analysis()
{
  if (ipt == 0) return;
  SetBranchInput();
  BranchOutput();
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
    opt->Fill(); // 无候选时保存空 vector，不改变事件顺序


  }
}
