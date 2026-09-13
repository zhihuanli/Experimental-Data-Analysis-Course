#include <TFile.h>
#include <TTree.h>
#include <iostream>
#include "ana.h"
int main(int argc, char** argv) {
    const char* inputName = argc>1 ? argv[1] : "../../vec_16C.root";
    const char* outputName = argc>2 ? argv[2] : "../../sort_16C.root";
    TFile* input = TFile::Open(inputName);
    if (!input || input->IsZombie()) return 1;
    TTree* tin = input->Get<TTree>("tree");
    if (!tin) return 1;
    TFile output(outputName,"RECREATE");
    TTree* tout = new TTree("tree","vector branch");
    {
        ana analysis(tin,tout);
        analysis.Analysis();
        std::cout << "Input=" << tin->GetEntries() << ", output=" << tout->GetEntries() << '\n';
        output.cd();
        tout->Write();
    }
    delete input;
    return 0;
}
