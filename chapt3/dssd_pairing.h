#ifndef DSSD_PAIRING_H
#define DSSD_PAIRING_H
#include <cmath>

// 两条互不相邻的 X，三条 Y 中恰有一组相邻条。
// 输入能量已经逐条作共同 offset 修正；不是 MeV。
// 返回通过容差的候选数。仅返回 1 时，group/single/matchedX 有唯一含义。
inline int Pair23(const int x[2], const int y[3],
                  const double ex[2], const double ey[3], double tolerance,
                  int& groupA, int& groupB, int& single, int& matchedX) {
    if (std::abs(x[0]-x[1])<=1) return 0;
    int count=0;
    for (int a=0; a<3; ++a) {
        for (int b=a+1; b<3; ++b) {
            int c=3-a-b; // 剩下的 Y hit，下标为 0+1+2-a-b
            if (std::abs(y[a]-y[b])!=1) continue;
            if (std::abs(y[c]-y[a])<=1 || std::abs(y[c]-y[b])<=1) continue;
            for (int i=0; i<2; ++i) { // 合并的 Y 组分别尝试对应 X[0]、X[1]
                double rGroup=ex[i]-(ey[a]+ey[b]);
                double rSingle=ex[1-i]-ey[c];
                if (std::abs(rGroup)>tolerance || std::abs(rSingle)>tolerance) continue;
                ++count;
                groupA=a; groupB=b; single=c; matchedX=i;
            }
        }
    }
    return count;
}

// 相邻两层各有两个粒子：0=直接配对，1=交换，-1=无解，-2=多解。
inline int PairLayers(const int x2[2], const int y2[2],
                      const int x3[2], const int y3[2], int maxDelta=2) {
    bool direct=true, swapped=true;
    for (int i=0; i<2; ++i) {
        direct &= std::abs(x2[i]-x3[i])<=maxDelta && std::abs(y2[i]-y3[i])<=maxDelta;
        swapped &= std::abs(x2[i]-x3[1-i])<=maxDelta && std::abs(y2[i]-y3[1-i])<=maxDelta;
    }
    if (direct && swapped) return -2;
    if (direct) return 0;
    if (swapped) return 1;
    return -1;
}
#endif
