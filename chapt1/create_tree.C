#include <TFile.h>
#include <TTree.h>
#include <TH1D.h>
#include <TRandom3.h>
#include <TMath.h>
#include <iostream>
#include <cmath>
void create_tree(){

  // 1. 常量声明
  const Int_t nEvents = 500000;
  const Double_t D = 5.0;      // m, 靶到探测器距离
  const Double_t L = 1.0;      // m, 探测器半长
  const Double_t T = 0.05;     // m, 厚度
  const Double_t Lambda = 3.8; // m, 衰减长度
  const Double_t Vsc = 0.075;  // m/ns, 光速



  const Double_t En0 = 100.0;    // MeV, 中子平均能量
  const Double_t Egmean = 15.0;      // MeV, Gamma能量
  const Double_t RatioGamma = 0.3;

  const Double_t sigt_floor = 0.5;    // 高能端极限 sigma (ns)
  const Double_t sigt_stat  = 2.0;   // 统计项系数 (ns*sqrt(ADC))

  const Double_t gL_qe = 10;   //ee to light；
  const Double_t gR_qe = 15;   //ee to light；

  const Double_t Rq = 0.1;     // 相对能量分辨率

  const Double_t t0L = 5.5;
  const Double_t t0R = 20.4;


  // 2. 声明 Tree 中的变量
  Double_t depth_true, path_true;
  Double_t x_true;  // 真实入射位置 (m)
  Double_t e_true;  // 真实能量
  Int_t pid;        // 0: Gamma, 1: Neutron
  Double_t tof_true;// 真实 TOF (ns)
  Double_t tL_true, tR_true;  // 探测器时间
  Double_t tL, tR;  // 探测器时间
  Double_t qL, qR;  // 探测器能量
  Double_t AL, AR;  // 探测器能量

  // 3. 定义文件与 Tree
  TFile *opf = new TFile("tree_demo.root", "recreate");
  TTree *opt = new TTree("tree", "Simulated Data");

  opt->Branch("depth_true", &depth_true, "depth_true/D");
  opt->Branch("path_true", &path_true, "path_true/D");
  opt->Branch("x_true", &x_true, "x_true/D");
  opt->Branch("e_true", &e_true, "e_true/D");
  opt->Branch("tof_true", &tof_true, "tof_true/D");
  opt->Branch("pid", &pid, "pid/I");
  opt->Branch("tL_true", &tL_true, "tL_true/D");
  opt->Branch("tR_true", &tR_true, "tR_true/D");
  opt->Branch("tL", &tL, "tL/D");
  opt->Branch("tR", &tR, "tR/D");
  opt->Branch("AL", &AL, "AL/D");
  opt->Branch("AR", &AR, "AR/D");

  TH1D *htof = new TH1D("htof", "Mean end time;Mean end time (ns);Counts", 1000, 0, 100);
  TRandom3 *gr = new TRandom3(1101);

   std::cout << "Starting Simulation..." << std::endl;

  // 4. 事件循环
  for(int i = 0; i < nEvents; i++){

     // --- 进度条提示输出 (每5%刷新一次) ---
    if (i % (nEvents / 20) == 0) {
        Double_t progress = (Double_t)i / nEvents * 100;
        std::cout << "\rProcessing: " << (int)progress << "% completed..." << std::flush;
    }
    // --- 生成真值 ---
    x_true = gr->Uniform(-L, L);
    depth_true = gr->Uniform(-T/2.0, T/2.0); // 深度 y'
    Double_t dis = TMath::Sqrt(pow(D + depth_true, 2) + pow(x_true, 2)); // 真实距离

    path_true = dis;
    Double_t E_dep = 0; // 沉积能量 (产生光信号的能量)
    if(gr->Uniform() < RatioGamma) { // Gamma
       pid = 0;
       e_true = gr->Exp(Egmean);
       tof_true = dis / 0.299792458; // m -> ns
       E_dep = e_true;// Gamma沉积能量
    } else { // Neutron
        pid = 1;
        e_true = En0; //中子能量，
        if(e_true <= 0) continue;
        tof_true = dis / (0.299792458 * sqrt(1-pow(1+e_true/939.565,-2))) ;
        E_dep = e_true;//中子能量沉积
    }

    // --- 探测器响应 ---
    // 时间信号

    tL_true = tof_true + (L + x_true)/Vsc + t0L; // x 定义方向

    tL = gr->Gaus(tL_true, sigt_floor);

    tR_true = tof_true + (L - x_true)/Vsc + t0R;
    tR = gr->Gaus(tR_true, sigt_floor);

    // 能量信号
    // 此处简化：暂不考虑反冲质子能量分布

    Double_t Q = E_dep;
    qL = (Q/2.0) * TMath::Exp(-(L + x_true)/Lambda);
    qL = gr->Gaus(qL, qL * Rq/2.355);
    AL = gL_qe * qL;

    qR = (Q/2.0) * TMath::Exp(-(L - x_true)/Lambda);
    qR = gr->Gaus(qR, qR * Rq/2.355);
    AR = gR_qe * qR;

    if (AL < 0 || AR < 0) continue;

    // 在线重构
    double tof_rec = (tL + tR)/2.0;

    htof->Fill(tof_rec); //填充histogram
    //5.将计算好的变量值填到Tree中
    opt->Fill();
  }
  // 完成后输出 100%
  std::cout << "\rProcessing: 100% completed!      " << std::endl;
  // 6.将数据写入root文件中
  htof->Write();
  opt->Write();
  opf->Close();

  std::cout << "Data saved to tree_demo.root" << std::endl;
}
