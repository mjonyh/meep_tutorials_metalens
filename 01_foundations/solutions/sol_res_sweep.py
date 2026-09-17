"""Module 1 Stretch Solution | Resolution convergence sweep (20 -> 60 px/um)
Run: module load <chain> && srun --mpi=pmix -n 4 python3 sol_res_sweep.py
Verifies: max|R+T-1| <= 0.02 across resolutions 20, 30, 40, 60
"""

import os
import sys
import numpy as np

# Add parent directory to access sim_02_fabry
pkg_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.join(pkg_dir, "..")
sys.path.insert(0, parent_dir)

from sim_02_fabry import run_slab


def main():
    resolutions = [20, 30, 40, 60]
    results = []

    print("Running Module 1 Stretch Resolution Sweep...")
    print("---------------------------------------------")
    print(f"{'Res (px/um)':<12} {'max|R+T-1|':<15} {'Fringe peak R':<15} {'Gate':<10}")

    for r in resolutions:
        f, R, T = run_slab(resolution=r)
        err = float(np.max(np.abs(R + T - 1)))
        peak_r = float(np.max(R))
        verdict = "PASS" if err <= 0.02 else "FAIL"
        results.append((r, err, peak_r, verdict))
        print(f"{r:<12} {err:<15.4f} {peak_r:<15.4f} {verdict:<10}")

    outdir = os.path.join(pkg_dir, "outputs")
    os.makedirs(outdir, exist_ok=True)
    out_csv = os.path.join(outdir, "res_sweep.csv")
    np.savetxt(
        out_csv,
        np.array([(r, e, p) for r, e, p, _ in results]),
        header="resolution,max_energy_err,peak_R",
        delimiter=",",
        fmt=["%d", "%.6e", "%.6e"],
    )
    print(f"\nSaved sweep summary to {out_csv}")


if __name__ == "__main__":
    main()
