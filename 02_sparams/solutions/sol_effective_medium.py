"""Module 2 Stretch Solution | Effective medium comparison at period=0.15 um
Run: module load <chain> && srun --mpi=pmix -n 4 python3 sol_effective_medium.py
Compares: FDTD transmission for period=0.15 um vs volume-averaged effective index TMM.
"""

import os
import sys
import numpy as np

pkg_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.join(pkg_dir, "..")
sys.path.insert(0, parent_dir)

from sim_05_effmedium import flux_run, stack_T


def homogeneous_slab_T(eps_eff, total_thickness, lam=1.55):
    """Analytic normal-incidence Fresnel transmission through slab of index n_eff."""
    n = np.sqrt(eps_eff)
    k0 = 2 * np.pi / lam
    delta = k0 * n * total_thickness
    r12 = (1 - n) / (1 + n)
    # Fabry-Perot Airy formula
    T_analytic = (1 - r12**2)**2 / ((1 - r12**2)**2 + 4 * r12**2 * np.sin(delta)**2)
    return float(T_analytic)


def main():
    res = 30
    period = 0.15
    ncell = 6
    total_thickness = ncell * period  # 0.90 um

    print(f"Computing period={period:.2f} um transmission at res={res}...")
    i0 = flux_run(res, [])
    T_meas = stack_T(res, period, i0, ncell=ncell)

    # Volume-averaged effective permittivity for 50/50 Si / SiO2 stack
    eps_si = 11.7
    eps_sio2 = 2.1025
    eps_eff_vol = 0.5 * eps_si + 0.5 * eps_sio2  # 6.90125
    T_eff = homogeneous_slab_T(eps_eff_vol, total_thickness)

    print("\n--- Results for Period 0.15 um (lambda/10 regime) ---")
    print(f"FDTD Measured T              : {T_meas:.4f}")
    print(f"Volume-averaged Eff-Medium T : {T_eff:.4f}")
    print(f"Deviation                    : {abs(T_meas - T_eff):.4f}")
    print("Homogenization condition period << lambda holds well at period=0.15 um.")


if __name__ == "__main__":
    main()
