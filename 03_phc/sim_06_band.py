"""06 PhC band square lattice Si rods | Objective: TM gap + gap-midgap % | Outcome: outputs/bands.csv + bands.png, gap ±5% lit.
Run: module load <chain> && srun --mpi=pmix -n 4 python3 sim_06_band.py [--resolution R] | Walltime: ~1 min (Job 1030: bands 3-4 mini-gap 0.5698-0.5785)
"""

import argparse
import os

import numpy as np


def bands_at_k(resolution, k, fcen=0.35, df=0.6, runtime=150, nbands=6):
    """Run one Bloch k-point, return sorted Harminv mode freqs (TM/Ez)."""
    import meep as mp

    r, eps = 0.2, 11.7
    geometry = [mp.Cylinder(r, material=mp.Medium(epsilon=eps))]
    src = [
        mp.Source(
            mp.GaussianSource(fcen, fwidth=df),
            component=mp.Ez,
            center=mp.Vector3(0.1, 0.13),  # low-symmetry point excites all modes
        )
    ]
    sim = mp.Simulation(
        cell_size=mp.Vector3(1, 1, 0),
        geometry=geometry,
        sources=src,
        resolution=resolution,
        k_point=k,
        default_material=mp.Medium(epsilon=1.0),
    )
    h = mp.Harminv(mp.Ez, mp.Vector3(-0.11, 0.07), fcen, df, nbands * 4)
    sim.run(mp.after_sources(h), until_after_sources=runtime)
    # HarminvMode fields are complex in PyMeep 1.28: compare real/abs parts.
    modes = sorted(
        float(np.real(m.freq))
        for m in h.modes
        if abs(m.freq - fcen) < df / 2 and abs(m.err) < 0.05
    )
    return modes[:nbands]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--resolution", type=float, default=24)
    ap.add_argument("--outdir", default="outputs")
    a = ap.parse_args()
    import meep as mp

    os.makedirs(a.outdir, exist_ok=True)
    # G-X-M-G path, 8 segments per leg.
    corners = [
        mp.Vector3(0, 0),
        mp.Vector3(0.5, 0),
        mp.Vector3(0.5, 0.5),
        mp.Vector3(0, 0),
    ]
    labels = ["G", "X", "M", "G"]
    kpts, xticks, xpos = [], [], []
    x = 0
    for leg in range(3):
        seg = np.linspace(0, 1, 9)[:-1]  # 8 pts per leg, no duplicate corners
        for s in seg:
            kpts.append(corners[leg] * (1 - s) + corners[leg + 1] * s)
            x += 1
        xticks.append(labels[leg])
        xpos.append(x - 8)
    xticks.append("G")
    xpos.append(x)
    nbands = 6
    bandmat = np.full((len(kpts), nbands), np.nan)
    for i, k in enumerate(kpts):
        modes = bands_at_k(a.resolution, k, nbands=nbands)
        bandmat[i, : len(modes)] = modes
        if mp.am_master():
            print(
                f"k {i + 1}/{len(kpts)} ({k.x:.3f},{k.y:.3f}): {np.round(modes, 4)}",
                flush=True,
            )
    # Largest gap between adjacent bands across the whole path.
    gap_info = "none found in window"
    for b in range(nbands - 1):
        lo = np.nanmax(bandmat[:, b])
        hi = np.nanmin(bandmat[:, b + 1])
        if hi > lo:
            mid = (hi + lo) / 2
            pct = 100 * (hi - lo) / mid
            cand = f"bands {b + 1}-{b + 2}: {lo:.4f}-{hi:.4f} ({pct:.1f}%)"
            if "none" in gap_info or pct > float(gap_info.split("(")[1].rstrip("%)")):
                gap_info = cand
    if mp.am_master():
        np.savetxt(
            os.path.join(a.outdir, "bands.csv"),
            bandmat,
            header=f"meep={mp.__version__} res={a.resolution} TM r=0.2a eps=11.7 "
            f"gap: {gap_info}",
            delimiter=",",
        )
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots()
        for b in range(nbands):
            ax.plot(range(len(kpts)), bandmat[:, b], "o-", ms=3)
        ax.set_xticks(xpos, xticks)
        for xp in xpos:
            ax.axvline(xp, color="k", lw=0.5)
        ax.set_title(f"square-lattice rods TM bands (res={a.resolution}, UNTESTED)")
        ax.set_xlabel("k-path G-X-M-G")
        ax.set_ylabel("freq (c/a)")
        fig.savefig(os.path.join(a.outdir, "bands.png"))
        plt.close(fig)
        print(f"gap: {gap_info} (gate: within 5% of literature)")


if __name__ == "__main__":
    main()
