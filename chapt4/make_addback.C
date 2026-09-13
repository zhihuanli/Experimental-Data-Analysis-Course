#include <iostream>
#include <cmath>

#include "TFile.h"
#include "TTree.h"

const int ADD_MAXHIT = 1024;


// ------------------------------------------------------------
// Check whether two crystals are adjacent in the same cluster
// ------------------------------------------------------------
bool addback_is_adjacent(int id1, int id2)
{
  int cluster1 = id1 / 7;
  int cluster2 = id2 / 7;

  int seg1 = id1 % 7;
  int seg2 = id2 % 7;

  if (cluster1 != cluster2) return false;
  if (seg1 < 0 || seg1 >= 7) return false;
  if (seg2 < 0 || seg2 >= 7) return false;
  if (seg1 == seg2) return false;

  /*
    Local crystal geometry:

        0--1
       /    \
      5  6   2
       \    /
        4--3

    Segment 6 is the center crystal.
    The center crystal is adjacent to all outer crystals.
    The outer crystals are adjacent along the ring.
  */

  if (seg1 == 6 || seg2 == 6) {
    return true;
  }

  int d = std::abs(seg1 - seg2);

  if (d == 1) return true;

  if ((seg1 == 0 && seg2 == 5) ||
      (seg1 == 5 && seg2 == 0)) {
    return true;
  }

  return false;
}


// ------------------------------------------------------------
// Make addback tree
// ------------------------------------------------------------
void make_addback_tree(
    const char *inputFile = "eurica_time_pair.root",
    const char *outputFile = "eurica_addback.root")
{
  const double addbackWindow = 400.0; // ns

  TFile *fin = new TFile(inputFile);
  if (!fin || fin->IsZombie()) {
    std::cout << "cannot open " << inputFile << std::endl;
    return;
  }

  TTree *tin = (TTree*)fin->Get("tree");
  if (!tin) {
    std::cout << "cannot find tree in " << inputFile << std::endl;
    fin->Close();
    return;
  }

  int ghit;
  int gid_in[ADD_MAXHIT];
  double ge_in[ADD_MAXHIT];
  double gt_in[ADD_MAXHIT];

  if (tin->GetMaximum("ghit") > ADD_MAXHIT)
    throw std::runtime_error("Increase ADD_MAXHIT before reading branches");

  tin->SetBranchAddress("ghit", &ghit);
  tin->SetBranchAddress("gid", gid_in);
  tin->SetBranchAddress("ge", ge_in);
  tin->SetBranchAddress("gt", gt_in);

  TFile *fout = new TFile(outputFile, "recreate");
  TTree *tout = new TTree("tree", "addback tree");

  int o_ghit;
  int o_gid[ADD_MAXHIT];
  double o_ge[ADD_MAXHIT];
  double o_gt[ADD_MAXHIT];

  int o_ahit;
  int o_aid[ADD_MAXHIT];
  double o_ae[ADD_MAXHIT];
  double o_at[ADD_MAXHIT];

  tout->Branch("ghit", &o_ghit, "ghit/I");
  tout->Branch("gid", o_gid, "gid[ghit]/I");
  tout->Branch("ge", o_ge, "ge[ghit]/D");
  tout->Branch("gt", o_gt, "gt[ghit]/D");

  tout->Branch("ahit", &o_ahit, "ahit/I");
  tout->Branch("aid", o_aid, "aid[ahit]/I");
  tout->Branch("ae", o_ae, "ae[ahit]/D");
  tout->Branch("at", o_at, "at[ahit]/D");

  Long64_t nentries = tin->GetEntries();

  for (Long64_t ientry = 0; ientry < nentries; ientry++) {

    tin->GetEntry(ientry);

    o_ghit = ghit;

    for (int i = 0; i < ghit; i++) {
      o_gid[i] = gid_in[i];
      o_ge[i] = ge_in[i];
      o_gt[i] = gt_in[i];
    }

    int used[ADD_MAXHIT];

    for (int i = 0; i < ghit; i++) {
      used[i] = 0;
    }

    o_ahit = 0;

    for (int i = 0; i < ghit; i++) {

      if (used[i]) continue;

      int group[ADD_MAXHIT];
      int ngroup = 0;

      int queue[ADD_MAXHIT];
      int qfront = 0;
      int qback = 0;

      queue[qback++] = i;
      used[i] = 1;

      while (qfront < qback) {

        int u = queue[qfront++];
        group[ngroup++] = u;

        for (int v = 0; v < ghit; v++) {

          if (used[v]) continue;

          bool sameCluster =
            (gid_in[u] / 7 == gid_in[v] / 7);

          bool adjacent =
            addback_is_adjacent(gid_in[u], gid_in[v]);

          bool intime =
            std::abs(gt_in[u] - gt_in[v]) < addbackWindow;

          if (sameCluster && adjacent && intime) {
            used[v] = 1;
            queue[qback++] = v;
          }
        }
      }

      double esum = 0.0;
      int seed = group[0];

      for (int k = 0; k < ngroup; k++) {

        int idx = group[k];

        esum += ge_in[idx];

        if (ge_in[idx] > ge_in[seed]) {
          seed = idx;
        }
      }

      o_aid[o_ahit] = gid_in[seed];
      o_ae[o_ahit] = esum;
      o_at[o_ahit] = gt_in[seed];

      o_ahit++;
    }

    tout->Fill();
  }

  fout->cd();
  tout->Write();
  fout->Close();
  fin->Close();

  std::cout << "addback file saved to "
            << outputFile << std::endl;
}
