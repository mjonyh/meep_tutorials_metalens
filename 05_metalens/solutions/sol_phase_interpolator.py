"""Module 5 Stretch Solution | Meta-atom phase-to-diameter library interpolation
Run: python3 sol_phase_interpolator.py [--focal_length F --diameter D]
Demonstrates: Filtering high-transmission library points and synthesizing radial pillar arrangements.
"""

import argparse
import os
import numpy as np

pkg_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.join(pkg_dir, "..")
lib_path = os.path.join(parent_dir, "expected_figs", "library.csv")


def load_library(path=lib_path, min_transmission=0.5):
    """Load meta-atom library and extract monotonic high-transmission branch."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"Library not found at {path}. Run sim_12_library.py first.")

    # Cols: diameter, T, phase
    data = np.loadtxt(path, delimiter=",")
    d, T, phi = data[:, 0], data[:, 1], data[:, 2]

    # Filter out low-transmission or steep branch regions
    mask = T >= min_transmission
    d_filt = d[mask]
    phi_filt = phi[mask]

    # Unwrap phase
    unwrapped = np.unwrap(phi_filt)
    sort_idx = np.argsort(unwrapped)
    return unwrapped[sort_idx], d_filt[sort_idx]


def design_lens_profile(f, D, period=0.7, lam=1.55):
    """Compute required diameters across 1D cylindrical lens."""
    phi_vals, d_vals = load_library()
    span = phi_vals[-1] - phi_vals[0]

    xs = np.arange(-D / 2, D / 2 + period / 2, period)
    # Hyperbolic phase profile
    target_phi = -2 * np.pi / lam * (np.sqrt(f**2 + xs**2) - f)
    wrapped_phi = target_phi % (2 * np.pi)

    # Scale wrapped 0..2pi into available library span
    scaled_targets = phi_vals[0] + (wrapped_phi / (2 * np.pi)) * span
    diameters = np.interp(scaled_targets, phi_vals, d_vals)

    return xs, wrapped_phi, diameters


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--focal_length", type=float, default=6.0, help="Focal length in um")
    ap.add_argument("--diameter", type=float, default=20.0, help="Lens aperture in um")
    a = ap.parse_args()

    xs, phi, ds = design_lens_profile(a.focal_length, a.diameter)

    print(f"Synthesized cylindrical metalens: f={a.focal_length} um, D={a.diameter} um")
    print(f"Number of pillars: {len(xs)}")
    print(f"Pillar diameter span: {ds.min():.3f} um to {ds.max():.3f} um")
    print(f"{'Position x (um)':<18} {'Target Phase (rad)':<20} {'Selected Pillar d (um)':<22}")
    print("-" * 60)
    for x, p, d in zip(xs[::4], phi[::4], ds[::4]):
        print(f"{x:<18.2f} {p:<20.3f} {d:<22.3f}")

    outdir = os.path.join(pkg_dir, "outputs")
    os.makedirs(outdir, exist_ok=True)
    out_csv = os.path.join(outdir, "lens_layout.csv")
    np.savetxt(
        out_csv,
        np.column_stack([xs, phi, ds]),
        header="x_um,target_phase_rad,diameter_um",
        delimiter=",",
        fmt=["%.3f", "%.4f", "%.4f"],
    )
    print(f"\nSaved synthesized layout to {out_csv}")


if __name__ == "__main__":
    main()
