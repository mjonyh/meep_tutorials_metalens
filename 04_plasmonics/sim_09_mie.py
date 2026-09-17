"""09 Au cylinder scattering | Objective: Mie dipolar peak ±10nm vs analytic | Outcome: outputs/mie.csv + mie.png + res sweep.
Run: module load <chain> && srun --mpi=pmix -n 4 python3 sim_09_mie.py [--resolution R --run_time T] | Walltime: ~1 min (Job 1146, res 120, 4 tasks, true MPI)
"""

import argparse
import os
import sys

import numpy as np

RADIUS = 0.05  # 50 nm in um units
# Closed-box half side 0.15: top/bottom faces sit inside the cell (|y|<=0.2),
# clear of the periodic edge; source and PML stay outside it.
BOX = 0.15


def box_flux(resolution, geometry, fcen, df, nfreq, run_time):
    """Net outward flux through a closed box (scattered + incident) plus the
    incident intensity probe (forward flux through a transverse line in
    front of the box, per unit length). Caller normalizes by the EMPTY-run
    probe: without this the spectrum is weighted by |source(f)|^2 and the
    apparent peak sits at fcen (found 2026-09-16: raw peak 540nm =
    source center; true absorption peak 470nm)."""
    import meep as mp

    # Periodic-y cell (Ly=0.4 < lambda: all grating orders evanescent) with a
    # FULL-WIDTH uniform line source => rigorously normal plane wave (the
    # sim_04 pattern). The old finite-cell/line-source drove the wire with a
    # near-field cylindrical wave (Fresnel number ~1.6 even after the 2.0-cell
    # widening), redshifting the peak +20nm vs analytic robustly across
    # res/probe/cell (Jobs 1139-1143 + r25 diag). PML only in X; y periodic.
    cell = mp.Vector3(3.0, 0.4, 0)
    src = [
        mp.Source(
            mp.GaussianSource(fcen, fwidth=df),
            # Ey: E transverse to the wire axis (z) => excites the dipolar LSP.
            # (Old Ez drove the axial mode: no visible LSP, unconverged peak.)
            component=mp.Ey,
            center=mp.Vector3(-0.8, 0, 0),
            size=mp.Vector3(0, 0.4, 0),
        )
    ]
    sim = mp.Simulation(
        cell_size=cell,
        boundary_layers=[mp.PML(0.5, direction=mp.X)],
        geometry=geometry,
        sources=src,
        resolution=resolution,
        k_point=mp.Vector3(0, 0, 0),
    )
    # MEEP orients every flux region along the FIXED +axis, not outward:
    # verified on login-node micro-run (empty box: left+right both >0,
    # top+bot cancel). Outward-oriented sum = -left + right + top - bot;
    # the naive all-plus sum measures O_L - O_R - O_T + O_B (a
    # forward-scattering asymmetry peaking ~490nm) instead of P_abs.
    monitors = [
        (
            +1.0,
            sim.add_flux(
                fcen,
                df,
                nfreq,
                mp.FluxRegion(
                    center=mp.Vector3(0, BOX, 0), size=mp.Vector3(2 * BOX, 0, 0)
                ),
            ),
        ),
        (
            -1.0,
            sim.add_flux(
                fcen,
                df,
                nfreq,
                mp.FluxRegion(
                    center=mp.Vector3(0, -BOX, 0), size=mp.Vector3(2 * BOX, 0, 0)
                ),
            ),
        ),
        (
            +1.0,
            sim.add_flux(
                fcen,
                df,
                nfreq,
                mp.FluxRegion(
                    center=mp.Vector3(BOX, 0, 0), size=mp.Vector3(0, 2 * BOX, 0)
                ),
            ),
        ),
        (
            -1.0,
            sim.add_flux(
                fcen,
                df,
                nfreq,
                mp.FluxRegion(
                    center=mp.Vector3(-BOX, 0, 0), size=mp.Vector3(0, 2 * BOX, 0)
                ),
            ),
        ),
    ]
    # Incident-intensity probe: NARROW transverse line (0.2) at the particle
    # plane (x=0) = the illumination the particle sees. A 0.6-wide probe
    # averages in diffractive beam edges: edge dimming grows with lambda,
    # tilting sigma UP at long lambda and redshifting the peak (Job 1139:
    # 490nm vs analytic 470nm with the 0.6 probe). Registered BEFORE run.
    inc_mon = sim.add_flux(
        fcen,
        df,
        nfreq,
        mp.FluxRegion(center=mp.Vector3(0, 0, 0), size=mp.Vector3(0, 0.2, 0)),
    )
    sim.run(until_after_sources=run_time)
    total = np.zeros(nfreq)
    for sign, m in monitors:
        total += sign * np.array(mp.get_fluxes(m))
    inc = np.array(mp.get_fluxes(inc_mon))
    return total, inc / 0.2  # box net flux, incident intensity (per um)


def spectrum_at(resolution, run_time):
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "common"))
    import meep as mp  # noqa: F401
    from materials import au_rakic

    # Band centered for the SOURCE WEIGHT, not the old guess: fcen=1/0.55 put
    # the analytic 470nm peak at 5% source weight (mask edge), so every run
    # "converged" to the 490nm mask edge (Jobs 1064-1144 + r25 diag).
    # fcen=1/0.52, df=1.0 => lam 0.41-0.70 with 470nm at ~40% weight.
    fcen, df, nfreq = 1 / 0.52, 1.0, 60
    geo = [mp.Cylinder(RADIUS, material=au_rakic())]
    box, _inc_loaded = box_flux(resolution, geo, fcen, df, nfreq, run_time)
    box0, inc0 = box_flux(resolution, [], fcen, df, nfreq, run_time)
    # Au absorbs: loaded-box net flux is SMALLER than empty (net power sinks
    # into the particle). (box0 - box) is the absorbed power; dividing by the
    # EMPTY-run incident intensity gives the absorption width (cross-section
    # per unit wire length). Normalization is essential: without it the
    # spectrum carries |source(f)|^2 and the peak sits at fcen regardless of
    # physics. Mask points where the source is weak (<5% of max).
    with np.errstate(divide="ignore", invalid="ignore"):
        sigma = (box0 - box) / np.maximum(inc0, 1e-30)
    valid = inc0 > 0.05 * np.max(inc0)
    sigma[~valid] = np.nan
    f = np.linspace(fcen - df / 2, fcen + df / 2, nfreq)
    return f, sigma


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--resolution", type=float, default=120)
    ap.add_argument("--run_time", type=float, default=80)
    ap.add_argument("--outdir", default="outputs")
    a = ap.parse_args()
    import meep as mp

    os.makedirs(a.outdir, exist_ok=True)
    resolutions = sorted({40, 80, int(a.resolution)})
    peaks = []
    f = np.zeros(60)
    scat = np.zeros(60)
    for res in resolutions:
        f, scat = spectrum_at(res, a.run_time)
        lam_nm = 1 / f * 1000
        peak = float(lam_nm[np.nanargmax(scat)])
        peaks.append(peak)
        if mp.am_master():
            print(f"res={res}: dipolar peak ~{peak:.0f} nm", flush=True)
    if mp.am_master():
        np.savetxt(
            os.path.join(a.outdir, "mie.csv"),
            np.column_stack([1 / f, scat]),
            header=f"meep={mp.__version__} res={a.resolution} radius_um={RADIUS} "
            f"cols=wavelength_um,sigma_abs_um peak_nm={peaks[-1]:.0f}",
            delimiter=",",
        )
        np.savetxt(
            os.path.join(a.outdir, "mie_res_sweep.csv"),
            np.column_stack([resolutions, peaks]),
            header="cols=res,peak_nm (convergence: peak must stabilize)",
            delimiter=",",
        )
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
        ax1.plot(1 / f * 1000, scat, label="FDTD")
        # Same-fit analytic reference (diag_mie_analytic.py, validated 2D-Mie):
        # direct overlay, same units (um per unit wire length).
        ana_path = os.path.join(a.outdir, "mie_analytic.csv")
        ana_peak = None
        if os.path.exists(ana_path):
            ana = np.loadtxt(ana_path, delimiter=",", comments="#")
            ax1.plot(ana[:, 0], ana[:, 1], "--", label="analytic 2D-Mie")
            ana_peak = float(ana[np.argmax(ana[:, 1]), 0])
            ax1.legend()
        ax1.set_title(f"Au cylinder absorption width (res={a.resolution})")
        ax1.set_xlabel("wavelength (nm)")
        ax1.set_ylabel("sigma_abs (um)")
        ax2.plot(resolutions, peaks, "o-")
        if ana_peak is not None:
            ax2.axhline(ana_peak, ls="--", label=f"analytic {ana_peak:.0f} nm")
            ax2.legend()
        ax2.set_xlabel("resolution (px/um)")
        ax2.set_ylabel("peak (nm)")
        ax2.set_title("convergence")
        fig.savefig(os.path.join(a.outdir, "mie.png"))
        plt.close(fig)
        if ana_peak is not None:
            print(
                f"peak at {peaks[-1]:.0f} nm vs analytic {ana_peak:.0f} nm "
                f"(delta={peaks[-1] - ana_peak:+.0f} nm, gate: |d|<=10nm)"
            )
        else:
            print(f"peak at {peaks[-1]:.0f} nm (gate: analytic ±10nm at convergence)")


if __name__ == "__main__":
    main()
