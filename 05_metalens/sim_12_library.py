"""12 meta-atom library Si pillar | Objective: 8-level 0-2π T+phase at 1.55um | Outcome: outputs/library.csv + T-phase.png.
Run: module load <chain> && srun --mpi=pmix -n 4 python3 sim_12_library.py [--resolution R] | Walltime: ~1 min (Job 1138, res 30, 4 tasks, true MPI)
"""

import argparse
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "common"))
from materials import si_nir, sio2

# H=1.4 gives 6.38 rad coverage with T>=0.25 (height scan 2026-09-16:
# H=0.9/1.1/1.3 cover 3.88/4.94/5.77 rad -- insufficient; H=1.5 covers 6.67
# but aspect 12.5:1. Diameters span the resonance (steep branch d<0.2) plus
# the gentle tail so np.interp on unwrapped phase picks 8 levels for sim_13).
PERIOD, H_PILLAR, LAM = 0.7, 1.4, 1.55
PROBE = (0.0, -2.0)  # air below substrate (cell half-height 3, PML 0.5)


def substrate():
    import meep as mp

    return [
        mp.Block(
            mp.Vector3(mp.inf, 0.5, mp.inf),
            center=mp.Vector3(0, -1.2, 0),
            material=sio2(),
        )
    ]


def transmitted(resolution, geometry):
    """Steady-state complex Ez at probe (complex fields => true amplitude/phase)."""
    import meep as mp

    fcen = 1 / LAM
    src = [
        mp.Source(
            mp.ContinuousSource(fcen),
            component=mp.Ez,
            center=mp.Vector3(0, 1.0, 0),
            size=mp.Vector3(PERIOD, 0, 0),
        )
    ]
    sim = mp.Simulation(
        cell_size=mp.Vector3(PERIOD, 6, 0),
        geometry=geometry,
        sources=src,
        resolution=resolution,
        boundary_layers=[mp.PML(0.5, direction=mp.Y)],
        # Periodic in x (unit-cell library). Default boundaries are PEC
        # metal: without k_point the walls short the Ez source and the
        # "plane wave" is a waveguide mode, not periodic illumination.
        k_point=mp.Vector3(0, 0, 0),
        force_complex_fields=True,
    )
    sim.run(until=60)
    return sim.get_field_point(mp.Ez, mp.Vector3(*PROBE))


def cell_response(resolution, diameter):
    import meep as mp

    geo = substrate() + [
        mp.Cylinder(
            diameter / 2,
            height=H_PILLAR,
            axis=mp.Vector3(0, 1, 0),
            center=mp.Vector3(0, -0.95 + H_PILLAR / 2, 0),  # sits on substrate top
            material=si_nir(),
        )
    ]
    return transmitted(resolution, geo)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--resolution", type=float, default=30)
    ap.add_argument("--outdir", default="outputs")
    a = ap.parse_args()
    import meep as mp

    os.makedirs(a.outdir, exist_ok=True)
    # Reference: bare substrate. T and phase are quoted relative to it,
    # so the library measures what the pillar adds (old code used |E| raw).
    e0 = transmitted(a.resolution, substrate())
    # Dense sweep incl. the steep resonance branch (d 0.12-0.16 passed
    # 0.40->2.45 rad in ONE 13-pt step, leaving circular phases 0.81-2.45
    # empty: max gap 1.64 rad, circular cover only 4.64 rad — Job 1069).
    # 31 pts over 0.08-0.68 (Job 1132) cut the gap to 0.83 rad but the branch
    # d 0.14-0.16 still jumps 1.59->2.42 rad: add 0.002-step local sampling.
    # Circular coverage (2π - max wrapped gap) is the gate metric, NOT
    # unwrapped ptp (which double-counts resonance winding).
    # Job 1136 leftovers are all unsampled micro-intervals between grids
    # (0.25-0.26, ~0.134, 0.18-0.19): finish with a uniform 0.004 grid.
    coarse = np.linspace(0.08, 0.68, 151)
    fine1 = np.linspace(0.125, 0.175, 26)  # first steep branch (Job 1133: OK)
    # Second steep branch d 0.20-0.24 jumps +3.13 -> -1.96 through ±π
    # (max gap 1.19 rad, Job 1133): sample it at 0.002 like the first.
    fine2 = np.linspace(0.19, 0.25, 31)
    # Job 1135 leftovers (circular 5.92, all in gentle tail, all continuous):
    # edge micro-branch d 0.08-0.10, d 0.26-0.34, and across the T~0.02
    # zero at d~0.52 (phases there may be unusable-low-T: T-gate reported).
    fine3 = np.linspace(0.08, 0.10, 11)
    fine4 = np.linspace(0.26, 0.34, 17)
    fine5 = np.linspace(0.46, 0.58, 25)
    # Job 1137 leftovers (circular 6.18): sub-0.002 micro-branches at
    # d 0.141-0.143, 0.145-0.147, 0.136-0.140 — all good-T, purely sampling.
    fine6 = np.linspace(0.136, 0.148, 25)
    ds = np.unique(np.concatenate([coarse, fine1, fine2, fine3, fine4, fine5, fine6]))
    Ts, phis = [], []
    for d in ds:
        ez = cell_response(a.resolution, float(d))
        ratio = ez / e0
        Ts.append(abs(ratio) ** 2)
        phis.append(float(np.angle(ratio)))
        if mp.am_master():
            print(f"d={d:.3f}: T={Ts[-1]:.3f} phi={phis[-1]:+.3f} rad", flush=True)
    if mp.am_master():
        arr = np.column_stack([ds, Ts, phis])
        wrapped = np.sort(((arr[:, 2] + np.pi) % (2 * np.pi)) - np.pi)
        gaps = np.diff(np.append(wrapped, wrapped[0] + 2 * np.pi))
        circular = float(2 * np.pi - np.max(gaps))
        np.savetxt(
            os.path.join(a.outdir, "library.csv"),
            arr,
            header=f"meep={mp.__version__} res={a.resolution} lam={LAM} "
            f"cols=d_um,T_rel_substrate,phase_rad circular_cover={circular:.2f}rad",
            delimiter=",",
        )
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig, ax1 = plt.subplots()
        ax1.plot(ds, arr[:, 1], "o-", label="T")
        ax1.set_xlabel("diameter (um)")
        ax1.set_ylabel("T (vs substrate)")
        ax2 = ax1.twinx()
        ax2.plot(ds, np.unwrap(arr[:, 2]), "s-", color="C1", label="phase")
        ax2.set_ylabel("phase (rad, unwrapped)")
        ax1.set_title(f"meta-atom library (res={a.resolution})")
        fig.savefig(os.path.join(a.outdir, "T-phase.png"))
        plt.close(fig)
        cover = float(np.ptp(np.unwrap(arr[:, 2])))
        wrapped = np.sort(((arr[:, 2] + np.pi) % (2 * np.pi)) - np.pi)
        gaps = np.diff(np.append(wrapped, wrapped[0] + 2 * np.pi))
        circular = float(2 * np.pi - np.max(gaps))
        print(
            f"phase coverage={cover:.2f} rad unwrapped-ptp, "
            f"{circular:.2f} rad circular (gate: full 0-2π circular)"
        )


if __name__ == "__main__":
    main()
