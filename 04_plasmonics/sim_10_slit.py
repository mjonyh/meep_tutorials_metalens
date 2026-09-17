"""10 MIM slit EOT | Objective: field enhancement map | Outcome: outputs/slit.csv + field map, enhancement quoted.
Run: module load <chain> && srun --mpi=pmix -n 4 python3 sim_10_slit.py [--resolution R] | Walltime: ~4 min (Job 1043: enhancement ~1.3x, marginal)
"""

import argparse
import os
import sys

T_METAL, W_SLIT = 0.15, 0.08
# Subwavelength period (P < lambda_min): the film is continuous across the
# x-walls, i.e. a proper slit ARRAY with k_point=0. (Old cell x=1.0 with PEC
# default walls was an accidental super-wavelength 1.0-period grating:
# propagating diffraction orders spoiled EOT, measured <=1.3x.)
PERIOD = 0.4
# Wavelength sweep: the slit Fabry-Perot condition t ≈ λ/2n_eff is hit by
# scanning λ at fixed geometry (single-λ gave 0.9x off-resonance).
LAMBDAS = [0.55, 0.65, 0.80]


def slit_geometry():
    """Ag film x in [-PERIOD/2, PERIOD/2] with a centered slit of W_SLIT.

    The film touches the periodic walls: continuous film across periods.
    (Old code used two width-1.0 blocks whose union covered the slit.)
    """
    import meep as mp
    from materials import ag_rakic

    side_w = PERIOD / 2 - W_SLIT / 2
    xc = W_SLIT / 2 + side_w / 2
    return [
        mp.Block(
            mp.Vector3(side_w, T_METAL, mp.inf),
            center=mp.Vector3(-xc, 0, 0),
            material=ag_rakic(),
        ),
        mp.Block(
            mp.Vector3(side_w, T_METAL, mp.inf),
            center=mp.Vector3(xc, 0, 0),
            material=ag_rakic(),
        ),
    ]


def center_field(resolution, geometry, tag, lam):
    """Steady-state |Ex| across the slit (complex fields => true amplitude)."""
    import meep as mp
    import numpy as np

    cell = mp.Vector3(PERIOD, 1.5, 0)
    src = [
        mp.Source(
            mp.ContinuousSource(1 / lam),
            # Ex (TM): E across the slit couples to the gap mode (no cutoff).
            # (Old Ez/TE is cut off in a subwavelength slit: measured 0.1x.)
            component=mp.Ex,
            center=mp.Vector3(0, 0.4, 0),  # interior: PML starts at |y|=0.55
            size=mp.Vector3(PERIOD, 0, 0),
        )
    ]
    sim = mp.Simulation(
        cell_size=cell,
        boundary_layers=[mp.PML(0.2, direction=mp.Y)],
        geometry=geometry,
        sources=src,
        resolution=resolution,
        k_point=mp.Vector3(0, 0, 0),  # slit array: periodic in x
        force_complex_fields=True,
        filename_prefix=tag,
    )
    sim.run(until=120)
    # Center value (converged) plus max over the slit aperture (edge
    # singularities concentrate the field; resolution-sensitive by nature).
    pts = [mp.Vector3(float(x), 0, 0) for x in np.linspace(-W_SLIT / 2, W_SLIT / 2, 9)]
    vals = [abs(sim.get_field_point(mp.Ex, p)) for p in pts]
    mp.output_efield_x(sim)
    return vals[len(vals) // 2], max(vals), sim


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--resolution", type=float, default=80)
    ap.add_argument("--outdir", default="outputs")
    a = ap.parse_args()
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "common"))
    import meep as mp

    os.makedirs(a.outdir, exist_ok=True)
    rows = []
    for lam in LAMBDAS:
        tag = f"slit-lam{lam}"
        e_slit, e_slit_max, _ = center_field(a.resolution, slit_geometry(), tag, lam)
        e0, e0_max, _ = center_field(a.resolution, [], tag + "-empty", lam)
        rows.append((lam, e_slit / max(e0, 1e-12), e_slit_max / max(e0_max, 1e-12)))
        if mp.am_master():
            print(
                f"lam={lam}: center={rows[-1][1]:.2f}x max={rows[-1][2]:.1f}x",
                flush=True,
            )
    if mp.am_master():
        import numpy as np

        arr = np.array(rows)
        np.savetxt(
            os.path.join(a.outdir, "slit.csv"),
            arr,
            header=f"meep={mp.__version__} res={a.resolution} "
            "cols=lam_um,enh_center,enh_max",
            delimiter=",",
        )
        best = int(np.argmax(arr[:, 2]))
        print(
            f"best lam={arr[best, 0]}: center={arr[best, 1]:.2f}x "
            f"max={arr[best, 2]:.1f}x (gate: quoted on map)"
        )


if __name__ == "__main__":
    main()
