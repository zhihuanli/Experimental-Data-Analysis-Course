#ifndef ANA_H
#define ANA_H
#include "tracking.h"
#include <TH2.h>
class ana : public tracking {
public:

   Double_t xx[3], xz[3], yy[3], yz[3], dx[3], dy[3];
   Double_t xx2b[2], yy2b[2], xz2b, yz2b, anode2b;
   Double_t tx,ty,theta_x,theta_y,sigma_tx,sigma_ty,sigma_thetax,sigma_thetay,c2nx,c2ny;
   Long64_t source_entry;
   void SetBranch(TTree *tree);
   void TrackInit();
   void SetTrace(TH2D *h, Double_t k, Double_t b, Int_t min, Int_t max);


    TTree *fOutTree;
    ana(TTree *input,TTree *output) : tracking(input),fOutTree(output) {}
    void Analysis();
};
#endif
