// pair_timewalk_correction.C

#include <iostream>
#include <vector>
#include <cmath>

#include "TFile.h"
#include "TTree.h"
#include "TH1F.h"
#include "TH2F.h"
#include "TProfile.h"
#include "TF1.h"
#include "TCanvas.h"
#include "TROOT.h"
#include "TStyle.h"
#include "TLatex.h"
#include "TFitResultPtr.h"

const int MAXHIT = 1024;
const int NCLUSTER = 12;
const int NSEG = 7;

double E_HIGH = 600.0;
double E_REF = 600.0;
double E_MAX_OFFSET = 3000.0;

TH2F *h_tw_id[NSEG] = {0};
TProfile *hp_tw_id[NSEG] = {0};

TH1F *h_off_pair[NSEG][NSEG] = {0};
TF1  *f_off_pair[NSEG][NSEG] = {0};

double t_off[NCLUSTER][NSEG][NSEG];
int has_toff[NCLUSTER][NSEG][NSEG];

TF1 *f_tw[NCLUSTER][NSEG] = {0};
int has_fit[NCLUSTER][NSEG];

Long64_t seg_high_count[NCLUSTER][NSEG];

double seg_offset[NCLUSTER][NSEG];
int has_seg_offset[NCLUSTER][NSEG];

int ref_seg_cluster[NCLUSTER];


// ------------------------------------------------------------
// Make pair-combination time-walk histograms for one cluster
// ------------------------------------------------------------
std::vector<TH2F*> make_pair_timewalk_cluster(int clusterID = 6)
{
  TH1::AddDirectory(kFALSE);

  std::vector<TH2F*> hlist;

  if (clusterID < 0 || clusterID >= NCLUSTER) {
    std::cout << "invalid clusterID" << std::endl;
    return hlist;
  }

  TFile *fin = new TFile("eurica_event.root");
  if (!fin || fin->IsZombie()) {
    std::cout << "cannot open eurica_event.root" << std::endl;
    return hlist;
  }

  TTree *tree = (TTree*)fin->Get("tree");
  if (!tree) {
    std::cout << "cannot find tree" << std::endl;
    fin->Close();
    return hlist;
  }

  int ghit;
  int gid[MAXHIT];
  double ge[MAXHIT];
  double gt[MAXHIT];

  if (tree->GetMaximum("ghit")>MAXHIT)
    throw std::runtime_error("Increase MAXHIT before reading branches");

  tree->SetBranchAddress("ghit", &ghit);
  tree->SetBranchAddress("gid", gid);
  tree->SetBranchAddress("ge", ge);
  tree->SetBranchAddress("gt", gt);

  for (int s = 0; s < NSEG; s++) {
    seg_high_count[clusterID][s] = 0;
  }

  // reset offset histograms and fit functions
  for (int i = 0; i < NSEG; i++) {
    for (int j = 0; j < NSEG; j++) {

      has_toff[clusterID][i][j] = 0;
      t_off[clusterID][i][j] = 0.0;

      if (h_off_pair[i][j]) {
        delete h_off_pair[i][j];
        h_off_pair[i][j] = 0;
      }

      if (f_off_pair[i][j]) {
        delete f_off_pair[i][j];
        f_off_pair[i][j] = 0;
      }

      if (i == j) continue;

      h_off_pair[i][j] =
        new TH1F(Form("h_off_c%d_%d_%d", clusterID, i, j),
                 Form("cluster %d: pair %d-%d; t_{%d}-t_{%d} (ns); counts",
                      clusterID, i, j, i, j),
                 120, -600, 600);

      h_off_pair[i][j]->SetDirectory(0);
    }
  }

  Long64_t nentries = tree->GetEntries();

  // first pass: fill high-energy pair offset histograms
  for (Long64_t ientry = 0; ientry < nentries; ientry++) {

    tree->GetEntry(ientry);

    for (int a = 0; a < ghit; a++) {

      int cid_a = gid[a] / 7;
      int sid_a = gid[a] % 7;

      if (cid_a != clusterID) continue;
      if (sid_a < 0 || sid_a >= NSEG) continue;
      if (ge[a] < E_HIGH || ge[a] > E_MAX_OFFSET) continue;

      seg_high_count[clusterID][sid_a]++;

      for (int b = 0; b < ghit; b++) {

        if (a == b) continue;

        int cid_b = gid[b] / 7;
        int sid_b = gid[b] % 7;

        if (cid_b != clusterID) continue;
        if (sid_b < 0 || sid_b >= NSEG) continue;
        if (sid_b == sid_a) continue;
        if (ge[b] < E_HIGH || ge[b] > E_MAX_OFFSET) continue;

        double dt = gt[a] - gt[b];

        h_off_pair[sid_a][sid_b]->Fill(dt);
      }
    }
  }

  // fit pair offsets
  for (int i = 0; i < NSEG; i++) {
    for (int j = 0; j < NSEG; j++) {

      if (i == j) continue;
      if (!h_off_pair[i][j]) continue;

      if (h_off_pair[i][j]->GetEntries() < 50) {
        continue;
      }

      int maxbin = h_off_pair[i][j]->GetMaximumBin();
      double x0 = h_off_pair[i][j]->GetBinCenter(maxbin);

      f_off_pair[i][j] =
        new TF1(Form("f_off_c%d_%d_%d", clusterID, i, j),
                "gaus",
                x0 - 120.0,
                x0 + 120.0);

      f_off_pair[i][j]->SetParameter(0, h_off_pair[i][j]->GetMaximum());
      f_off_pair[i][j]->SetParameter(1, x0);
      f_off_pair[i][j]->SetParameter(2, 60.0);

      TFitResultPtr r = h_off_pair[i][j]->Fit(f_off_pair[i][j], "RQ0");

      if ((int)r == 0) {
        t_off[clusterID][i][j] = f_off_pair[i][j]->GetParameter(1);
      } else {
        std::cout << "Skip failed pair offset fit: " << clusterID << ", " << i << ", " << j << std::endl;
        continue;
      }

      has_toff[clusterID][i][j] = 1;
    }
  }

  // reset time-walk histograms
  for (int s = 0; s < NSEG; s++) {

    if (h_tw_id[s]) {
      delete h_tw_id[s];
      h_tw_id[s] = 0;
    }

    h_tw_id[s] =
      new TH2F(Form("h_tw_c%d_id%d", clusterID, s),
               Form("cluster %d: segment %d, all references; #Delta t_{ij} (ns); E_{seg %d}",
                    clusterID, s, s),
               80, -600, 600,
               130, 0, 1300);

    h_tw_id[s]->SetDirectory(0);
    hlist.push_back(h_tw_id[s]);
  }

  // second pass: fill pair-offset-corrected time-walk plots
  for (Long64_t ientry = 0; ientry < nentries; ientry++) {

    tree->GetEntry(ientry);

    for (int a = 0; a < ghit; a++) {

      int cid_a = gid[a] / 7;
      int sid_a = gid[a] % 7;

      if (cid_a != clusterID) continue;
      if (sid_a < 0 || sid_a >= NSEG) continue;
      if (ge[a] < 30) continue;

      for (int b = 0; b < ghit; b++) {

        if (a == b) continue;

        int cid_b = gid[b] / 7;
        int sid_b = gid[b] % 7;

        if (cid_b != clusterID) continue;
        if (sid_b < 0 || sid_b >= NSEG) continue;
        if (sid_b == sid_a) continue;
        if (ge[b] < E_HIGH) continue;

        if (!has_toff[clusterID][sid_a][sid_b]) continue;

        double dt = gt[a] - gt[b];
        double dt_corr = dt - t_off[clusterID][sid_a][sid_b];

        h_tw_id[sid_a]->Fill(dt_corr, ge[a]);
      }
    }
  }

  fin->Close();

  std::cout << "cluster " << clusterID
            << " pair time-walk histograms filled." << std::endl;

  for (int s = 0; s < NSEG; s++) {
    std::cout << "segment " << s
              << " high-energy count = " << seg_high_count[clusterID][s]
              << ", walk entries = " << h_tw_id[s]->GetEntries()
              << std::endl;
  }

  return hlist;
}


// ------------------------------------------------------------
// Draw 7 segment time-walk plots for current cluster
// ------------------------------------------------------------
void draw_pair_timewalk_cluster(int clusterID = 6)
{
  TCanvas *c_old = (TCanvas*)gROOT->FindObject("c_pair_tw");
  if (c_old) delete c_old;

  TCanvas *c = new TCanvas("c_pair_tw",
                           Form("cluster %d: pair-combination time walk", clusterID),
                           900, 600);

  c->Divide(4, 2);
  gStyle->SetOptStat(0);

  for (int s = 0; s < NSEG; s++) {
    c->cd(s + 1);
    if (h_tw_id[s]) h_tw_id[s]->Draw("colz");
  }

  c->Draw();
}


// ------------------------------------------------------------
// Draw pair offset histograms for current cluster
// ------------------------------------------------------------
void draw_pair_offset_cluster(int clusterID = 6)
{
  TCanvas *c_old = (TCanvas*)gROOT->FindObject("c_pair_off");
  if (c_old) delete c_old;

  TCanvas *c = new TCanvas("c_pair_off",
                           Form("cluster %d: pair offsets", clusterID),
                           1050, 1050);

  c->Divide(7, 7);
  gStyle->SetOptStat(0);

  for (int i = 0; i < NSEG; i++) {
    for (int j = 0; j < NSEG; j++) {

      int ipad = i * NSEG + j + 1;
      c->cd(ipad);

      if (i == j) {
        TLatex text;
        text.SetTextAlign(22);
        text.SetTextSize(0.18);
        text.DrawLatexNDC(0.5, 0.5, Form("%d = %d", i, j));
        continue;
      }

      if (!h_off_pair[i][j]) continue;

      h_off_pair[i][j]->SetLineColor(kBlack);
      h_off_pair[i][j]->Draw();

      if (f_off_pair[i][j]) {
        f_off_pair[i][j]->SetLineColor(kRed);
        f_off_pair[i][j]->Draw("same");
      }

      TLatex label;
      label.SetTextSize(0.10);
      label.SetNDC();

      if (has_toff[clusterID][i][j]) {
        label.DrawLatex(0.18, 0.82,
                        Form("%d-%d: %.1f ns", i, j,
                             t_off[clusterID][i][j]));
      } else {
        label.DrawLatex(0.18, 0.82,
                        Form("%d-%d: no fit", i, j));
      }
    }
  }

  c->Draw();
}


// ------------------------------------------------------------
// Choose reference segment by highest high-energy count
// ------------------------------------------------------------
int ChooseReferenceSegmentByHighCount(int clusterID)
{
  int bestSeg = -1;
  Long64_t bestCount = -1;

  for (int s = 0; s < NSEG; s++) {

    if (!has_fit[clusterID][s]) continue;

    Long64_t count = seg_high_count[clusterID][s];

    std::cout << "cluster " << clusterID
              << ", reference candidate segment " << s
              << ": high-energy count = "
              << count << std::endl;

    if (count > bestCount) {
      bestCount = count;
      bestSeg = s;
    }
  }

  return bestSeg;
}


// ------------------------------------------------------------
// Absorb segment offset into p0
// ------------------------------------------------------------
void absorb_segment_offset_to_p0(int clusterID)
{
  if (clusterID < 0 || clusterID >= NCLUSTER) return;

  int refSeg = ChooseReferenceSegmentByHighCount(clusterID);
  ref_seg_cluster[clusterID] = refSeg;

  if (refSeg < 0) {
    std::cout << "cluster " << clusterID
              << ": no valid reference segment found." << std::endl;
    return;
  }

  std::cout << "cluster " << clusterID
            << ": selected reference segment = "
            << refSeg << std::endl;

  // C_s = (t_s-t_j) + C_j：无直接 pair 时，沿有效参考关系传递。
  for (int s=0; s<NSEG; ++s) {
    seg_offset[clusterID][s]=0;
    has_seg_offset[clusterID][s]=(s==refSeg);
    // 优先保留直接参考；仅对缺少直接 pair 的通道使用传递。
    if (s!=refSeg && has_toff[clusterID][s][refSeg]) {
      seg_offset[clusterID][s]=t_off[clusterID][s][refSeg];
      has_seg_offset[clusterID][s]=1;
    }
  }
  for (int step=0; step<NSEG; ++step)
    for (int s=0; s<NSEG; ++s) {
      if (has_seg_offset[clusterID][s]) continue;
      for (int j=0; j<NSEG; ++j) {
        if (!has_seg_offset[clusterID][j] || !has_toff[clusterID][s][j]) continue;
        seg_offset[clusterID][s]=t_off[clusterID][s][j]+seg_offset[clusterID][j];
        has_seg_offset[clusterID][s]=1;
        break;
      }
    }

  for (int s = 0; s < NSEG; s++) {
    if (!has_fit[clusterID][s] || !f_tw[clusterID][s]) continue;
    double C = seg_offset[clusterID][s];
    if (!has_seg_offset[clusterID][s]) {
      std::cout << "cluster " << clusterID
                << ", segment " << s
                << ": no connected offset path to reference segment "
                << refSeg
                << ", keep this channel uncorrected" << std::endl;
      has_fit[clusterID][s] = 0;
      continue;
    }

    seg_offset[clusterID][s] = C;

    // Shift p0 so that f(E_REF) = C.
    double fref = f_tw[clusterID][s]->Eval(E_REF);
    double p0_old = f_tw[clusterID][s]->GetParameter(0);
    double p0_new = p0_old - fref + C;

    f_tw[clusterID][s]->SetParameter(0, p0_new);

    std::cout << "cluster " << clusterID
              << ", segment " << s
              << ": C = " << C
              << " ns, p0 -> " << p0_new
              << std::endl;
  }
}


// ------------------------------------------------------------
// Fit time-walk functions for current cluster
// ------------------------------------------------------------
void fit_pair_timewalk_cluster(int clusterID = 6, bool draw = true)
{
  if (clusterID < 0 || clusterID >= NCLUSTER) {
    std::cout << "invalid clusterID" << std::endl;
    return;
  }

  double fitEmin = 30.0;
  double fitEmax = 800.0;

  double dtMin = -400.0;
  double dtMax = 400.0;

  TCanvas *c = 0;

  if (draw) {
    TCanvas *c_old = (TCanvas*)gROOT->FindObject("c_fit_tw");
    if (c_old) delete c_old;

    c = new TCanvas("c_fit_tw",
                    Form("cluster %d time-walk fits", clusterID),
                    900, 600);

    c->Divide(4, 2);
    c->SetLogy(0);
  }

  for (int s = 0; s < NSEG; s++) {

    has_fit[clusterID][s] = 0;

    if (!h_tw_id[s]) continue;
    if (h_tw_id[s]->GetEntries() < 100) continue;

    int xbin1 = h_tw_id[s]->GetXaxis()->FindBin(dtMin);
    int xbin2 = h_tw_id[s]->GetXaxis()->FindBin(dtMax);

    if (hp_tw_id[s]) {
      delete hp_tw_id[s];
      hp_tw_id[s] = 0;
    }

    hp_tw_id[s] = h_tw_id[s]->ProfileY(Form("hp_tw_c%d_s%d", clusterID, s),
                                       xbin1, xbin2);

    hp_tw_id[s]->SetDirectory(0);

    if (f_tw[clusterID][s]) {
      delete f_tw[clusterID][s];
      f_tw[clusterID][s] = 0;
    }

    f_tw[clusterID][s] =
      new TF1(Form("f_tw_c%d_s%d", clusterID, s),
              "[0]+[1]/sqrt(x)+[2]/x+[3]/(x*x)",
              30.0, 1300.0);

    f_tw[clusterID][s]->SetParameters(0.0, 1000.0, -10000.0, 100000.0);

    int status = hp_tw_id[s]->Fit(f_tw[clusterID][s], "R0Q", "", fitEmin, fitEmax);
    if (status != 0) {
      std::cout << "Skip failed time-walk fit: " << clusterID << ", " << s << std::endl;
      continue;
    }

    has_fit[clusterID][s] = 1;

    std::cout << "cluster " << clusterID
              << ", segment " << s
              << " fit:"
              << " p0=" << f_tw[clusterID][s]->GetParameter(0)
              << ", p1=" << f_tw[clusterID][s]->GetParameter(1)
              << ", p2=" << f_tw[clusterID][s]->GetParameter(2)
              << ", p3=" << f_tw[clusterID][s]->GetParameter(3)
              << std::endl;

    if (draw) {
      c->cd(s + 1);
      gPad->SetLogy(0);

      hp_tw_id[s]->SetMarkerStyle(20);
      hp_tw_id[s]->SetMarkerSize(0.7);
      hp_tw_id[s]->SetMinimum(-300);
      hp_tw_id[s]->SetMaximum(300);

      hp_tw_id[s]->Draw();

      TF1 *f_draw = (TF1*)f_tw[clusterID][s]->Clone(
        Form("f_draw_c%d_s%d", clusterID, s)
      );

      f_draw->SetLineColor(kRed);
      f_draw->SetRange(30, 1300);
      f_draw->Draw("same");
    }
  }

  // After fitting walk shape, absorb high-energy segment offset into p0.
  absorb_segment_offset_to_p0(clusterID);

  if (draw) c->Draw();
}


// ------------------------------------------------------------
// Fit all clusters
// ------------------------------------------------------------
void fit_all_clusters_pair()
{
  for (int c = 0; c < NCLUSTER; c++) {

    std::cout << "======================================" << std::endl;
    std::cout << "Processing cluster " << c << std::endl;

    make_pair_timewalk_cluster(c);
    fit_pair_timewalk_cluster(c, false);
  }

  std::cout << "All cluster time-walk fits finished." << std::endl;
}


// ------------------------------------------------------------
// Evaluate final correction.
// p0 already includes high-energy offset.
// ------------------------------------------------------------
double GetTimeWalkCorrection(int clusterID, int segID, double E)
{
  if (clusterID < 0 || clusterID >= NCLUSTER) return 0.0;
  if (segID < 0 || segID >= NSEG) return 0.0;
  if (!has_fit[clusterID][segID]) return 0.0;
  if (!f_tw[clusterID][segID]) return 0.0;
  if (E <= 0) return 0.0;

  return f_tw[clusterID][segID]->Eval(E);
}


// ------------------------------------------------------------
// Generate corrected ROOT file
// ------------------------------------------------------------
void make_time_corrected_tree_pair(
    const char *inputFile = "eurica_event.root",
    const char *outputFile = "eurica_time_pair.root")
{
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
  int gid_in[MAXHIT];
  double ge_in[MAXHIT];
  double gt_in[MAXHIT];

  if (tin->GetMaximum("ghit")>MAXHIT)
    throw std::runtime_error("Increase MAXHIT before reading branches");

  tin->SetBranchAddress("ghit", &ghit);
  tin->SetBranchAddress("gid", gid_in);
  tin->SetBranchAddress("ge", ge_in);
  tin->SetBranchAddress("gt", gt_in);

  TFile *fout = new TFile(outputFile, "recreate");
  TTree *tout = new TTree("tree", "pair time-walk corrected tree");

  int o_ghit;
  int o_gid[MAXHIT];
  double o_ge[MAXHIT];
  double o_gt[MAXHIT];
  int o_tw_ok[MAXHIT];

  tout->Branch("ghit", &o_ghit, "ghit/I");
  tout->Branch("gid", o_gid, "gid[ghit]/I");
  tout->Branch("ge", o_ge, "ge[ghit]/D");
  tout->Branch("gt", o_gt, "gt[ghit]/D");
  tout->Branch("gt_raw", gt_in, "gt_raw[ghit]/D"); // 保留修正前的时间，便于复核
  tout->Branch("tw_ok", o_tw_ok, "tw_ok[ghit]/I");

  Long64_t nentries = tin->GetEntries();

  for (Long64_t ientry = 0; ientry < nentries; ientry++) {

    tin->GetEntry(ientry);

    o_ghit = ghit;

    for (int i = 0; i < ghit; i++) {

      int clusterID = gid_in[i] / 7;
      int segID = gid_in[i] % 7;

      double corr = GetTimeWalkCorrection(clusterID, segID, ge_in[i]);

      o_gid[i] = gid_in[i];
      o_ge[i] = ge_in[i];
      o_gt[i] = gt_in[i] - corr;
      o_tw_ok[i] = clusterID>=0 && clusterID<NCLUSTER && segID>=0 && segID<NSEG
                && has_fit[clusterID][segID] && ge_in[i]>0;
    }

    tout->Fill();
  }

  fout->cd();
  tout->Write();
  for (int c=0; c<NCLUSTER; ++c)
    for (int s=0; s<NSEG; ++s)
      if (has_fit[c][s] && f_tw[c][s]) f_tw[c][s]->Write();
  fout->Close();
  fin->Close();

  std::cout << "time-corrected file saved to "
            << outputFile << std::endl;
}
