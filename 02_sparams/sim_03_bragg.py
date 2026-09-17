"""03 Bragg mirror 8-bilayer Si/SiO2 | Objective: DBR stopband vs TMM | Outcome: outputs/bragg.csv + bragg.png, R>95% in stopband.
Run: module load <chain> && srun --mpi=pmix -n 4 python3 sim_03_bragg.py [--resolution R] | Walltime: ~1 min (Job 1024: peak R=1.003)
"""

import argparse
import os

import numpy as np


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--resolution", type=float, default=30)
    ap.add_argument("--outdir", default="outputs")
    a = ap.parse_args()
    import meep as mp

    os.makedirs(a.outdir, exist_ok=True)
    d1, d2 = 0.11, 0.27  # quarter-wave-ish at 1.55um for eps 11.7/2.1
    geo, x = [], -4 * (d1 + d2) / 2
    for _ in range(8):
        geo.append(
            mp.Block(
                mp.Vector3(d1, mp.inf, mp.inf),
                center=mp.Vector3(x + d1 / 2),
                material=mp.Medium(epsilon=11.7),
            )
        )
        x += d1
        geo.append(
            mp.Block(
                mp.Vector3(d2, mp.inf, mp.inf),
                center=mp.Vector3(x + d2 / 2),
                material=mp.Medium(epsilon=2.1025),
            )
        )
        x += d2
    cell = mp.Vector3(10, 0, 0)
    fcen, df, nfreq = 0.65, 0.7, 80
    src = [
        mp.Source(
            mp.GaussianSource(fcen, fwidth=df),
            component=mp.Ez,
            center=mp.Vector3(-4, 0, 0),
        )
    ]
    sim = mp.Simulation(
        cell_size=cell,
        boundary_layers=[mp.PML(1.0)],
        geometry=geo,
        sources=src,
        resolution=a.resolution,
    )
    refl = sim.add_flux(fcen, df, nfreq, mp.FluxRegion(center=mp.Vector3(-3, 0, 0)))
    tran = sim.add_flux(fcen, df, nfreq, mp.FluxRegion(center=mp.Vector3(3.5, 0, 0)))
    sim.run(until_after_sources=150)
    r, t = np.array(mp.get_fluxes(refl)), np.array(mp.get_fluxes(tran))
    sim.reset_meep()
    sim2 = mp.Simulation(
        cell_size=cell,
        boundary_layers=[mp.PML(1.0)],
        sources=src,
        resolution=a.resolution,
    )
    r0 = sim2.add_flux(fcen, df, nfreq, mp.FluxRegion(center=mp.Vector3(-3, 0, 0)))
    t0 = sim2.add_flux(fcen, df, nfreq, mp.FluxRegion(center=mp.Vector3(3.5, 0, 0)))
    sim2.run(until_after_sources=150)
    r0, t0 = np.array(mp.get_fluxes(r0)), np.array(mp.get_fluxes(t0))
    f = np.linspace(fcen - df / 2, fcen + df / 2, nfreq)
    # Refl monitor sees incident + reflected: R = -(r - r0)/r0.
    # (Old form -r/r0 gives R-1, i.e. unphysical negative R.)
    R = -(r - r0) / np.maximum(r0, 1e-12)
    T = t / np.maximum(t0, 1e-12)
    R = np.clip(R, 0.0, None)
    T = np.clip(T, 0.0, None)
    if mp.am_master():
        import sys

        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "common"))
        np.savetxt(
            os.path.join(a.outdir, "bragg.csv"),
            np.column_stack([1 / f, R, T]),
            header=f"meep={mp.__version__} res={a.resolution} cols=wavelength_um,R,T",
            delimiter=",",
        )
        from plot_utils import spectrum

        spectrum(
            1 / f,
            R,
            T,
            f"Bragg 8-bilayer (res={a.resolution})",
            os.path.join(a.outdir, "bragg.png"),
        )
        print(f"peak R={R.max():.3f} (gate >0.95)")


if __name__ == "__main__":
    main()
