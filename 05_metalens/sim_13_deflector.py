"""13 beam deflector 8-element | Objective: anomalous angle vs generalized Snell | Outcome: outputs/deflector.csv + farfield.png, ±3°.
Run: module load <chain> && srun --mpi=pmix -n 4 python3 sim_13_deflector.py [--resolution R] | Walltime: ~12 min (Job 1070: 16.1°=16.1°, eff 0.87)
"""

import argparse
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "common"))
from materials import si_nir, sio2

PERIOD, N, LAM = 0.7, 8, 1.55
H_PILLAR = 1.4  # same meta-atom as sim_12 library (H=0.9 covers only 3.4 rad)
# 8 phase levels interpolated from the sim_12 H=1.4 library (res 30):
# equidistant unwrapped phases 0.21..5.79 rad, all T>=0.6 (2026-09-16).
# Span is 5.58 rad, 11% short of 2pi: expect measured angle ~11% below
# generalized-Snell theory (gate is +/-3 deg absolute -- still passes).
DIAMETERS = [0.120, 0.138, 0.156, 0.183, 0.218, 0.259, 0.316, 0.415]
Y_MEAS = -1.8  # transverse cut below substrate (interior: |y|<=2.0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--resolution", type=float, default=30)
    ap.add_argument("--outdir", default="outputs")
    a = ap.parse_args()
    import meep as mp

    os.makedirs(a.outdir, exist_ok=True)
    super_p = PERIOD * N
    theory = float(np.arcsin(LAM / super_p))
    cell = mp.Vector3(super_p, 5, 0)
    geo = [
        mp.Block(
            mp.Vector3(mp.inf, 0.5, mp.inf),
            center=mp.Vector3(0, -1.2, 0),
            material=sio2(),
        )
    ]
    for i in range(N):  # picked 0..2π library entries (see DIAMETERS)
        d = DIAMETERS[i]
        geo.append(
            mp.Cylinder(
                d / 2,
                height=H_PILLAR,
                axis=mp.Vector3(0, 1, 0),
                center=mp.Vector3(
                    -super_p / 2 + (i + 0.5) * PERIOD, -0.95 + H_PILLAR / 2, 0
                ),
                material=si_nir(),
            )
        )
    src = [
        mp.Source(
            mp.ContinuousSource(1 / LAM),
            component=mp.Ez,
            center=mp.Vector3(0, 1.5, 0),
            size=mp.Vector3(super_p, 0, 0),
        )
    ]
    sim = mp.Simulation(
        cell_size=cell,
        geometry=geo,
        sources=src,
        resolution=a.resolution,
        boundary_layers=[mp.PML(0.5, direction=mp.Y)],
        # Supercell must be periodic in x (FFT order analysis assumes it).
        # Default boundaries are PEC metal: without k_point the side walls
        # mirror the supercell and spoil the anomalous order.
        k_point=mp.Vector3(0, 0, 0),
        force_complex_fields=True,
    )
    sim.run(until=80)
    # Transverse field cut -> angular spectrum via FFT (x is periodic with
    # period super_p, so FFT bins are the diffraction orders).
    nx = 240
    xs = np.linspace(-super_p / 2, super_p / 2, nx, endpoint=False)
    ez = np.array(
        [sim.get_field_point(mp.Ez, mp.Vector3(float(x), Y_MEAS)) for x in xs]
    )
    spec = np.fft.fftshift(np.fft.fft(ez))
    kx = np.fft.fftshift(np.fft.fftfreq(nx, d=super_p / nx))  # cycles/um
    k0 = 1 / LAM
    valid = np.abs(kx) < k0  # propagating orders only
    order = int(np.argmax(np.abs(spec[valid])))
    kx_all = kx[valid]
    kx_peak = float(kx_all[order])
    theta_meas = float(np.arcsin(np.clip(kx_peak / k0, -1, 1)))
    # Efficiency: power in the peak order vs total propagating power.
    eff = float(np.abs(spec[valid][order]) ** 2 / np.sum(np.abs(spec[valid]) ** 2))
    if mp.am_master():
        np.savetxt(
            os.path.join(a.outdir, "deflector.csv"),
            np.array([[theory, theta_meas, eff]]),
            header=f"meep={mp.__version__} res={a.resolution} "
            "cols=theory_rad,measured_rad,order_eff",
            delimiter=",",
        )
        np.savetxt(
            os.path.join(a.outdir, "deflector_spectrum.csv"),
            np.column_stack([kx, np.abs(spec) ** 2]),
            header="cols=kx_cyc_per_um,intensity",
            delimiter=",",
        )
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots()
        ax.plot(kx / k0, np.abs(spec) ** 2, "o-", ms=3)
        ax.axvline(np.sin(theory), ls="--", label="theory")
        ax.axvline(np.sin(theta_meas), ls=":", label="measured")
        ax.set_title(f"deflector orders (res={a.resolution})")
        ax.set_xlabel("kx/k0 (= sin θ)")
        ax.set_ylabel("intensity (arb)")
        ax.legend()
        fig.savefig(os.path.join(a.outdir, "farfield.png"))
        plt.close(fig)
        mp.output_efield_z(sim)
        print(
            f"theory={np.degrees(theory):.1f}° measured={np.degrees(theta_meas):.1f}° "
            f"(gate ±3°), order eff={eff:.2f}"
        )


if __name__ == "__main__":
    main()
