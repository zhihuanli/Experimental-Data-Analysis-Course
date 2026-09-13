#include "../chapt3/dssd_pairing.h"
#include <TFile.h>
#include <TTree.h>
#include <TH2.h>
#include <cassert>
#include <iostream>
#include <cmath>

void test_dssd_pairing() {
    int x[2]={4,14}, y[3]={3,4,20};
    double ex[2]={100,60}, ey[3]={40,60,60};
    int a,b,c,i;
    assert(Pair23(x,y,ex,ey,2,a,b,c,i)==1 && i==0 && c==2);
    double swapped[2]={60,100};
    assert(Pair23(x,y,swapped,ey,2,a,b,c,i)==1 && i==1);
    double near[2]={100,100}, ambiguousY[3]={40,60,100};
    assert(Pair23(x,y,near,ambiguousY,2,a,b,c,i)==2);
    double unmatched[2]={150,180};
    assert(Pair23(x,y,unmatched,ey,2,a,b,c,i)==0);
    int adjacentX[2]={4,5}, chainY[3]={3,4,5};
    assert(Pair23(adjacentX,y,ex,ey,2,a,b,c,i)==0);
    assert(Pair23(x,chainY,ex,ey,2,a,b,c,i)==0);

    int x2[2]={2,20},y2[2]={4,21},x3[2]={3,21},y3[2]={5,20};
    assert(PairLayers(x2,y2,x3,y3)==0);
    std::swap(x3[0],x3[1]); std::swap(y3[0],y3[1]);
    assert(PairLayers(x2,y2,x3,y3)==1);
    int q[2]={10,11};
    assert(PairLayers(q,q,q,q)==-2);
    assert(PairLayers(x2,y2,q,q)==-1);

    TFile original("chapt3/data/evt_16C.root");
    TFile matched("chapt3/matched_layers23.root");
    auto tin=original.Get<TTree>("tree"), tout=matched.Get<TTree>("tree");
    assert(tin && tout && tin->GetEntries()==tout->GetEntries());
    Long64_t source,stored,fileEntry;
    int n2,n3,status,n,p[2],ax[32],ay[32],bx[32],by[32];
    double e2[32],e3[32],de[2],ee[2];
    tin->SetBranchAddress("jentry",&source);
    tin->SetBranchAddress("hit2",&n2); tin->SetBranchAddress("hit3",&n3);
    tin->SetBranchAddress("x2",ax); tin->SetBranchAddress("y2",ay);
    tin->SetBranchAddress("x3",bx); tin->SetBranchAddress("y3",by);
    tin->SetBranchAddress("e2",e2); tin->SetBranchAddress("e3",e3);
    tout->SetBranchAddress("source_entry",&stored);
    tout->SetBranchAddress("file_entry",&fileEntry);
    tout->SetBranchAddress("status",&status);
    tout->SetBranchAddress("nMatched",&n);
    tout->SetBranchAddress("partner",p);
    tout->SetBranchAddress("de",de); tout->SetBranchAddress("ee",ee);
    Long64_t unique=0;
    for(Long64_t row=0;row<tin->GetEntries();++row) {
        tin->GetEntry(row);tout->GetEntry(row);
        assert(source==stored && row==fileEntry);
        int expected=(n2==2 && n3==2)?PairLayers(ax,ay,bx,by):-3;
        assert(status==expected);
        if(status>=0) {
            assert(n==2 && p[0]!=p[1]); ++unique;
            for(int j=0;j<2;++j) {
                assert(de[j]==e2[j] && ee[j]==e3[p[j]]);
                assert(std::abs(ax[j]-bx[p[j]])<=2 && std::abs(ay[j]-by[p[j]])<=2);
            }
            assert(ee[0]+ee[1]==e3[0]+e3[1]);
        } else assert(n==0);
    }
    assert(matched.Get<TH2>("hBefore")->GetEntries()==2*unique);
    assert(matched.Get<TH2>("hAfter")->GetEntries()==2*unique);

    TFile strips("chapt3/data/cal_16C.root"), candidates("chapt3/two_particle_candidates.root");
    auto raw=strips.Get<TTree>("tree"), out=candidates.Get<TTree>("tree");
    Long64_t entry;
    int nhx,nhy,sx[32],sy[32],nc,nh,ox[2],oy[2],mask[2];
    double rx[32],ry[32],oe[2],res[2];
    raw->SetBranchAddress("x2hit",&nhx); raw->SetBranchAddress("y2hit",&nhy);
    raw->SetBranchAddress("x2",sx); raw->SetBranchAddress("y2",sy);
    raw->SetBranchAddress("x2e",rx); raw->SetBranchAddress("y2e",ry);
    out->SetBranchAddress("source_entry",&entry);
    out->SetBranchAddress("nCandidates",&nc); out->SetBranchAddress("hit",&nh);
    out->SetBranchAddress("x",ox); out->SetBranchAddress("y",oy);
    out->SetBranchAddress("ymask",mask); out->SetBranchAddress("e",oe);
    out->SetBranchAddress("residual",res);
    for(Long64_t row=0;row<out->GetEntries();++row) {
        out->GetEntry(row);raw->GetEntry(entry);
        assert(nhx==2 && nhy==3);
        double cx[2]={rx[0]-25,rx[1]-25},cy[3]={ry[0]-25,ry[1]-25,ry[2]-25};
        assert(nc==Pair23(sx,sy,cx,cy,15,a,b,c,i));
        if(nc!=1) {assert(nh==0);continue;}
        assert(nh==2 && ox[0]==sx[i] && ox[1]==sx[1-i]);
        assert(mask[0]==((1<<a)|(1<<b)) && mask[1]==(1<<c));
        assert(oe[0]==cx[i] && oe[1]==cx[1-i]);
        assert(std::abs(res[0])<=15 && std::abs(res[1])<=15);
        assert(std::abs(oe[0]+oe[1]-(rx[0]+rx[1]-50))<1e-9);
    }
    std::cout<<"PASS: synthetic unique/swapped/ambiguous/unmatched cases; all "
             <<tin->GetEntries()<<" layer records and "<<out->GetEntries()
             <<" strip-candidate records preserve source IDs, energies and assignments.\n";
}
