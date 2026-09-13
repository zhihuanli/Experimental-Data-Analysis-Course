#include "ana.h"
#include <TH2.h>
#include <TStyle.h>
#include <TCanvas.h>
#include <TF1.h>
#include <TGraphErrors.h>   // 【修改】必须包含带有误差的图类
#include <TFitResult.h>
#include <TMatrixDSym.h>    // 【新增】用于接收协方差矩阵
#include <iostream>
#include <cmath>

using namespace std;

void ana::SetBranch(TTree *tree)
{
    tree->Branch("source_entry", &source_entry, "source_entry/L");
    tree->Branch("xx", xx, "xx[3]/D");
    tree->Branch("xz", xz, "xz[3]/D");
    tree->Branch("yy", yy, "yy[3]/D");
    tree->Branch("yz", yz, "yz[3]/D");
    tree->Branch("dx", dx, "dx[3]/D");
    tree->Branch("dy", dy, "dy[3]/D");
    tree->Branch("xx2b", xx2b, "xx2b[2]/D");
    tree->Branch("yy2b", yy2b, "yy2b[2]/D");
    tree->Branch("anode2b", &anode2b, "anode2b/D");

    // 【新增】注册所有运动学中心值及其物理误差
    tree->Branch("tx", &tx, "tx/D");
    tree->Branch("ty", &ty, "ty/D");
    tree->Branch("theta_x", &theta_x, "theta_x/D");
    tree->Branch("theta_y", &theta_y, "theta_y/D");
    tree->Branch("sigma_tx", &sigma_tx, "sigma_tx/D");
    tree->Branch("sigma_ty", &sigma_ty, "sigma_ty/D");
    tree->Branch("sigma_thetax", &sigma_thetax, "sigma_thetax/D");
    tree->Branch("sigma_thetay", &sigma_thetay, "sigma_thetay/D");

    tree->Branch("c2nx", &c2nx, "c2nx/D");
    tree->Branch("c2ny", &c2ny, "c2ny/D");
    tree->Branch("beamTrig", &beamTrig, "beamTrig/I");
    tree->Branch("must2Trig", &must2Trig, "must2Trig/I");
    tree->Branch("targetX", &targetX, "targetX/F");
    tree->Branch("targetY", &targetY, "targetY/F");
}

void ana::TrackInit()
{
    // 初始化所有计算变量为无效值，防止上一个事件的数据污染
    tx = -999; ty = -999;
    c2nx = -1; c2ny = -1;
    for (int i=0;i<3;++i) { dx[i]=-999; dy[i]=-999; }
    theta_x = -999; theta_y = -999;
    sigma_tx = -1; sigma_ty = -1;             // 误差初始化为负数代表无效
    sigma_thetax = -1; sigma_thetay = -1;

    xx[0] = PPACF8[0][0];  yy[0] = PPACF8[0][1];  xz[0] = PPACF8[0][2];  yz[0] = PPACF8[0][3];
    xx[1] = PPACF8[2][0];  yy[1] = PPACF8[2][1];  xz[1] = PPACF8[2][2];  yz[1] = PPACF8[2][3];
    xx[2] = PPACF8[4][0];  yy[2] = PPACF8[4][1];  xz[2] = PPACF8[4][2];  yz[2] = PPACF8[4][3];

    xx2b[0] = PPACF8[3][0]; yy2b[0] = PPACF8[3][1];
    xz2b    = PPACF8[3][2]; yz2b    = PPACF8[3][3];
    anode2b = PPACF8[3][4];

    xx2b[1] = -1000; yy2b[1] = -1000;
}

void ana::SetTrace(TH2D *h, Double_t k, Double_t b, Int_t min, Int_t max){
    if(h == 0 || min >= max) return;
    for(int i = min; i < max; i++){
        h->Fill(i, i * k + b);
    }
}

void ana::Analysis()
{
    TTree *tree = fOutTree;
    if (fChain == 0) return;

    SetBranch(tree);

    TH2D *htf8xz = new TH2D("htf8xz", "X-Z Plane Trace; Z (mm); X (mm)", 2200, -2000, 200, 300, -150, 150);
    TH2D *htf8yz = new TH2D("htf8yz", "Y-Z Plane Trace; Z (mm); Y (mm)", 2200, -2000, 200, 300, -150, 150);

    // 【核心修改】使用 TGraphErrors 替代 TGraph，输入假设的单层位置误差
    TGraphErrors *grx = new TGraphErrors(3);
    TGraphErrors *gry = new TGraphErrors(3);
    TF1 *fx = new TF1("fx", "pol1", -2000, 0);
    TF1 *fy = new TF1("fy", "pol1", -2000, 0);

    // 假设：所有PPAC每层的本征位置分辨率为 1.0 mm
    const double det_resolution = 1.0;
    const double z_target = 0.0; // 物理靶所在Z坐标位置

    Long64_t nentries = fChain->GetEntriesFast();
    Long64_t nbytes = 0, nb = 0;

    for (Long64_t jentry = 0; jentry < nentries; jentry++) {
        Long64_t ientry = LoadTree(jentry);
        if (ientry < 0) break;
        nb = fChain->GetEntry(jentry);   nbytes += nb;

        source_entry = jentry;
        TrackInit();

        bool b1a = abs(xx[0]) < 150 && abs(yy[0]) < 150;
        bool b2a = abs(xx[1]) < 150 && abs(yy[1]) < 150;
        bool b3  = abs(xx[2]) < 100 && abs(yy[2]) < 100;
        if(!b1a || !b2a || !b3) continue;

        // ================= X-Z 平面径迹拟合与误差计算 =================
        for(int i=0; i<3; i++) {
            grx->SetPoint(i, xz[i], xx[i]);
            grx->SetPointError(i, 0.0, det_resolution); // 关键：输入Z和X的误差
        }

        // 【核心修改】去除 "W" 选项。S=保存结果(以获取矩阵), Q=静默模式
        TFitResultPtr rx = grx->Fit(fx, "SQN");

        if (int(rx)==0 && rx.Get() && rx->IsValid()) {
            double p0_x = fx->GetParameter(0);
            double p1_x = fx->GetParameter(1);

            // 提取中心值
            xx2b[1] = fx->Eval(xz2b);
            tx      = p0_x + p1_x * z_target;
            theta_x = atan(p1_x); // 物理出射角 (rad)

            // 提取协方差矩阵并计算严谨物理误差
            TMatrixDSym cov_x = rx->GetCovarianceMatrix();
            double var_p0 = cov_x(0, 0);
            double var_p1 = cov_x(1, 1);
            double cov_p0_p1 = cov_x(0, 1);

            // 外推位置误差传递公式
            double err2_tx = var_p0 + (z_target * z_target * var_p1) + (2.0 * z_target * cov_p0_p1);
            sigma_tx = sqrt(err2_tx);

            // 角度非线性误差传递公式
            sigma_thetax = sqrt(var_p1) / (1.0 + p1_x * p1_x);

            c2nx = rx->Chi2() / rx->Ndf();
            if (jentry < 10000) SetTrace(htf8xz, p1_x, p0_x, -1800, 0);
            for(int i=0; i<3; i++) dx[i] = xx[i] - fx->Eval(xz[i]);
        }

        // ================= Y-Z 平面径迹拟合与误差计算 =================
        for(int i=0; i<3; i++) {
            gry->SetPoint(i, yz[i], yy[i]);
            gry->SetPointError(i, 0.0, det_resolution);
        }

        TFitResultPtr ry = gry->Fit(fy, "SQN");

        if (int(ry)==0 && ry.Get() && ry->IsValid()) {
            double p0_y = fy->GetParameter(0);
            double p1_y = fy->GetParameter(1);

            yy2b[1] = fy->Eval(yz2b);
            ty      = p0_y + p1_y * z_target;
            theta_y = atan(p1_y);

            TMatrixDSym cov_y = ry->GetCovarianceMatrix();
            double var_p0 = cov_y(0, 0);
            double var_p1 = cov_y(1, 1);
            double cov_p0_p1 = cov_y(0, 1);

            double err2_ty = var_p0 + (z_target * z_target * var_p1) + (2.0 * z_target * cov_p0_p1);
            sigma_ty = sqrt(err2_ty);

            sigma_thetay = sqrt(var_p1) / (1.0 + p1_y * p1_y);

            c2ny = ry->Chi2() / ry->Ndf();
            if (jentry < 10000) SetTrace(htf8yz, p1_y, p0_y, -1800, 0);
            for(int i=0; i<3; i++) dy[i] = yy[i] - fy->Eval(yz[i]);
        }

        // 将本事件结果写入 Tree (包括新算出的误差)
        if (c2nx>=0 && c2ny>=0) tree->Fill();

        if(jentry % 10000 == 0) cout << "Processing Event: " << jentry << " / " << nentries << endl;
    }

    // 释放内存并保存结果
    delete grx; delete gry;
    delete fx;  delete fy;




    cout << "Input events=" << nentries << ", accepted reference tracks=" << tree->GetEntries() << endl;



}

