#include "dssd_pairing.h"
#include <TFile.h>
#include <TTree.h>
#include <TH2.h>
#include <TH1.h>
#include <iostream>
#include <stdexcept>

// 有界实例：仅检验 DSSD2 的 (xhit,yhit)=(2,3) 两粒子假设。
// 输出另存，不覆盖 cal_16C.root 或完整参考重建 evt_16C.root。
void reconstruct_two_particles(double tolerance=15) {
    TFile input("data/cal_16C.root");
    TTree* tin=input.Get<TTree>("tree");
    if (!tin) throw std::runtime_error("missing cal_16C tree");
    int nx,ny,x[32],y[32];
    double ex[32],ey[32];
    tin->SetBranchAddress("x2hit",&nx); tin->SetBranchAddress("y2hit",&ny);
    tin->SetBranchAddress("x2",x); tin->SetBranchAddress("y2",y);
    tin->SetBranchAddress("x2e",ex); tin->SetBranchAddress("y2e",ey);

    TFile output("two_particle_candidates.root","RECREATE");
    TTree result("tree","DSSD2 two-by-three candidates");
    Long64_t source_entry;
    int nCandidates, hit, ix[2], iy[2], ymask[2];
    double energy[2], residual[2];
    result.Branch("source_entry",&source_entry,"source_entry/L");
    result.Branch("nCandidates",&nCandidates,"nCandidates/I");
    result.Branch("hit",&hit,"hit/I");
    result.Branch("x",ix,"x[hit]/I"); result.Branch("y",iy,"y[hit]/I");
    result.Branch("ymask",ymask,"ymask[hit]/I"); // 输入 Y hit 的成员位掩码
    result.Branch("e",energy,"e[hit]/D"); result.Branch("residual",residual,"residual[hit]/D");
    TH2D hAll("hCandidates","All geometric hypotheses;r_{group} (rel. amplitude);r_{single} (rel. amplitude)",240,-120,120,240,-120,120);
    TH2D hUnique("hUnique","Unique accepted hypothesis;r_{group};r_{single}",120,-30,30,120,-30,30);
    Long64_t total23=0, topology=0, unique=0, ambiguous=0, none=0;
    Long64_t firstUnique=-1;
    for(source_entry=0;source_entry<tin->GetEntries();++source_entry) {
        tin->GetEntry(source_entry);
        if(nx!=2 || ny!=3) continue;
        ++total23;
        if(std::abs(x[0]-x[1])<=1) continue;
        int adjacent=0;
        for(int a=0;a<3;++a) for(int b=a+1;b<3;++b)
            if(std::abs(y[a]-y[b])==1) ++adjacent;
        if(adjacent!=1) continue; // 排除三连条等其他拓扑
        ++topology;
        double cx[2]={ex[0]-25,ex[1]-25};
        double cy[3]={ey[0]-25,ey[1]-25,ey[2]-25};
        // 显示所有几何候选，未先施加总能量或逐粒子 residual cut。
        for(int a=0;a<3;++a) for(int b=a+1;b<3;++b) {
            if(std::abs(y[a]-y[b])!=1) continue;
            int c=3-a-b;
            for(int i=0;i<2;++i) hAll.Fill(cx[i]-cy[a]-cy[b],cx[1-i]-cy[c]);
        }
        int a=-1,b=-1,c=-1,i=-1;
        nCandidates=Pair23(x,y,cx,cy,tolerance,a,b,c,i);
        hit=0;
        if(nCandidates==1) {
            ++unique; hit=2;
            ix[0]=x[i]; ix[1]=x[1-i];
            iy[0]=cy[a]>=cy[b]?y[a]:y[b]; // 用共享组中幅度较大的条定位
            iy[1]=y[c];
            ymask[0]=(1<<a)|(1<<b); ymask[1]=1<<c;
            energy[0]=cx[i]; energy[1]=cx[1-i]; // X 两条各自分辨了一个粒子
            residual[0]=cx[i]-cy[a]-cy[b]; residual[1]=cx[1-i]-cy[c];
            hUnique.Fill(residual[0],residual[1]);
            if(firstUnique<0) {
                firstUnique=source_entry;
                std::cout<<"Example input entry "<<source_entry<<": Y["<<a<<"]+Y["<<b
                         <<"] -> X["<<i<<"], Y["<<c<<"] -> X["<<1-i<<"]\n";
            }
        } else if(nCandidates>1) ++ambiguous;
        else ++none;
        result.Fill(); // 无解、多解也保留，hit=0，不把它们伪装成唯一解
    }
    result.Write(); hAll.Write(); hUnique.Write();
    std::cout<<"Input="<<tin->GetEntries()<<", (2,3)="<<total23<<", tested topology="<<topology
             <<"\nTolerance="<<tolerance<<", unique="<<unique<<", ambiguous="<<ambiguous
             <<", no match="<<none<<"\nSaved rows="<<result.GetEntries()<<'\n';
    if(topology!=unique+ambiguous+none) throw std::runtime_error("candidate accounting mismatch");
}
