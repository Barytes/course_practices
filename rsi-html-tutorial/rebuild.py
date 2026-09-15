# -*- coding: utf-8 -*-
"""Rebuild all generated fifth-part HTML pages."""
from pathlib import Path
import runpy
import os

ROOT = Path(__file__).resolve().parent
os.chdir(ROOT)

scripts = [
    "gen_b0.py",
    "gen_l1.py",
    "gen_l2.py",
    "gen_l3.py",
    "gen_l4.py",
    "gen_l5.py",
    "gen_apps.py",
    "gen_surveys.py",
    "gen_industry.py",
    "gen_bib.py",
]
for s in scripts:
    print("==>", s)
    runpy.run_path(str(ROOT / s), run_name="__main__")
print("done")
