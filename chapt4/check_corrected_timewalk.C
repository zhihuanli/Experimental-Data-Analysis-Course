
#include <iostream>

const int MAXHIT = 1024;
const int NCLUSTER = 12;
const int NSEG = 7;

// high-reference walk:
//   E_i vs t_i-t_j, with E_i > EminTarget and E_j > EminRef
TH2F *h_walk_cluster[NCLUSTER] = {0};

// all-energy walk:
//   E_i vs t_i-t_j, no energy gate
TH2F *h_walk_cluster_allE[NCLUSTER] = {0};

// high-energy time difference:
//   t_i-t_j, with E_i > EminRef and E_j > EminRef
TH1F *h_dt_cluster[NCLUSTER] = {0};
TH1F *h_dt_all = 0;

// all-energy time difference:
//   t_i-t_j, no energy gate
TH1F *h_dt_cluster_allE[NCLUSTER] = {0};
TH1F *h_dt_all_allE = 0;

TF1 *f_dt_cluster[NCLUSTER] = {0};
TF1 *f_dt_cluster_allE[NCLUSTER] = {0};

TF1 *f_dt_all = 0;
TF1 *f_dt_all_allE = 0;

// Make corrected walk plots and time-difference spectra
void make_corrected_cluster_walk(
    const char *filename = "eurica_time_pair.root",
    double EminTarget = 30.0,
    double EminRef = 600.0)
{
  TH1::AddDirectory(kFALSE);
  for (int c = 0; c < NCLUSTER; c++) {
    if (h_walk_cluster[c]) {
      delete h_walk_cluster[c];
      h_walk_cluster[c] = 0;
    }

    h_walk_cluster[c] =
      new TH2F(Form("h_walk_cluster_%d", c),
               Form("cluster %d: corrected walk, E_{ref}>%.0f; t_i-t_j (ns); E_i",
                    c, EminRef),
               120, -600, 600,
               130, 0, 1300);

    h_walk_cluster[c]->SetDirectory(0);
    if (h_walk_cluster_allE[c]) {
      delete h_walk_cluster_allE[c];
      h_walk_cluster_allE[c] = 0;
    }

    h_walk_cluster_allE[c] =
      new TH2F(Form("h_walk_cluster_allE_%d", c),
               Form("cluster %d: corrected walk, all energy; t_i-t_j (ns); E_i",
                    c),
               120, -600, 600,
               130, 0, 1300);

    h_walk_cluster_allE[c]->SetDirectory(0);
    if (h_dt_cluster[c]) {
      delete h_dt_cluster[c];
      h_dt_cluster[c] = 0;
    }

    h_dt_cluster[c] =
      new TH1F(Form("h_dt_cluster_%d", c),
               Form("cluster %d: high-energy time difference; t_i-t_j (ns); counts",
                    c),
               240, -600, 600);

    h_dt_cluster[c]->SetDirectory(0);
    if (h_dt_cluster_allE[c]) {
      delete h_dt_cluster_allE[c];
      h_dt_cluster_allE[c] = 0;
    }

    h_dt_cluster_allE[c] =
      new TH1F(Form("h_dt_cluster_allE_%d", c),
               Form("cluster %d: all-energy time difference; t_i-t_j (ns); counts",
                    c),
               240, -600, 600);

    h_dt_cluster_allE[c]->SetDirectory(0);
  }
  if (h_dt_all) {
    delete h_dt_all;
    h_dt_all = 0;
  }

  h_dt_all =
    new TH1F("h_dt_all",
             "high-energy time difference: all clusters; t_i-t_j (ns); counts",
             240, -600, 600);

  h_dt_all->SetDirectory(0);
  if (h_dt_all_allE) {
    delete h_dt_all_allE;
    h_dt_all_allE = 0;
  }

  h_dt_all_allE =
    new TH1F("h_dt_all_allE",
             "all-energy time difference: all clusters; t_i-t_j (ns); counts",
             240, -600, 600);

  h_dt_all_allE->SetDirectory(0);

  TFile *fin = new TFile(filename);
  if (!fin || fin->IsZombie()) {
    std::cout << "cannot open " << filename << std::endl;
    return;
  }

  TTree *tree = (TTree*)fin->Get("tree");
  if (!tree) {
    std::cout << "cannot find tree in " << filename << std::endl;
    fin->Close();
    return;
  }

  int ghit;
  int gid[MAXHIT];
  double ge[MAXHIT];
  double gt[MAXHIT];

  if (tree->GetMaximum("ghit") > MAXHIT)
    throw std::runtime_error("Increase MAXHIT before reading branches");
  tree->SetBranchAddress("ghit", &ghit);
  tree->SetBranchAddress("gid", gid);
  tree->SetBranchAddress("ge", ge);
  tree->SetBranchAddress("gt", gt);

  Long64_t nentries = tree->GetEntries();
  for (Long64_t ientry = 0; ientry < nentries; ientry++) {

    tree->GetEntry(ientry);
    for (int a = 0; a < ghit; a++) {

      int cluster_a = gid[a] / 7;
      int seg_a = gid[a] % 7;
      if (cluster_a < 0 || cluster_a >= NCLUSTER) continue;
      if (seg_a < 0 || seg_a >= NSEG) continue;
      for (int b = 0; b < ghit; b++) {
        if (a == b) continue;

        int cluster_b = gid[b] / 7;
        int seg_b = gid[b] % 7;
        if (cluster_b != cluster_a) continue;
        if (seg_b < 0 || seg_b >= NSEG) continue;
        if (seg_b == seg_a) continue;

        double dt = gt[a] - gt[b];

        // Walk plots

        // all-energy walk: no energy gate
        h_walk_cluster_allE[cluster_a]->Fill(dt, ge[a]);

        // high-reference walk:
        // target hit can be low energy; reference hit is high energy
        if (ge[a] >= EminTarget && ge[b] >= EminRef) {
          h_walk_cluster[cluster_a]->Fill(dt, ge[a]);
        }

        // Time-difference spectra
        // Fill each detector pair once.
        // Use gid ordering, not array ordering.
        if (gid[a] >= gid[b]) continue;

        // all-energy time difference
        h_dt_cluster_allE[cluster_a]->Fill(dt);
        h_dt_all_allE->Fill(dt);

        // high-energy time difference
        if (ge[a] >= EminRef && ge[b] >= EminRef) {
          h_dt_cluster[cluster_a]->Fill(dt);
          h_dt_all->Fill(dt);
        }
      }
    }
  }

  fin->Close();
  for (int c = 0; c < NCLUSTER; c++) {
    std::cout << "cluster " << c
              << " high-ref walk entries = "
              << h_walk_cluster[c]->GetEntries()
              << ", all-energy walk entries = "
              << h_walk_cluster_allE[c]->GetEntries()
              << ", high-energy dt entries = "
              << h_dt_cluster[c]->GetEntries()
              << ", all-energy dt entries = "
              << h_dt_cluster_allE[c]->GetEntries()
              << std::endl;
  }

  std::cout << "all high-energy dt entries = "
            << h_dt_all->GetEntries()
            << std::endl;

  std::cout << "all all-energy dt entries = "
            << h_dt_all_allE->GetEntries()
            << std::endl;
}

// Draw corrected walk plots: high-reference version
void draw_corrected_cluster_walk()
{
  TCanvas *c_old = (TCanvas*)gROOT->FindObject("c_corr_cluster_walk");
  if (c_old) delete c_old;

  TCanvas *c = new TCanvas("c_corr_cluster_walk",
                           "corrected walk by cluster: high-reference",
                           900, 600);

  c->Divide(4, 3);
  gStyle->SetOptStat(0);
  for (int ic = 0; ic < NCLUSTER; ic++) {
    c->cd(ic + 1);
    gPad->SetLogz(0);
    if (h_walk_cluster[ic]) {
      h_walk_cluster[ic]->Draw("colz");
    }
  }

  c->Draw();
}

// Draw corrected walk plots: all-energy version
void draw_corrected_cluster_walk_allE()
{
  TCanvas *c_old = (TCanvas*)gROOT->FindObject("c_corr_cluster_walk_allE");
  if (c_old) delete c_old;

  TCanvas *c = new TCanvas("c_corr_cluster_walk_allE",
                           "corrected walk by cluster: all energy",
                           900, 600);

  c->Divide(4, 3);
  gStyle->SetOptStat(0);
  for (int ic = 0; ic < NCLUSTER; ic++) {
    c->cd(ic + 1);
    gPad->SetLogz(0);
    if (h_walk_cluster_allE[ic]) {
      h_walk_cluster_allE[ic]->Draw("colz");
    }
  }

  c->Draw();
}

// Draw high-energy time-difference spectra by cluster
void draw_corrected_dt_by_cluster()
{
  TCanvas *c_old = (TCanvas*)gROOT->FindObject("c_corr_dt_cluster");
  if (c_old) delete c_old;

  TCanvas *c = new TCanvas("c_corr_dt_cluster",
                           "high-energy time difference by cluster",
                           900, 600);

  c->Divide(4, 3);
  gStyle->SetOptStat(0);
  for (int ic = 0; ic < NCLUSTER; ic++) {

    c->cd(ic + 1);
    gPad->SetLogy(0);
    if (!h_dt_cluster[ic]) continue;
    if (f_dt_cluster[ic]) {
      delete f_dt_cluster[ic];
      f_dt_cluster[ic] = 0;
    }
    if (h_dt_cluster[ic]->GetEntries() < 20) {
      h_dt_cluster[ic]->Draw("hist");
      continue;
    }

    int maxbin = h_dt_cluster[ic]->GetMaximumBin();
    double x0 = h_dt_cluster[ic]->GetBinCenter(maxbin);

    f_dt_cluster[ic] =
      new TF1(Form("f_dt_cluster_%d", ic),
              "gaus",
              x0 - 50.0,
              x0 + 50.0);

    f_dt_cluster[ic]->SetParameter(0, h_dt_cluster[ic]->GetMaximum());
    f_dt_cluster[ic]->SetParameter(1, x0);
    f_dt_cluster[ic]->SetParameter(2, 60.0);

    h_dt_cluster[ic]->Fit(f_dt_cluster[ic], "RQ0");

    h_dt_cluster[ic]->Draw("hist");
    f_dt_cluster[ic]->SetLineColor(kRed);
    f_dt_cluster[ic]->Draw("same");

    std::cout << "high-energy cluster " << ic
              << ": mean = " << f_dt_cluster[ic]->GetParameter(1)
              << " ns, sigma = " << f_dt_cluster[ic]->GetParameter(2)
              << " ns"
              << std::endl;
  }

  c->Draw();
}

// Draw all-energy time-difference spectra by cluster
void draw_corrected_dt_by_cluster_allE()
{
  TCanvas *c_old = (TCanvas*)gROOT->FindObject("c_corr_dt_cluster_allE");
  if (c_old) delete c_old;

  TCanvas *c = new TCanvas("c_corr_dt_cluster_allE",
                           "all-energy time difference by cluster",
                           900, 600);

  c->Divide(4, 3);
  gStyle->SetOptStat(0);
  for (int ic = 0; ic < NCLUSTER; ic++) {

    c->cd(ic + 1);
    gPad->SetLogy(0);
    if (!h_dt_cluster_allE[ic]) continue;
    if (f_dt_cluster_allE[ic]) {
      delete f_dt_cluster_allE[ic];
      f_dt_cluster_allE[ic] = 0;
    }
    if (h_dt_cluster_allE[ic]->GetEntries() < 20) {
      h_dt_cluster_allE[ic]->Draw("hist");
      continue;
    }

    int maxbin = h_dt_cluster_allE[ic]->GetMaximumBin();
    double x0 = h_dt_cluster_allE[ic]->GetBinCenter(maxbin);

    f_dt_cluster_allE[ic] =
      new TF1(Form("f_dt_cluster_allE_%d", ic),
              "gaus",
              x0 - 100.0,
              x0 + 100.0);

    f_dt_cluster_allE[ic]->SetParameter(0, h_dt_cluster_allE[ic]->GetMaximum());
    f_dt_cluster_allE[ic]->SetParameter(1, x0);
    f_dt_cluster_allE[ic]->SetParameter(2, 60.0);

    h_dt_cluster_allE[ic]->Fit(f_dt_cluster_allE[ic], "RQ0");

    h_dt_cluster_allE[ic]->Draw("hist");
    f_dt_cluster_allE[ic]->SetLineColor(kRed);
    f_dt_cluster_allE[ic]->Draw("same");

    std::cout << "all-energy cluster " << ic
              << ": mean = " << f_dt_cluster_allE[ic]->GetParameter(1)
              << " ns, sigma = " << f_dt_cluster_allE[ic]->GetParameter(2)
              << " ns"
              << std::endl;
  }

  c->Draw();
}

// Draw cumulative high-energy time-difference spectrum
void draw_corrected_dt_all()
{
  TCanvas *c_old = (TCanvas*)gROOT->FindObject("c_corr_dt_all");
  if (c_old) delete c_old;

  TCanvas *c = new TCanvas("c_corr_dt_all",
                           "cumulative high-energy time difference",
                           800, 600);

  c->SetLogy();
  if (!h_dt_all) {
    std::cout << "h_dt_all does not exist. Run make_corrected_cluster_walk() first."
              << std::endl;
    return;
  }
  if (f_dt_all) {
    delete f_dt_all;
    f_dt_all = 0;
  }
  if (h_dt_all->GetEntries() < 20) {
    h_dt_all->Draw("hist");
    c->Draw();
    return;
  }

  int maxbin = h_dt_all->GetMaximumBin();
  double x0 = h_dt_all->GetBinCenter(maxbin);

  f_dt_all =
    new TF1("f_dt_all",
            "gaus",
            x0 - 100.0,
            x0 + 100.0);

  f_dt_all->SetParameter(0, h_dt_all->GetMaximum());
  f_dt_all->SetParameter(1, x0);
  f_dt_all->SetParameter(2, 60.0);

  h_dt_all->Fit(f_dt_all, "RQ0");

  h_dt_all->Draw("hist");
  f_dt_all->SetLineColor(kRed);
  f_dt_all->Draw("same");

  c->Draw();

  std::cout << "all clusters high-energy:"
            << " mean = " << f_dt_all->GetParameter(1)
            << " ns, sigma = " << f_dt_all->GetParameter(2)
            << " ns"
            << std::endl;
}

// Draw cumulative all-energy time-difference spectrum
void draw_corrected_dt_all_allE()
{
  TCanvas *c_old = (TCanvas*)gROOT->FindObject("c_corr_dt_all_allE");
  if (c_old) delete c_old;

  TCanvas *c = new TCanvas("c_corr_dt_all_allE",
                           "cumulative all-energy time difference",
                           800, 600);

  c->SetLogy();
  if (!h_dt_all_allE) {
    std::cout << "h_dt_all_allE does not exist. Run make_corrected_cluster_walk() first."
              << std::endl;
    return;
  }
  if (f_dt_all_allE) {
    delete f_dt_all_allE;
    f_dt_all_allE = 0;
  }
  if (h_dt_all_allE->GetEntries() < 20) {
    h_dt_all_allE->Draw("hist");
    c->Draw();
    return;
  }

  int maxbin = h_dt_all_allE->GetMaximumBin();
  double x0 = h_dt_all_allE->GetBinCenter(maxbin);

  f_dt_all_allE =
    new TF1("f_dt_all_allE",
            "gaus",
            x0 - 200.0,
            x0 + 200.0);

  f_dt_all_allE->SetParameter(0, h_dt_all_allE->GetMaximum());
  f_dt_all_allE->SetParameter(1, x0);
  f_dt_all_allE->SetParameter(2, 60.0);

  h_dt_all_allE->Fit(f_dt_all_allE, "RQ0");

  h_dt_all_allE->Draw("hist");
  f_dt_all_allE->SetLineColor(kRed);

  f_dt_all_allE->Draw("same");

  c->Draw();

  std::cout << "all clusters all-energy:"
            << " mean = " << f_dt_all_allE->GetParameter(1)
            << " ns, sigma = " << f_dt_all_allE->GetParameter(2)
            << " ns"
            << std::endl;
}
