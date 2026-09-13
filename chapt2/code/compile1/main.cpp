#include <TFile.h>
#include <TTree.h>
#include <TString.h>
#include <cstdlib>
#include <iostream>
#include "tracking.h"

int main(int argc, char** argv) {
    if (argc!=2 && argc!=4) {
        std::cerr << "Usage: ./tracking run [input_dir output_dir]\n";
        return 1;
    }
    char* end = nullptr;
    long parsed = std::strtol(argv[1], &end, 10);
    if (end==argv[1] || *end!='\0' || parsed<0 || parsed>999999) {
        std::cerr << "Invalid run number: " << argv[1] << '\n';
        return 1;
    }
    int run = int(parsed);
    const char* inputDir = argc==4 ? argv[2] : "../..";
    const char* outputDir = argc==4 ? argv[3] : ".";
    TString inputName = Form("%s/f8ppac%03d.root",inputDir,run);
    TString outputName = Form("%s/out%03d.root",outputDir,run);
    TFile* input = TFile::Open(inputName);
    if (!input || input->IsZombie()) {
        std::cerr << "Cannot open " << inputName << '\n';
        delete input;
        return 1;
    }
    TTree* tin = input->Get<TTree>("tree");
    if (!tin) {
        std::cerr << "Missing tree in " << inputName << '\n';
        delete input;
        return 1;
    }
    TFile output(outputName,"RECREATE");
    if (output.IsZombie()) return 1;
    TTree* tout = new TTree("tree","PPAC tracking");
    {
        tracking analysis(tin);
        analysis.Loop(tout);

        std::cout << "Input=" << tin->GetEntries() << ", output=" << tout->GetEntries() << '\n';
        output.Write();
    } // MakeClass 基类析构时释放输入文件；不再重复 delete input。
    return 0;
}
