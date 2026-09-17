"""05 effective medium stack | Objective: homogenization limit at period~λ/5 | Outcome: outputs/effmedium.csv + period_sweep.png.
Run: module load <chain> && srun --mpi=pmix -n 4 python3 sim_05_effmedium.py [--resolution R] | Walltime: ~1 min (Job 1026: T collapse at period~λ/5)
"""

import argparse
import os

import numpy as np


def flux_run(resolution, geometry, fcen=1 / 1.55, df=0.05, nfreq=5):
    import meep as mp

    cell = mp.Vector3(10, 0, 0)
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
        geometry=geometry,
        sources=src,
        resolution=resolution,
    )
    tr = sim.add_flux(fcen, df, nfreq, mp.FluxRegion(center=mp.Vector3(4, 0, 0)))
    sim.run(until_after_sources=120)
    return float(np.mean(mp.get_fluxes(tr)))


def stack_T(resolution, period, empty_flux, ncell=6):
    import meep as mp  # noqa: F401 (kept for symmetry; flux via helper)

    d1 = d2 = period / 2
    geo, x0 = [], -ncell * period / 2
    for i in range(ncell):
        geo.append(
            mp.Block(
                mp.Vector3(d1, mp.inf, mp.inf),
                center=mp.Vector3(x0 + i * period + d1 / 2),
                material=mp.Medium(epsilon=11.7),
            )
        )
        geo.append(
            mp.Block(
                mp.Vector3(d2, mp.inf, mp.inf),
                center=mp.Vector3(x0 + i * period + d1 + d2 / 2),
                material=mp.Medium(epsilon=2.1025),
            )
        )
    # Normalize by empty-run flux; old code returned raw flux (T>1).
    return flux_run(resolution, geo) / max(empty_flux, 1e-12)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--resolution", type=float, default=30)
    ap.add_argument("--outdir", default="outputs")
    a = ap.parse_args()
    import meep as mp

    os.makedirs(a.outdir, exist_ok=True)
    periods = [0.05, 0.1, 0.2, 0.31, 0.5]
    empty_flux = flux_run(a.resolution, [])
    Ts = [stack_T(a.resolution, p, empty_flux) for p in periods]
    Ts = [min(max(v, 0.0), 1.0) for v in Ts]
    if mp.am_master():
        np.savetxt(
            os.path.join(a.outdir, "effmedium.csv"),
            np.column_stack([periods, Ts]),
            header=f"meep={mp.__version__} res={a.resolution} cols=period_um,T",
            delimiter=",",
        )
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots()
        ax.plot(periods, Ts, "o-")
        ax.axvline(1.55 / 5, ls="--", label="λ/5")
        ax.set_title(f"homogenization breakdown (res={a.resolution}, UNTESTED)")
        ax.set_xlabel("period (um)")
        ax.set_ylabel("T")
        ax.legend()
        fig.savefig(os.path.join(a.outdir, "period_sweep.png"))
        plt.close(fig)
        print("wrote effmedium.csv + period_sweep.png")


if __name__ == "__main__":
    main()
