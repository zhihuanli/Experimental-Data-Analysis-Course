#ifndef ana_h
#define ana_h

#include <TRandom3.h>
#include <iostream>
#include "test.h"  //包含基类头文件

using namespace std;

struct dssd
{
  Int_t id;
  Double_t e;
  Double_t t;
};

class ana : public test //从test类中继承其成员变量和成员函数
{
 public:
  vector<dssd> x1v,x2v,x3v;
  vector<dssd> y1v,y2v,y3v;
  TTree *opt;
  TRandom3 *gr;
    
 ana(TTree* ipt_,TTree *opt_): test(ipt_),opt(opt_) {} 
  virtual ~ana() {};
  virtual void     Analysis();//分析函数，作用等价于原Loop函数
  virtual void     SetOutBranch();
  virtual void     ProcessDS(Double_t ee[32], vector<dssd> &vec);

};
#endif
