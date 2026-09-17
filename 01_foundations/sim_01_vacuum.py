"""01 vacuum pulse | Objective: verify c + PML echo <1% | Outcome: outputs/vacuum.csv + vacuum.png, arrival at c±2%.
Run: module load gcc/12.4 openmpi/5.0.10 openblas/0.3.34 fftw/3.3.11 hdf5/1.14.6 python/3.11.9 meep/1.28.0 && srun --mpi=pmix -n 4 python3 sim_01_vacuum.py [--resolution R]
Saves: outputs/vacuum.csv, outputs/vacuum.png | Walltime: ~1 min on 4 cores (Job 1022: c_err=0.0011, echo=0.0; clean re-run Job 1175 byte-identical)
"""

import argparse
import os

import numpy as np


def envelope(x, window):
    kernel = np.ones(window) / window
    return np.convolve(np.abs(x), kernel, mode="same")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--resolution", type=float, default=30)
    ap.add_argument("--outdir", default="outputs")
    a = ap.parse_args()
    import meep as mp

    os.makedirs(a.outdir, exist_ok=True)
    # Two probes straddle the source delay: GaussianSource peaks late
    # (t~6 for df=0.4), so absolute arrival is source-model dependent.
    # The DIFFERENCE cancels it: dx=4 apart => dt=4 at c=1, gate on that.
    # PML inner edge at |x|=5: echo reaches probe2 ~6 units after main pulse.
    src_x, x1, x2, dx = -4.0, -2.0, 2.0, 4.0
    Lx, pml_t = 12.0, 1.0
    fcen, df, dt, tmax = 0.5, 0.4, 0.05, 26.0
    cell = mp.Vector3(Lx, 0, 0)
    src = [
        mp.Source(
            mp.GaussianSource(fcen, fwidth=df),
            component=mp.Ez,
            center=mp.Vector3(src_x, 0, 0),
            size=mp.Vector3(0, 0, 0),
        )
    ]
    sim = mp.Simulation(
        cell_size=cell,
        boundary_layers=[mp.PML(pml_t)],
        sources=src,
        resolution=a.resolution,
    )
    p1, p2 = mp.Vector3(x1, 0, 0), mp.Vector3(x2, 0, 0)
    tr1, tr2 = [], []

    def grab(sim):
        # get_field_point returns complex in PyMeep 1.28; real part is the field.
        tr1.append(float(np.real(sim.get_field_point(mp.Ez, p1))))
        tr2.append(float(np.real(sim.get_field_point(mp.Ez, p2))))

    sim.run(mp.at_every(dt, grab), until=tmax)
    times = (np.arange(len(tr1)) + 1) * dt
    win = max(int(2.0 / dt), 1)  # 1 carrier period
    env1 = envelope(np.array(tr1), win)
    env2 = envelope(np.array(tr2), win)

    def centroid(env):
        peak = float(np.max(env))
        lobe = np.where(env > 0.1 * peak)[0]
        t = float(np.sum(times[lobe] * env[lobe] ** 2) / np.sum(env[lobe] ** 2))
        return t, peak, lobe

    t1, peak1, lobe1 = centroid(env1)
    t2, peak2, lobe2 = centroid(env2)
    dt_meas = t2 - t1
    c_err = abs(dt_meas - dx) / dx
    echo_win = times > (times[lobe2[-1]] + 2.0)
    echo = float(np.max(env2[echo_win]) / peak2) if np.any(echo_win) else 0.0
    if mp.am_master():
        np.savetxt(
            os.path.join(a.outdir, "vacuum.csv"),
            np.column_stack([times, tr1, tr2]),
            header=f"meep={mp.__version__} res={a.resolution} cols=t,Ez1,Ez2 "
            f"dt={dt_meas:.3f} c_err={c_err:.4f} echo={echo:.4f}",
            delimiter=",",
        )
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots()
        ax.plot(times, tr1, lw=0.7, label="Ez(x=-2)")
        ax.plot(times, tr2, lw=0.7, label="Ez(x=+2)")
        ax.axvline(t1, ls="--", label=f"t1={t1:.2f}")
        ax.axvline(t2, ls=":", label=f"t2={t2:.2f}")
        ax.set_title(f"vacuum pulse (res={a.resolution})")
        ax.set_xlabel("t (meep units, c=1)")
        ax.set_ylabel("Ez")
        ax.legend()
        fig.savefig(os.path.join(a.outdir, "vacuum.png"))
        plt.close(fig)
        print(f"dt={dt_meas:.3f} (expect {dx}), c_err={c_err:.4f} (gate <=0.02)")
        print(f"PML echo={echo:.4f} (gate <0.01)")


if __name__ == "__main__":
    main()
