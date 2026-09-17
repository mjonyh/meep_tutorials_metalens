"""02 Fabry-Perot Si slab | Objective: T fringes vs Fresnel + res sweep | Outcome: outputs/fabry.csv + fabry.png, R+T+A=1±0.02.
Run: module load <chain> && srun --mpi=pmix -n 4 python3 sim_02_fabry.py [--resolution R]
Saves: outputs/fabry.csv, outputs/fabry.png | Walltime: ~1 min on 4 cores (Job 1023: max|R+T-1|=0.0003)
"""

import argparse
import os

import numpy as np


def flux_run(resolution, geometry, fcen=0.5, df=0.4, nfreq=60, run_time=120):
    import meep as mp

    cell = mp.Vector3(8, 0, 0)
    pml = [mp.PML(1.0)]
    src = [
        mp.Source(
            mp.GaussianSource(fcen, fwidth=df),
            component=mp.Ez,
            center=mp.Vector3(-3, 0, 0),
        )
    ]
    sim = mp.Simulation(
        cell_size=cell,
        boundary_layers=pml,
        geometry=geometry,
        sources=src,
        resolution=resolution,
    )
    refl = sim.add_flux(fcen, df, nfreq, mp.FluxRegion(center=mp.Vector3(-2, 0, 0)))
    tran = sim.add_flux(fcen, df, nfreq, mp.FluxRegion(center=mp.Vector3(2, 0, 0)))
    sim.run(until_after_sources=run_time)
    return (
        np.array(mp.get_fluxes(refl)),
        np.array(mp.get_fluxes(tran)),
        np.array([fcen + (i / (nfreq - 1) - 0.5) * df for i in range(nfreq)]),
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--resolution", type=float, default=30)
    ap.add_argument("--outdir", default="outputs")
    a = ap.parse_args()
    import meep as mp

    os.makedirs(a.outdir, exist_ok=True)
    slab = [
        mp.Block(
            mp.Vector3(1.0, mp.inf, mp.inf),
            center=mp.Vector3(),
            material=mp.Medium(epsilon=11.7),
        )
    ]
    r, t, f = flux_run(a.resolution, slab)
    r0, t0, _ = flux_run(a.resolution, [])
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
            os.path.join(a.outdir, "fabry.csv"),
            np.column_stack([f, R, T]),
            header=f"meep={mp.__version__} res={a.resolution} cols=freq,R,T",
            delimiter=",",
        )
        from plot_utils import spectrum

        spectrum(
            1 / f,
            R,
            T,
            f"Si slab R/T (res={a.resolution})",
            os.path.join(a.outdir, "fabry.png"),
        )
        print(f"max|R+T-1| off-res check: {np.max(np.abs(R + T - 1)):.3f} (gate ≤0.02)")


if __name__ == "__main__":
    main()
