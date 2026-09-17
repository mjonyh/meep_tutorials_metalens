"""11 MIM patch absorber | Objective: A>90% + width/spacer sweep | Outcome: outputs/absorber.csv + absorber.png.
Run: module load <chain> && srun --mpi=pmix -n 4 python3 sim_11_absorber.py [--resolution R --run_time T] | Walltime: ~11 min (Job 1102, res 160, 4 tasks, true MPI)
"""

import argparse
import os
import sys

import numpy as np

sys.path.insert(
    0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "common")
)


# Wide band λ 0.9–2.5um to FIND the MIM resonance (narrow 0.87–1.18um band
# showed only bare-Au 3%: resonance sits redder than first estimated).
FCEN, DF, NFREQ, PERIOD = 0.75, 0.7, 40, 0.4
# 30nm spacer (was 50nm): tighter gap mode, less radiation — push the
# broad 0.36 resonance toward critical coupling. Needs res>=80 (2.4 cells).
SPACER_H = 0.03
# Simulate two periods (cell x = 0.8): a flux region spanning exactly one
# 0.4-wide periodic cell returns ~0 DFT flux (fields are healthy O(1);
# single-period source/monitor seam suspected — diag jobs 1048-1055).
# Physics pitch stays PERIOD; patches are duplicated at x=±PERIOD/2.
NCELL = 2


def refl_flux(res, geometry, run_time):
    import meep as mp
    from materials import au_rakic  # noqa: F401 (import keeps sys.path pattern)

    # Tall cell mirrors the proven sim_04 grating geometry.
    # Interior |y|<=2: source/monitor/structure all clear of the PML.
    xw = NCELL * PERIOD
    cell = mp.Vector3(xw, 6, 0)
    src = [
        mp.Source(
            mp.GaussianSource(FCEN, fwidth=DF),
            # Ex (TM): in-plane E drives the patch/backplane magnetic resonance.
            # (Old Ez is uniform along the invariant axis: no restoring force,
            # no resonance — measured A~0.1 broadband.)
            component=mp.Ex,
            center=mp.Vector3(0, 1.5, 0),
            size=mp.Vector3(xw, 0, 0),
        )
    ]
    sim = mp.Simulation(
        cell_size=cell,
        geometry=geometry,
        sources=src,
        resolution=res,
        boundary_layers=[mp.PML(1.0, direction=mp.Y)],
        # Patch array is periodic in x. Default boundaries are PEC metal:
        # without k_point the side walls mirror the cell (effective doubled
        # period). Even-mode normal incidence is nearly unaffected, but
        # periodic is the well-posed statement (cf. sim_04 grating).
        k_point=mp.Vector3(0, 0, 0),
    )
    refl = sim.add_flux(
        FCEN,
        DF,
        NFREQ,
        mp.FluxRegion(center=mp.Vector3(0, 1.0, 0), size=mp.Vector3(xw, 0, 0)),
    )
    sim.run(until_after_sources=run_time)
    return np.array(mp.get_fluxes(refl))


def absorber_geometry(width, spacer_h):
    import meep as mp
    from materials import au_rakic

    au, sio2 = au_rakic(), mp.Medium(epsilon=2.1025)
    # Layers in CONTACT (backplane top y=0): 100nm Au, SPACER_H SiO2,
    # 50nm Au patch on top. Old coordinates left 175nm + 50nm air gaps
    # around the spacer — no gap plasmon, measured bare-Au 3% (Jobs 1056-58).
    geo = [
        mp.Block(
            mp.Vector3(mp.inf, 0.1, mp.inf),
            center=mp.Vector3(0, -0.05, 0),
            material=au,
        ),
        mp.Block(
            mp.Vector3(mp.inf, spacer_h, mp.inf),
            center=mp.Vector3(0, spacer_h / 2, 0),
            material=sio2,
        ),
    ]
    for xc in (-PERIOD / 2, PERIOD / 2):  # one patch per period
        geo.append(
            mp.Block(
                mp.Vector3(width, 0.05, mp.inf),
                center=mp.Vector3(xc, spacer_h + 0.025, 0),
                material=au,
            )
        )
    return geo


def A_at(res, width, spacer_h, r0, run_time):
    # Opaque Au backplane => T=0, A(f) = 1 - R(f).
    # Incident power flows -y, so r0 is negative: guard must preserve sign.
    # Bins where the incident spectrum vanishes (band edges) carry no
    # information: masked to NaN, excluded from the peak (old code returned
    # A=1.0 at the lowest bin for every width — a normalization artifact).
    r = refl_flux(res, absorber_geometry(width, spacer_h), run_time)
    valid = np.abs(r0) >= 0.05 * np.max(np.abs(r0))
    with np.errstate(divide="ignore", invalid="ignore"):
        R = np.where(valid, -(r - r0) / np.where(valid, r0, 1.0), np.nan)
    R = np.clip(R, 0.0, 1.0)
    A = 1.0 - R
    return float(np.nanmax(A)), A


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--resolution", type=float, default=160)
    ap.add_argument("--run_time", type=float, default=120)
    ap.add_argument("--outdir", default="outputs")
    a = ap.parse_args()
    import meep as mp

    os.makedirs(a.outdir, exist_ok=True)
    # One empty run serves all spacers (r0 is geometry-independent).
    r0 = refl_flux(a.resolution, [], a.run_time)
    # Spacer sweep: radiative/absorptive coupling ratio sets critical
    # coupling. 30nm was never above A=0.75 (Jobs 1092/1096); 50nm was only
    # tested with the old air-gap bug, never with contacting layers.
    spacers = [0.015, 0.02]
    widths = [0.19, 0.20, 0.21]
    f = np.linspace(FCEN - DF / 2, FCEN + DF / 2, NFREQ)
    best = (-1.0, 0.03, 0.20)  # (A, spacer, width); always replaced (A>=0)
    best_row = None
    for s in spacers:
        peak_As, spectra = [], []
        for w in widths:
            peak, spec = A_at(a.resolution, w, s, r0, a.run_time)
            peak_As.append(peak)
            spectra.append(spec)
            if peak > best[0]:
                best = (peak, s, w)
        if mp.am_master():
            tag = f"spacer{int(round(s * 1000)):02d}nm"
            np.savetxt(
                os.path.join(a.outdir, f"absorber_{tag}.csv"),
                np.column_stack([widths, peak_As]),
                header=f"meep={mp.__version__} res={a.resolution} "
                f"spacer={s} cols=width_um,A_peak",
                delimiter=",",
            )
            np.savetxt(
                os.path.join(a.outdir, f"absorber_spectra_{tag}.csv"),
                np.column_stack([1 / f] + spectra),
                header=f"meep={mp.__version__} res={a.resolution} spacer={s} "
                "cols=wavelength_um,A(w=...)" + ",".join(f"{w}" for w in widths),
                delimiter=",",
            )
    if mp.am_master():
        # Canonical absorber.csv/png track the best spacer (lesson gate).
        bA, bS, bW = best
        btag = f"spacer{int(round(bS * 1000)):02d}nm"
        import shutil

        shutil.copy(
            os.path.join(a.outdir, f"absorber_{btag}.csv"),
            os.path.join(a.outdir, "absorber.csv"),
        )
        shutil.copy(
            os.path.join(a.outdir, f"absorber_spectra_{btag}.csv"),
            os.path.join(a.outdir, "absorber_spectra.csv"),
        )
        best_row = np.loadtxt(
            os.path.join(a.outdir, f"absorber_{btag}.csv"),
            delimiter=",",
            comments="#",
        )
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots()
        ax.plot(best_row[:, 0], best_row[:, 1], "o-")
        ax.axhline(0.9, ls="--", label="90%")
        ax.set_title(f"MIM absorber (res={a.resolution}, spacer={bS})")
        ax.set_xlabel("patch width (um)")
        ax.set_ylabel("A_peak")
        ax.legend()
        fig.savefig(os.path.join(a.outdir, "absorber.png"))
        plt.close(fig)
        print(
            f"wrote absorber.csv + absorber_spectra.csv + absorber.png "
            f"(best A={bA:.3f} at spacer={bS} width={bW}, gate >0.90)"
        )


if __name__ == "__main__":
    main()
