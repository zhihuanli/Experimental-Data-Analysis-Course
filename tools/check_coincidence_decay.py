"""Read-only scientific invariants for the chapter-5/6 example outputs."""
from pathlib import Path
import hashlib
import ROOT

base=Path(__file__).resolve().parents[1]
ROOT.gROOT.SetBatch(True)
for original,copy in [
    ('materials/chapt4/gamma-gamma/eurica.root','chapt4/eurica.root'),
    ('materials/chapt5/alpha.root','chapt5/alpha.root'),
    ('materials/chapt5/mwpc.root','chapt5/mwpc.root')]:
    def digest(name):
        with (base/name).open('rb') as stream:
            return hashlib.file_digest(stream,'sha256').hexdigest()
    assert digest(original)==digest(copy),(original,copy)
    print('PASS unchanged input',copy,flush=True)

ROOT.gInterpreter.Declare(r'''
#include <TFile.h>
#include <TTree.h>
#include <TH2.h>
#include <cmath>
#include <stdexcept>
#include <iostream>
void check_gamma_stages(const char *dir) {
    TFile raw((std::string(dir)+"/eurica_event.root").c_str());
    TFile corrected((std::string(dir)+"/eurica_time_pair.root").c_str());
    TFile added((std::string(dir)+"/eurica_addback.root").c_str());
    auto a=(TTree*)raw.Get("tree"), b=(TTree*)corrected.Get("tree"), c=(TTree*)added.Get("tree");
    if (a->GetEntries()!=b->GetEntries() || a->GetEntries()!=c->GetEntries())
        throw std::runtime_error("Event counts changed");
    constexpr int capacity=1024;
    int na,nb,nc,nadd,ia[capacity],ib[capacity],ic[capacity],ok[capacity];
    double ea[capacity],eb[capacity],ec[capacity],ta[capacity],tb[capacity],tc[capacity],tr[capacity],ae[capacity];
    TTree *trees[]={a,b,c}; int *counts[]={&na,&nb,&nc};
    int *ids[]={ia,ib,ic}; double *energies[]={ea,eb,ec}, *times[]={ta,tb,tc};
    for (int k=0;k<3;++k) {
        if (trees[k]->GetMaximum("ghit")>capacity) throw std::runtime_error("Array capacity");
        trees[k]->SetBranchAddress("ghit",counts[k]);
        trees[k]->SetBranchAddress("gid",ids[k]);
        trees[k]->SetBranchAddress("ge",energies[k]);
        trees[k]->SetBranchAddress("gt",times[k]);
    }
    b->SetBranchAddress("gt_raw",tr); b->SetBranchAddress("tw_ok",ok);
    c->SetBranchAddress("ahit",&nadd); c->SetBranchAddress("ae",ae);
    Long64_t hits=0,uncorrected=0; double maxEnergyDifference=0;
    for (Long64_t n=0;n<a->GetEntries();++n) {
        a->GetEntry(n); b->GetEntry(n); c->GetEntry(n);
        if (na!=nb || na!=nc) throw std::runtime_error("Hit multiplicity changed");
        double before=0,after=0;
        for (int i=0;i<na;++i) {
            if (ia[i]!=ib[i] || ia[i]!=ic[i] || ea[i]!=eb[i] || ea[i]!=ec[i]
                || ta[i]!=tr[i] || tb[i]!=tc[i]) throw std::runtime_error("Hit identity or raw value changed");
            if (!std::isfinite(tb[i])) throw std::runtime_error("Nonfinite corrected time");
            if (!ok[i]) { ++uncorrected; if (tb[i]!=ta[i]) throw std::runtime_error("Invalid channel was corrected"); }
            before+=ea[i];
        }
        for (int i=0;i<nadd;++i) after+=ae[i];
        maxEnergyDifference=std::max(maxEnergyDifference,std::abs(after-before));
        if (std::abs(after-before)>1e-8*std::max(1.0,std::abs(before))) throw std::runtime_error("Addback energy not conserved");
        hits+=na;
    }
    std::cout << "PASS stage identities: " << a->GetEntries() << " events, " << hits << " hits; uncorrected=" << uncorrected
              << "; max addback energy difference=" << maxEnergyDifference << " keV\n";
}
void check_matrix(const char *filename) {
    TFile f(filename);
    auto raw=(TH2*)f.Get("hgg_input"), bg=(TH2*)f.Get("hggb_radware"), net=(TH2*)f.Get("hgg_radware");
    Long64_t negative=0;
    for (int i=1;i<=raw->GetNbinsX();++i) for (int j=1;j<=raw->GetNbinsY();++j) {
        double r=raw->GetBinContent(i,j), b=bg->GetBinContent(i,j), n=net->GetBinContent(i,j);
        if (r!=raw->GetBinContent(j,i) || std::abs(n-net->GetBinContent(j,i))>1e-8)
            throw std::runtime_error("Matrix is not symmetric");
        if (std::abs(n-(r-b))>1e-8) throw std::runtime_error("Subtraction differs");
        if (n<0) ++negative;
    }
    std::cout << "PASS matrix symmetry and subtraction; negative bins retained=" << negative << "\n";
}
''')
ROOT.check_gamma_stages(str(base/'chapt4'))
ROOT.check_matrix(str(base/'chapt4/eurica_gg_radware.root'))

source=ROOT.TFile.Open(str(base/'chapt5/sort1.root'))
tree=source.Get('tree')
total=tree.GetEntries()
with_mwpc=tree.GetEntries('me>0')
without_mwpc=tree.GetEntries('me<0')
assert total==with_mwpc+without_mwpc
assert tree.GetEntries('xstrip<0 || xstrip>47 || ystrip<0 || ystrip>127')==0
decayfile=ROOT.TFile.Open(str(base/'chapt5/decay.root'))
decay=decayfile.Get('tree')
assert decay.GetEntries()==with_mwpc
assert decay.GetEntries('bhit==0')>0
print('PASS decay partitions:',total,with_mwpc,without_mwpc,
      '; zero-candidate implants retained:',decay.GetEntries('bhit==0'),flush=True)
