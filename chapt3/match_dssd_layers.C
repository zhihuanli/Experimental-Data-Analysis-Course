#include "dssd_pairing.h"
#include <TFile.h>
#include <TTree.h>
#include <TH2.h>
#include <iostream>
#include <stdexcept>

void match_dssd_layers(int maxDelta=2) {
    TFile input("data/evt_16C.root");
    TTree* tin=input.Get<TTree>("tree");
    if(!tin) throw std::runtime_error("missing evt_16C tree");
    int hit2,hit3,x2[32],y2[32],x3[32],y3[32];
    double e2[32],e3[32];
    Long64_t original_entry;
    tin->SetBranchAddress("hit2",&hit2); tin->SetBranchAddress("hit3",&hit3);
    tin->SetBranchAddress("x2",x2); tin->SetBranchAddress("y2",y2);
    tin->SetBranchAddress("x3",x3); tin->SetBranchAddress("y3",y3);
    tin->SetBranchAddress("e2",e2); tin->SetBranchAddress("e3",e3);
    tin->SetBranchAddress("jentry",&original_entry);

    TFile output("matched_layers23.root","RECREATE");
    TTree result("tree","DSSD2-DSSD3 one-to-one matching");
    Long64_t file_entry;
    int status,nMatched,partner[2];
    double de[2],ee[2];
    result.Branch("source_entry",&original_entry,"source_entry/L");
    result.Branch("file_entry",&file_entry,"file_entry/L");
    result.Branch("status",&status,"status/I");
    result.Branch("nMatched",&nMatched,"nMatched/I");
    result.Branch("partner",partner,"partner[nMatched]/I");
    result.Branch("de",de,"de[nMatched]/D");
    result.Branch("ee",ee,"ee[nMatched]/D");
    TH2D before("hBefore","Same accepted events, original index;DSSD3 (rel. amplitude);DSSD2 (rel. amplitude)",600,0,9000,600,0,8000);
    TH2D after("hAfter","Same accepted events, geometric pairing;DSSD3 (rel. amplitude);DSSD2 (rel. amplitude)",600,0,9000,600,0,8000);
    Long64_t tested=0,direct=0,swapped=0,ambiguous=0,none=0;
    bool printed=false;
    for(file_entry=0;file_entry<tin->GetEntries();++file_entry) {
        tin->GetEntry(file_entry);
        status=-3; nMatched=0; // -3: 不属于本例的 two-by-two 类
        if(hit2==2 && hit3==2) {
            ++tested;
            status=PairLayers(x2,y2,x3,y3,maxDelta);
            if(status>=0) {
                nMatched=2;
                if(status==0) ++direct; else ++swapped;
                for(int i=0;i<2;++i) {
                    partner[i]=status==0?i:1-i;
                    de[i]=e2[i]; ee[i]=e3[partner[i]];
                    before.Fill(e3[i],e2[i]); after.Fill(ee[i],de[i]);
                }
                if(status==1 && !printed) {
                    std::cout<<"Swapped example: file entry="<<file_entry<<", original entry="<<original_entry<<'\n';
                    for(int i=0;i<2;++i)
                        std::cout<<"D2["<<i<<"] ("<<x2[i]<<","<<y2[i]<<") -> D3["<<partner[i]
                                 <<"] ("<<x3[partner[i]]<<","<<y3[partner[i]]<<")\n";
                    printed=true;
                }
            } else if(status==-2) ++ambiguous; else ++none;
        }
        result.Fill(); // 所有输入事例都留状态，保留与原始事例的关联
    }
    result.Write(); before.Write(); after.Write();
    std::cout<<"Input="<<tin->GetEntries()<<", tested two-by-two="<<tested
             <<"\nDirect="<<direct<<", swapped="<<swapped<<", ambiguous="<<ambiguous
             <<", no match="<<none<<", saved rows="<<result.GetEntries()<<'\n';
    if(tested!=direct+swapped+ambiguous+none || result.GetEntries()!=tin->GetEntries())
        throw std::runtime_error("layer matching accounting mismatch");
}
