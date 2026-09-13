"""Formatting only; synchronize source cells after trimming line endings."""
from lecture_editor import ROOT,PAGES,Page
import subprocess

paths=subprocess.check_output(['git','ls-files','--modified','--others','--exclude-standard'],cwd=ROOT,text=True).splitlines()
for rel in paths:
    path=ROOT/rel
    if not path.is_file() or not rel.startswith(('chapt1/','chapt2/','chapt3/')):continue
    if path.suffix not in ('.html','.C','.cpp','.h','.cc'):continue
    # Keep archived inputs and graphical cuts byte-identical to originals.
    if rel.startswith('chapt3/data/') or path.name in ('cut1.C','cut2.C','cut3.C'):continue
    text=path.read_text()
    cleaned='\n'.join(line.rstrip() for line in text.splitlines())+'\n'
    if text!=cleaned:path.write_text(cleaned)
for rel in PAGES+['chapt1/ROOT_tips.html']:
    Page(rel,current=True).save()
