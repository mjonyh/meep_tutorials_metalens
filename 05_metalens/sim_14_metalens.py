"""14 cylindrical metalens 2D | Objective: focus FWHM vs λ/2NA + efficiency | Outcome: outputs/focus.csv + focal-cut.png.
Run: module load <chain> && srun --mpi=pmix -n 4 python3 sim_14_metalens.py [--resolution R] | Walltime: ~23 min (Job 1071: FWHM=0.625, eff=0.420; fallback_data/ available)
"""

import argparse
import os

import numpy as np

LAM, F_LEN, WIDTH, PERIOD = 1.55, 6.0, 20.0, 0.7
H_PILLAR = 1.4  # same meta-atom as sim_12 library
# Pillars y in [-1.75,-0.35] + f=6 -> focus y≈4.7, inside the cell
# (|y|<=8, PML 1.0); the axial scan locates it exactly.
# (Old f=10 put the focus at y≈8.7, outside the cell.)
# Phase->diameter map: monotonic branch of the sim_12 H=1.4 library
# (res 30, unwrapped phase 0.21..6.18 rad over d=0.12..0.495). Required
# wrapped phase p is scaled onto the available 5.97 rad span (5% gradient
# shortfall, noted in the lesson); beyond-branch values clip to max d.
_LIB_D = [0.120, 0.162, 0.203, 0.245, 0.287, 0.328, 0.370, 0.412, 0.453, 0.495]
_LIB_P = [0.21, 2.09, 3.07, 3.97, 4.68, 5.12, 5.47, 5.77, 6.06, 6.18]
_LIB_SPAN = _LIB_P[-1] - _LIB_P[0]


def phase_to_d(p):
    target = _LIB_P[0] + (p / (2 * np.pi)) * _LIB_SPAN
    return float(np.interp(target, _LIB_P, _LIB_D))


def build_geometry():
    import meep as mp

    xs = np.arange(-WIDTH / 2, WIDTH / 2, PERIOD)
    phi = -2 * np.pi / LAM * (np.sqrt(F_LEN**2 + xs**2) - F_LEN)
    geo = [
        mp.Block(
            mp.Vector3(mp.inf, 0.5, mp.inf),
            center=mp.Vector3(0, -2.0, 0),
            material=mp.Medium(epsilon=2.1025),
        )
    ]
    for x, p in zip(xs, phi):
        d = phase_to_d(p % (2 * np.pi))
        geo.append(
            mp.Cylinder(
                d / 2,
                height=H_PILLAR,
                axis=mp.Vector3(0, 1, 0),
                center=mp.Vector3(float(x), -1.75 + H_PILLAR / 2, 0),
                material=mp.Medium(epsilon=11.7),
            )
        )
    return geo


def run_lens(resolution, geometry, tag):
    import meep as mp

    cell = mp.Vector3(WIDTH + 4, 16, 0)
    src = [
        mp.Source(
            mp.ContinuousSource(1 / LAM),
            component=mp.Ez,
            center=mp.Vector3(0, -4.0, 0),
            size=mp.Vector3(WIDTH, 0, 0),
        )
    ]
    sim = mp.Simulation(
        cell_size=cell,
        geometry=geometry,
        sources=src,
        resolution=resolution,
        boundary_layers=[mp.PML(1.0)],
        force_complex_fields=True,
        filename_prefix=tag,
    )
    sim.run(until=120)
    return sim


def fwhm(xs, intensity):
    peak = float(np.max(intensity))
    above = np.where(intensity >= peak / 2)[0]
    if len(above) < 2:
        return 0.0
    dx = xs[1] - xs[0]
    return float((above[-1] - above[0]) * dx)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--resolution", type=float, default=25)
    ap.add_argument("--outdir", default="outputs")
    a = ap.parse_args()
    import meep as mp

    os.makedirs(a.outdir, exist_ok=True)
    sim = run_lens(a.resolution, build_geometry(), "metalens")
    # Axial scan to locate the focal plane, then transverse cut there.
    ys = np.linspace(0, 7, 141)
    axial = np.array(
        [abs(sim.get_field_point(mp.Ez, mp.Vector3(0, float(y)))) for y in ys]
    )
    y_focus = float(ys[int(np.argmax(axial))])
    xs = np.linspace(-WIDTH / 2, WIDTH / 2, 321)
    trans = np.array(
        [
            abs(sim.get_field_point(mp.Ez, mp.Vector3(float(x), y_focus))) ** 2
            for x in xs
        ]
    )
    fw = fwhm(xs, trans)
    na = float(np.sin(np.arctan((WIDTH / 2) / F_LEN)))
    dl = LAM / (2 * na)
    # Efficiency: power in main lobe (±1.5 FWHM) vs incident power from
    # an empty run cut at the same plane.
    lobe = np.abs(xs) <= 1.5 * fw
    sim0 = run_lens(a.resolution, [], "metalens-empty")
    trans0 = np.array(
        [
            abs(sim0.get_field_point(mp.Ez, mp.Vector3(float(x), y_focus))) ** 2
            for x in xs
        ]
    )
    eff = float(np.sum(trans[lobe]) / max(np.sum(trans0), 1e-12))
    if mp.am_master():
        np.savetxt(
            os.path.join(a.outdir, "focus.csv"),
            np.column_stack([xs, trans]),
            header=f"meep={mp.__version__} res={a.resolution} lam={LAM} f={F_LEN} "
            f"y_focus={y_focus:.2f} fwhm={fw:.3f} dl={dl:.3f} eff={eff:.3f} "
            "cols=x_um,intensity",
            delimiter=",",
        )
        np.savetxt(
            os.path.join(a.outdir, "axial.csv"),
            np.column_stack([ys, axial**2]),
            header="cols=y_um,axial_intensity",
            delimiter=",",
        )
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
        ax1.plot(ys, axial**2)
        ax1.axvline(y_focus, ls="--", label=f"focus y={y_focus:.2f}")
        ax1.set_title("axial intensity")
        ax1.set_xlabel("y (um)")
        ax1.legend()
        ax2.plot(xs, trans)
        ax2.set_title(f"focal cut: FWHM={fw:.2f}um vs λ/2NA={dl:.2f}um (UNTESTED)")
        ax2.set_xlabel("x (um)")
        ax2.set_ylabel("|E|^2")
        fig.savefig(os.path.join(a.outdir, "focal-cut.png"))
        plt.close(fig)
        mp.output_efield_z(sim)
        print(
            f"focus y={y_focus:.2f} (design f={F_LEN}), FWHM={fw:.3f} vs λ/2NA={dl:.3f}, eff={eff:.3f}"
        )


if __name__ == "__main__":
    main()
