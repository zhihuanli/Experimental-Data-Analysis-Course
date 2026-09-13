"""Copy selected, unchanged teaching inputs; never overwrite an existing file."""
from pathlib import Path
import hashlib
import json
import subprocess

ROOT = Path(__file__).resolve().parents[1]
pairs = {
 'materials/chapt1/makeclass/run0005.root': 'chapt1/run0005.root',
 'materials/chapt1/root-tree/tree_hw.root': 'chapt1/tree_hw.root',
 'materials/chapt1/root-tree/fig/tdiff.png': 'chapt1/fig/tdiff.png',
 'materials/chapt2/ppac/f8ppac001.root': 'chapt2/f8ppac001.root',
 'materials/chapt3/vector/cal_16C.root': 'chapt3/data/strip_arrays_16C.root',
}
for name in ['s4.root','s4hit.root','gamma.root','cut1.C','cut2.C','Pies.cal','Rings.cal']:
    pairs['materials/chapt3/dssd1/'+name] = 'chapt3/'+name
for name in ['data_16C.root','d1xy.root','d2xy.root','d3xy.root','cal_16C.root','evt_16C.root','cut1.C','cut2.C','cut3.C']:
    pairs['materials/chapt3/newDSSD/data/'+name] = 'chapt3/data/'+name
for n in range(1,4):
    name = f'cutd{n}esc.cut'
    pairs['materials/chapt3/newDSSD/'+name] = 'chapt3/'+name

def digest(path):
    with path.open('rb') as f:
        return hashlib.file_digest(f,'sha256').hexdigest()

records = []
for original, destination in pairs.items():
    src, dst = ROOT/original, ROOT/destination
    dst.parent.mkdir(parents=True, exist_ok=True)
    sha = digest(src)
    if not dst.exists():
        subprocess.run(['cp','-cRp',str(src),str(dst)],check=True)
    if digest(dst) != sha:
        raise RuntimeError('Different existing input: '+destination)
    records.append({'source':original,'copy':destination,'bytes':dst.stat().st_size,'sha256':sha})
(ROOT/'data_manifest.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n')
print('Verified',len(records),'input copies')
