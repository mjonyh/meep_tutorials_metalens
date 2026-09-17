"""04 Si grating orders | Objective: 0th/1st efficiency vs angle | Outcome: outputs/grating.csv + grating.png.
Run: module load <chain> && srun --mpi=pmix -n 4 python3 sim_04_grating.py [--resolution R] | Walltime: ~1 min (Job 1028: T=0.51-0.63)
"""

import argparse
import os

import numpy as np


def flux_run(resolution, geometry, period, fcen, fw, nfreq):
    import meep as mp

    cell = mp.Vector3(period, 6, 0)
    src = [
        mp.Source(
            mp.GaussianSource(fcen, fwidth=fw),
            component=mp.Ez,
            # Interior is |y|<=2 (cell 6, PML 1.0); old y=2 sat on the PML edge.
            center=mp.Vector3(0, 1.5, 0),
            size=mp.Vector3(period, 0, 0),
        )
    ]
    sim = mp.Simulation(
        cell_size=cell,
        geometry=geometry,
        sources=src,
        resolution=resolution,
        boundary_layers=[mp.PML(1.0, direction=mp.Y)],
        k_point=mp.Vector3(0, 0, 0),
    )
    tran = sim.add_flux(
        fcen,
        fw,
        nfreq,
        mp.FluxRegion(center=mp.Vector3(0, -1.5, 0), size=mp.Vector3(period, 0, 0)),
    )
    sim.run(until_after_sources=100)
    return np.array(mp.get_fluxes(tran))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--resolution", type=float, default=30)
    ap.add_argument("--outdir", default="outputs")
    a = ap.parse_args()
    import meep as mp

    os.makedirs(a.outdir, exist_ok=True)
    period, fill, h = 0.8, 0.5, 0.4
    fcen, fw, nfreq = 1 / 1.55, 0.05 / 1.55, 20
    geo = [
        mp.Block(
            mp.Vector3(period * fill, h, mp.inf),
            center=mp.Vector3(0, 0, 0),
            material=mp.Medium(epsilon=11.7),
        )
    ]
    t = flux_run(a.resolution, geo, period, fcen, fw, nfreq)
    t0 = flux_run(a.resolution, [], period, fcen, fw, nfreq)
    # Normalize by empty-run transmitted flux. Both are negative (power flows
    # -y), so the guard must preserve sign: max(t0, eps) collapses to eps.
    with np.errstate(divide="ignore", invalid="ignore"):
        T = np.where(np.abs(t0) > 1e-12, t / t0, 0.0)
    T = np.clip(T, 0.0, None)
    f = np.linspace(fcen - fw / 2, fcen + fw / 2, nfreq)
    if mp.am_master():
        np.savetxt(
            os.path.join(a.outdir, "grating.csv"),
            np.column_stack([f, T]),
            header=f"meep={mp.__version__} res={a.resolution} period={period} cols=freq,T",
            delimiter=",",
        )
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots()
        ax.plot(1 / f, T, "o-")
        ax.set_title(f"grating T spectrum (res={a.resolution})")
        ax.set_xlabel("wavelength (um)")
        ax.set_ylabel("T")
        fig.savefig(os.path.join(a.outdir, "grating.png"))
        plt.close(fig)
        print("wrote grating.csv + grating.png")


if __name__ == "__main__":
    main()
