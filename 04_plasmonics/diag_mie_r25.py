"""Diag: sim_09 spectrum at r=0.025um (half radius) to discriminate staircase
vs physics for the +20nm FDTD-vs-analytic offset at r=0.05.
If FDTD-25 lands on analytic-25/QS, both methods are sound and the r=50
offset is a meshing systematic. Serial run, ~1 min.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np

import sim_09_mie as m


def main():
    m.RADIUS = 0.025
    f, scat = m.spectrum_at(120, 80)
    lam_nm = 1 / f * 1000
    peak = float(lam_nm[np.nanargmax(scat)])
    print(f"diag r=0.025 res=120: dipolar peak ~{peak:.0f} nm", flush=True)


if __name__ == "__main__":
    main()
