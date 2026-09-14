"""Keep the chapter 4 macros in sync with the executed notebook examples.

Run each macro from chapt7, as with the corresponding notebook. Declaration
cells stay at file scope; executable cells run in the notebook's order.
"""
from pathlib import Path
import re
import nbformat

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = {
    "Relativistic_Kinematics": "kinematics_examples",
    "phasespace": "phase_space_examples",
    "invariant_mass": "mass_examples",
    "7.4 14C_reaction_sim": "c14_simulation",
    "7.5 Reaction Q-Reconstruction": "q_reconstruction",
    "7.6 Invariant mass reconstruction": "invariant_reconstruction",
}
HEADERS = """#include <iostream>
#include <fstream>
#include <vector>
#include <cmath>
#include <algorithm>
#include <stdexcept>
#include <TROOT.h>
#include <TFile.h>
#include <TTree.h>
#include <TParameter.h>
#include <TGenPhaseSpace.h>
#include <TLorentzVector.h>
#include <TVector3.h>
#include <TMath.h>
#include <TRandom3.h>
#include <TCanvas.h>
#include <TH1D.h>
#include <TH2D.h>
#include <TH1F.h>
#include <TH2F.h>
#include <TLegend.h>
#include <TLine.h>
#include <TStyle.h>
"""

for notebook, macro in EXAMPLES.items():
    nb = nbformat.read(ROOT / "chapt7" / (notebook + ".ipynb"), as_version=4)
    definitions, steps = [], []
    for cell in nb.cells:
        if cell.cell_type != "code":
            continue
        source = cell.source.strip()
        if not source or source == "%jsroot on":
            continue
        declaration = source.startswith("%%cpp -d\n")
        source = source.removeprefix("%%cpp -d\n")
        source = re.sub(r"^#include[^\n]*\n?", "", source, flags=re.M).strip()
        (definitions if declaration else steps).append(source)
    body = "\n\n".join(steps)
    text = "// Generated from " + notebook + ".ipynb by tools/export_kinematics_macros.py.\n"
    text += "// Run from chapt7; figures are drawn by ROOT, not replaced with image files.\n"
    text += HEADERS + "\n" + "\n\n".join(definitions)
    text += "\n\nvoid " + macro + "()\n{\n"
    text += "\n".join("    " + line if line else "" for line in body.splitlines())
    text += "\n}\n"
    path = ROOT / "chapt7" / (macro + ".C")
    path.write_text(text)
    print(path.relative_to(ROOT))
