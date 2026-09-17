"""07 W1 waveguide | Objective: in-gap vs out-gap T | Outcome: outputs/w1.csv + w1.png, suppression >10dB.
Run: module load <chain> && srun --mpi=pmix -n 4 python3 sim_08_w1.py [--resolution R] | Walltime: ~1 min (Job 1031: ~40 dB suppression; scaling Jobs 1171-1173)
"""

import argparse
import os

import numpy as np


def flux_run(res, fcen, geometry):
    import meep as mp

    a0 = 1.0
    nx, ny = 9, 7
    cell = mp.Vector3(nx * a0 + 2, ny * a0 + 2, 0)
    src = [
        mp.Source(
            mp.GaussianSource(fcen, fwidth=0.05),
            component=mp.Ez,
            center=mp.Vector3(-3.5, 0, 0),
            size=mp.Vector3(0, 1, 0),
        )
    ]
    sim = mp.Simulation(
        cell_size=cell,
        boundary_layers=[mp.PML(1.0)],
        geometry=geometry,
        sources=src,
        resolution=res,
    )
    tr = sim.add_flux(
        fcen,
        0.05,
        10,
        mp.FluxRegion(center=mp.Vector3(3.5, 0, 0), size=mp.Vector3(0, 1, 0)),
    )
    sim.run(until_after_sources=150)
    return float(np.mean(mp.get_fluxes(tr)))


def w1_geometry():
    import meep as mp

    a0, r = 1.0, 0.2
    nx, ny = 9, 7
    geo = []
    for ix in range(-nx // 2, nx // 2 + 1):
        for iy in range(-ny // 2, ny // 2 + 1):
            if iy == 0 and abs(ix) <= 4:
                continue
            geo.append(
                mp.Cylinder(
                    r,
                    center=mp.Vector3(ix * a0, iy * a0 * 0.866),
                    material=mp.Medium(epsilon=11.7),
                )
            )
    return geo


def T_at(res, fcen):
    # Normalize by empty-cell flux; old code returned raw flux ("dB arb").
    t = flux_run(res, fcen, w1_geometry())
    t0 = flux_run(res, fcen, [])
    return t / max(t0, 1e-12)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--resolution", type=float, default=20)
    ap.add_argument("--outdir", default="outputs")
    a = ap.parse_args()
    import meep as mp

    os.makedirs(a.outdir, exist_ok=True)
    freqs = [0.25, 0.30, 0.36]
    Ts = [T_at(a.resolution, f) for f in freqs]
    Ts = [min(max(v, 0.0), 1.0) for v in Ts]
    if mp.am_master():
        np.savetxt(
            os.path.join(a.outdir, "w1.csv"),
            np.column_stack([freqs, Ts]),
            header=f"meep={mp.__version__} res={a.resolution}",
            delimiter=",",
        )
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots()
        ax.plot(freqs, 10 * np.log10(np.maximum(Ts, 1e-6)), "o-")
        ax.set_title(f"W1 T (res={a.resolution}, UNTESTED)")
        ax.set_xlabel("freq (c/a)")
        ax.set_ylabel("T (dB, normalized)")
        fig.savefig(os.path.join(a.outdir, "w1.png"))
        plt.close(fig)
        print("wrote w1.csv + w1.png")


if __name__ == "__main__":
    main()
