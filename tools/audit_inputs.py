"""Read-only inventory of the inputs used by chapters 1--3."""
from pathlib import Path
import ROOT
ROOT.gROOT.SetBatch(True)
base = Path(__file__).resolve().parents[1]
files = [
 'materials/chapt1/root-tree/tree_hw.root',
 'materials/chapt1/makeclass/run0005.root',
 'materials/chapt2/ppac/f8ppac001.root',
 'materials/chapt3/dssd1/s4.root',
 'materials/chapt3/dssd1/s4hit.root',
 'materials/chapt3/dssd1/gamma.root',
 'materials/chapt3/newDSSD/data/data_16C.root',
 'materials/chapt3/newDSSD/data/d1xy.root',
 'materials/chapt3/newDSSD/data/cal_16C.root',
 'materials/chapt3/newDSSD/data/evt_16C.root',
]
for relative in files:
    path = base / relative
    f = ROOT.TFile.Open(str(path))
    print('\nFILE', relative, path.stat().st_size, flush=True)
    for key in f.GetListOfKeys():
        obj = key.ReadObj()
        if obj.InheritsFrom('TTree'):
            print('TREE', obj.GetName(), obj.GetEntries(), flush=True)
            print('; '.join(f'{leaf.GetName()}: {leaf.GetTypeName()} {leaf.GetTitle()}' for leaf in obj.GetListOfLeaves()), flush=True)
        else:
            print(key.GetName(), key.GetClassName(), flush=True)
    f.Close()
