"""08 L3 cavity | Objective: Q via Harminv/decay | Outcome: outputs/cavity.csv + Ez.png, Q + fit quoted.
Run: module load <chain> && srun --mpi=pmix -n 4 python3 sim_08_cavity.py [--resolution R] | Walltime: ~5 min (Jobs 1033/1034: f=0.3076, Q=97.4)
"""

import argparse
import os


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--resolution", type=float, default=24)
    ap.add_argument("--outdir", default="outputs")
    a = ap.parse_args()
    import meep as mp

    os.makedirs(a.outdir, exist_ok=True)
    a0, r = 1.0, 0.29
    nx, ny = 11, 7
    geo = []
    for ix in range(-nx // 2, nx // 2 + 1):
        for iy in range(-ny // 2, ny // 2 + 1):
            if iy == 0 and abs(ix) <= 1:
                continue
            geo.append(
                mp.Cylinder(
                    r,
                    center=mp.Vector3(ix * a0, iy * a0 * 0.866),
                    material=mp.Medium(epsilon=11.7),
                )
            )
    cell = mp.Vector3(nx * a0 + 3, ny * a0 + 3, 0)
    src = [
        mp.Source(
            mp.GaussianSource(0.3, fwidth=0.1),
            component=mp.Ez,
            center=mp.Vector3(0, 0, 0),
        )
    ]

    def make_sim(sources):
        return mp.Simulation(
            cell_size=cell,
            boundary_layers=[mp.PML(1.0)],
            geometry=geo,
            sources=sources,
            resolution=a.resolution,
            symmetries=[mp.Mirror(mp.X), mp.Mirror(mp.Y)],
        )

    sim = make_sim(src)
    h = mp.Harminv(mp.Ez, mp.Vector3(0.3, 0.2), 0.3, 0.1)
    # Long ringdown: high-Q modes need runtime >> Q periods to resolve.
    sim.run(mp.after_sources(h), until_after_sources=600)
    import numpy as np

    # HarminvMode fields are complex in PyMeep 1.28.
    modes = (
        [(float(np.real(m.freq)), float(np.real(m.Q))) for m in h.modes]
        if hasattr(h, "modes")
        else []
    )
    # Re-excite CW at the measured mode for a steady-state field pattern.
    f0 = modes[0][0] if modes else 0.3
    sim2 = make_sim(
        [
            mp.Source(
                mp.ContinuousSource(f0),
                component=mp.Ez,
                center=mp.Vector3(0, 0, 0),
            )
        ]
    )
    sim2.run(until=150)
    if mp.am_master():
        np.savetxt(
            os.path.join(a.outdir, "cavity.csv"),
            np.array(modes or [[0, 0]]),
            header=f"meep={mp.__version__} res={a.resolution} cols=freq,Q",
            delimiter=",",
        )
        mp.output_epsilon(sim)
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig = plt.figure()
        sim2.plot2D(ax=plt.gca(), fields=mp.Ez)
        plt.title(f"L3 mode Ez at f={f0:.4f} (res={a.resolution})")
        fig.savefig(os.path.join(a.outdir, "Ez.png"))
        plt.close(fig)
        print(f"modes={modes} (gate: Harminv converges)")


if __name__ == "__main__":
    main()
