"""Read-only numerical comparison of the independently compiled examples."""
from pathlib import Path
import ROOT as R
import numpy as np
import math

base=Path(__file__).resolve().parents[1]
columns=['source_entry','tx','ty','theta_x','theta_y','sigma_tx','sigma_ty','sigma_thetax','sigma_thetay','c2nx','c2ny']
values=[]
for name in ['compile1','compile2']:
    values.append(R.RDataFrame('tree',str(base/f'chapt2/code/{name}/out001.root')).AsNumpy(columns))
for col in columns:np.testing.assert_array_equal(values[0][col],values[1][col])
print('PASS PPAC: identical',len(values[0]['source_entry']),'events and',len(columns),'columns')

R.gSystem.Load(str(base/'chapt3/code/code2/libhits.so'))
files=[R.TFile.Open(str(base/x)) for x in ['chapt3/data/strip_arrays_16C.root','chapt3/vec_16C.root','chapt3/sort_16C.root']]
tin,tvec,tout=[f.Get('tree') for f in files]
entries=tin.GetEntries()
assert tvec.GetEntries()==tout.GetEntries()==entries
for filename in ['vec_16C.root','sort_16C.root']:
    df=R.RDataFrame('tree',str(base/'chapt3'/filename))
    assert df.Filter('source_entry != static_cast<Long64_t>(rdfentry_)').Count().GetValue()==0
print('PASS vector: all',entries,'input events retained in original order')
for i in list(range(20))+list(range(20,entries,20000))+[entries-1]:
    tin.GetEntry(i);tvec.GetEntry(i);tout.GetEntry(i)
    for layer in [1,2,3]:
        for side in ['x','y']:
            original=getattr(tin,f'd{layer}{side}')
            expected=[(j,float(original[j])) for j in range(32) if original[j]>=1]
            actual=getattr(tvec,f'{side}{layer}v')
            assert [(h.id,h.e) for h in actual]==expected
            assert all(math.isnan(h.t) for h in actual)
        x=sorted(getattr(tvec,f'x{layer}v'),key=lambda h:-h.e)
        y=sorted(getattr(tvec,f'y{layer}v'),key=lambda h:-h.e)
        expected=[(a.id,b.id,a.e,b.e) for a,b in zip(x,y) if abs(a.e-b.e)<50]
        assert [(h.xid,h.yid,h.xe,h.ye) for h in getattr(tout,f'd{layer}')]==expected
print('PASS vector samples: strip IDs, energies, missing-time NaN, and candidate pairing')
