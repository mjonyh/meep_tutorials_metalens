"""Module 3 Stretch Solution | W1 fine frequency probe & gap edge mapping
Run: module load <chain> && srun --mpi=pmix -n 4 python3 sol_w1_freq_probe.py
Evaluates: W1 defect waveguide transmission across the gap boundary (0.28 to 0.36 c/a).
"""

import os
import sys
import numpy as np

pkg_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.join(pkg_dir, "..")
sys.path.insert(0, parent_dir)

from sim_08_w1 import T_at


def main():
    res = 20
    # Probe frequencies across passband, in-gap notch, and band-edge (0.33)
    freqs = [0.25, 0.28, 0.30, 0.33, 0.36]
    Ts = []

    print("Running Module 3 W1 Frequency Probe...")
    print("---------------------------------------")
    print(f"{'Freq (c/a)':<12} {'T (norm)':<14} {'T (dB)':<12} {'Regime':<15}")

    for f in freqs:
        t = T_at(res, f)
        Ts.append(t)
        db = 10 * np.log10(max(t, 1e-6))
        regime = "In-Gap Notch" if t < 0.05 else ("Passband" if t > 0.3 else "Band Edge")
        print(f"{f:<12.2f} {t:<14.4e} {db:<12.1f} {regime:<15}")

    outdir = os.path.join(pkg_dir, "outputs")
    os.makedirs(outdir, exist_ok=True)
    np.savetxt(
        os.path.join(outdir, "w1_fine_sweep.csv"),
        np.column_stack([freqs, Ts]),
        header="freq,T",
        delimiter=",",
        fmt=["%.3f", "%.6e"],
    )
    print(f"\nSaved fine sweep to {os.path.join(outdir, 'w1_fine_sweep.csv')}")


if __name__ == "__main__":
    main()
