"""Diag6: bisect DFT-flux death. Vary monitor distance, x-width. Scratch."""

import os
import sys

pkg_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, pkg_dir)
sys.path.insert(0, os.path.join(pkg_dir, "..", "common"))
import numpy as np

import meep as mp


def empty_flux(xw, mon_y, fcen=1.0, fw=0.3, res=30):
    sim = mp.Simulation(
        cell_size=mp.Vector3(xw, 6, 0),
        boundary_layers=[mp.PML(1.0, direction=mp.Y)],
        sources=[
            mp.Source(
                mp.GaussianSource(fcen, fwidth=fw),
                component=mp.Ez,
                center=mp.Vector3(0, 1.5, 0),
                size=mp.Vector3(xw, 0, 0),
            )
        ],
        resolution=res,
    )
    mon = sim.add_flux(
        fcen,
        fw,
        5,
        mp.FluxRegion(center=mp.Vector3(0, mon_y, 0), size=mp.Vector3(xw, 0, 0)),
    )
    sim.run(until_after_sources=60)
    return np.array(mp.get_fluxes(mon))


for name, xw, my in [
    ("A:x0.4-far", 0.4, -1.5),
    ("B:x0.4-near", 0.4, 1.0),
    ("C:x0.8-near", 0.8, 1.0),
    ("D:x0.8-far", 0.8, -1.5),
]:
    fl = empty_flux(xw, my)
    print(f"{name}: max|flux|={np.max(np.abs(fl)):.4e}")
