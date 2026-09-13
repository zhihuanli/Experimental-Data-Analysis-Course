#include <TFile.h>
#include <TTree.h>
#include <TString.h>
#include <cstdlib>
#include <iostream>
#include "ana.h"

int main(int argc, char** argv) {
    if (argc!=2 && argc!=4) {
        std::cerr << "Usage: ./tracking run [input_dir output_dir]\n";
        return 1;
    }
    int run = std::atoi(argv[1]);
    const char* inputDir = argc==4 ? argv[2] : "../..";
    const char* outputDir = argc==4 ? argv[3] : ".";
    TString inputName = Form("%s/f8ppac%03d.root",inputDir,run);
    TString outputName = Form("%s/out%03d.root",outputDir,run);
    TFile* input = TFile::Open(inputName);
    if (!input || input->IsZombie()) return 1;
    TTree* tin = input->Get<TTree>("tree");
    if (!tin) return 1;
    TFile output(outputName,"RECREATE");
    if (output.IsZombie()) return 1;
    TTree* tout = new TTree("tree","PPAC tracking");
    {
        ana analysis(tin,tout);
        analysis.Analysis();

        std::cout << "Input=" << tin->GetEntries() << ", output=" << tout->GetEntries() << '\n';
        output.Write();
    } // MakeClass 基类析构时释放输入文件；不再重复 delete input。
    return 0;
}
