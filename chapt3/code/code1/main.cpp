#include <iostream> 
#include <TFile.h>
#include <TTree.h>
#include <TString.h>
#include "ana.h"  //用户代码头文件
using namespace std;

int main(int argc, char** argv)
{

   TString InputPath, OutputPath, infile, outfile;  
    InputPath = "./";
    OutputPath = "./";
    infile.Form("%scal_16C.root", InputPath.Data());
    outfile.Form("%svec_16C.root", OutputPath.Data());
    //input
    TFile *ipf = new TFile(infile);
    if(!ipf->IsOpen()) {
        cout<<"Cannot open input file: "<<infile<<endl;
        return -1;
    }
    TTree *ipt = (TTree*)ipf->Get("tree");

    //output
    TFile *opf = new TFile(outfile,"RECREATE");
    TTree *opt = new TTree("tree","vector branch");

    //
    ana *tk = new ana(ipt,opt); 
    tk->Analysis(); //等价于原Loop函数

    opt->Write();
    //
    ipf->Close();
    opf->Close();
    return 1;       
}
