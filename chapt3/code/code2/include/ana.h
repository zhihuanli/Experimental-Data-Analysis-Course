#ifndef ana_h
#define ana_h

#include <vector>
#include <algorithm>
#include <TFile.h>
#include <TTree.h>

using namespace std;
struct dssd//aside
{
  Int_t id;
  Double_t e;
  Double_t t;
};

struct DSSD//x-y side
{
 int xid;
 int yid;
 double xe;//xe
 double ye;//xt
};

class ana 
{
 public:
  vector<dssd> *br_x1v, *br_x2v, *br_x3v;  //声明vector指针
  vector<dssd> *br_y1v, *br_y2v, *br_y3v;
  Float_t sx1e,sx2e,sx3e;//sum
  Float_t sy1e,sy2e,sy3e;    
  TTree *ipt;
  TTree *opt;

  vector<DSSD> d1,d2,d3; //output
    
 ana(TTree* ipt_,TTree *opt_): ipt(ipt_),opt(opt_) {} 
  virtual ~ana() {};
  virtual void     SetBranchInput();
  virtual void     GetDSSD(vector<dssd> *x, vector<dssd> *y, vector<DSSD> &xy);
  virtual void     Analysis();
  virtual void     BranchOutput();
};
#endif
