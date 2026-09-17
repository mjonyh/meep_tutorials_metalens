# Module 5: Gradient Metasurfaces + Metalens

Prerequisites: Modules 1–4 (flux normalization, `k_point` periodicity, dispersive-material stability). Time: 3 h (20' recap · 30' crash · 30' demo · 90' lab · 10' show-and-tell). All jobs: `compute` partition, 4 tasks, meep/1.28.0.

## 1. Objectives

- O5.1: Build a Si-pillar meta-atom library (period 0.7 um, H=1.4 um, λ=1.55 um) reporting transmission T and phase via `get_field_point` with `force_complex_fields=True`, normalized to a bare-substrate reference run.
- O5.2: Assemble an 8-element supercell deflector and a hyperboloidal cylindrical lens with phase profile φ(r) = −2π/λ · (√(f² + r²) − f); extract deflection angle by FFT order analysis and focal spot by axial + transverse cuts.
- O5.3: Draft a 1-page capstone proposal (choice a/b/c below) with convergence evidence and a 5-minute lightning talk.

## 2. Outcomes — What You Must Show

| # | Artifact | Pass threshold |
|---|----------|----------------|
| E5.1 | `outputs/library.csv` + `expected_figs/T-phase.png` (dense sweep: uniform 0.004 grid + 0.002/0.0005 resonance-branch fills, n=269, res 30) | Circular coverage 6.20 rad, max wrapped gap 0.088 rad (5°); T≥0.25 keeps 6.20 (n=260, Tmin 0.016 at isolated zero d≈0.52). Unwrapped ptp 9.23 double-counts winding — NOT the metric. Campaign: 1069 13pt 4.64 → 1131 wrong-dir fail → 1132 5.45 → 1133 5.09 (non-monotonic-branch lesson) → 1134 5.92 → 1135 5.92 tail → 1136 6.08 → 1137 6.18 → 1138 6.20. |
| E5.2 | `outputs/deflector.csv` + `deflector_spectrum.csv` + `expected_figs/farfield.png` (8-pillar supercell, res 30) | Theory 16.1° = measured 16.1°, error 0.0° (±3° PASS); peak-order efficiency 0.87 (propagating-power fraction). |
| E5.3 | `outputs/focus.csv` + `axial.csv` + `expected_figs/focal-cut.png` (20 um lens, f=6.0, λ=1.55 um, res 25) + capstone proposal | Focus y=5.80 (design 6.0); FWHM=0.625 um vs λ/2NA=0.904 um (NA=0.857); efficiency 0.420 (main-lobe vs empty-run power). Proposal graded on convergence evidence, not plot beauty. |

## 3. Body

### 3.1 Concept crash (minimal theory)

| Concept | Statement |
|---|---|
| Meta-atom | Subwavelength Si pillar (eps 11.7) on SiO2 substrate (eps 2.1025); diameter tunes Mie-type resonance → transmitted phase. Period 0.7 um < λ keeps cell subwavelength. |
| Generalized Snell | Phase gradient dφ/dx = 2π/Λ (Λ = supercell period N·p) steers to sin θ = λ/Λ at normal incidence. Here Λ = 8 × 0.7 = 5.6 um → θ = arcsin(1.55/5.6) = 16.1°. |
| Hyperboloidal lens | φ(r) = −2π/λ · (√(f² + r²) − f) equalizes path length to focus f. Diffraction limit FWHM ≈ λ/2NA, NA = sin(atan((W/2)/f)). Here W=20, f=6.0 → NA=0.857 → λ/2NA=0.904 um. |
| Measurement | Complex-field steady state (`ContinuousSource` + `force_complex_fields=True`) → `get_field_point(mp.Ez, ...)` gives true amplitude/phase. Library T/phase quoted relative to bare-substrate run. |

### 3.2 Run commands (copy-pasteable)

```bash
module purge
module load gcc/12.4 openmpi/5.0.10 openblas/0.3.34 fftw/3.3.11 hdf5/1.14.6 python/3.11.9 meep/1.28.0
sbatch sim_12_library.sbatch    # Job 1138, res 30, ~51 s/rank (dense sweep n=269 × until=60)
sbatch sim_13_deflector.sbatch  # Job 1070, res 30, ~740 s/rank (~12 min, until=80)
sbatch sim_14_metalens.sbatch   # Job 1071, res 25, ~1387 s/rank (~23 min, 2 runs × until=120)
```

Stagger launches (2-node limit). Do not run the lens interactively; it runs two full simulations (lens + empty reference for efficiency). Queue >30 min → use precomputed `fallback_data/` (focus.csv, axial.csv, focal-cut.png from Job 1071; provenance in `fallback_data/README.md`) for analysis, then run overnight.

| Sim | sbatch | Resolution | Walltime (per rank) | Outputs |
|---|---|---|---|---|
| 12 library | `sim_12_library.sbatch` | 30 | ~51 s | `outputs/library.csv`, `outputs/T-phase.png` |
| 13 deflector | `sim_13_deflector.sbatch` | 30 | ~740 s (~12 min) | `outputs/deflector.csv`, `outputs/deflector_spectrum.csv`, `outputs/farfield.png`, `sim_13_deflector-ez-*.h5` |
| 14 metalens | `sim_14_metalens.sbatch` (limit 01:00:00) | 25 | ~1387 s (~23 min) | `outputs/focus.csv`, `outputs/axial.csv`, `outputs/focal-cut.png`, `metalens-ez-*.h5` |

### 3.3 Guided lab

1. Library (`sim_12_library.py`): unit cell 0.7 × 6 um, PML 0.5 in y, `k_point=(0,0,0)` for x-periodicity, source Ez plane at y=1.0, probe at (0,−2.0) in air below substrate. Reference run on bare substrate; dense diameter sweep Job 1138 (uniform 0.004 grid + 0.002/0.0005 resonance-branch fills, n=269). Check `library.csv` header (`meep=1.28.0 res=30.0 lam=1.55`). Plot `T-phase.png`: T vs d on left axis, unwrapped phase on right. Gate metric is circular coverage 6.20 rad (max wrapped gap 0.088 rad); unwrapped ptp 9.23 is recorded but NOT the metric.
2. Deflector (`sim_13_deflector.py`): 8 pillars at DIAMETERS = [0.120, 0.138, 0.156, 0.183, 0.218, 0.259, 0.316, 0.415] (interpolated equidistant unwrapped phases 0.21–5.79 rad, all T≥0.6; span 5.58 rad, 11% short of 2π). Supercell 5.6 × 5 um, PML 0.5 in y, `k_point=(0,0,0)`. Transverse cut at y=−1.8 (240 points) → FFT; bins are diffraction orders. Read `deflector.csv`: `theory_rad, measured_rad, order_eff`. Confirm `farfield.png` peak at kx/k0 = sin(16.1°).
3. Metalens (`sim_14_metalens.py`): 20 um aperture, pillars from `phase_to_d` map over library monotonic branch (d=0.12–0.495, phase 0.21–6.18 rad, span scaled to 2π; ~5% gradient shortfall). Cell (W+4) × 16 um, PML 1.0 all sides, source below at y=−4.0. Axial scan y=0–7 (141 pts) locates focus; transverse cut (321 pts) gives FWHM; empty rerun at same plane gives efficiency (lobe |x|≤1.5·FWHM). Read `focus.csv` header: `y_focus=5.80 fwhm=0.625 dl=0.904 eff=0.420`.

### 3.4 Stretch tasks

- Resolution: rerun library at `--resolution 20` and 40; tabulate coverage and T max. Expect T overshoot to shrink toward ≤1.0 as probe/substrate interference resolves.
- Deflector: drop element 8 (use 7 pillars) and recompute angle/efficiency; quantify sidelobe growth in `deflector_spectrum.csv`.
- Lens NA: change `F_LEN` 6.0 → 10.0 (rebuild; note focus must stay inside cell |y|≤8) and compare measured FWHM to new λ/2NA.

### 3.5 Debug table

| Symptom | Cause | Fix |
|---|---|---|
| Library coverage ≈3.4 rad (cf. Job 1065: 3.37 rad) | Diameter sweep or pillar height too narrow (H=0.9 covers 3.88 rad) | Use H=1.4, d=0.12–0.62 (Job 1069: 13 pts, log-span 6.70; superseded by dense sweep Job 1138: circular 6.20 rad) |
| T > 1 (here max 1.022) | Substrate-normalized ratio; probe-phase interference, not gain | Quote max honestly; check convergence with resolution sweep |
| Circular coverage (6.20 rad) < unwrapped span (9.23 rad) | Unwrapped ptp double-counts winding and non-monotonic resonance branch; wrapped max gap 0.088 rad is the honest gap metric | Report both; pick deflector/lens diameters from monotonic branch |
| Deflector angle off by >3° | Missing `k_point` (PEC side walls mirror supercell) or cut placed in PML/inside substrate | Keep `k_point=(0,0,0)`; cut at y=−1.8 (interior, \|y\|≤2.0) |
| Lens focus outside cell / no peak | Old f=10 put focus at y≈8.7, outside cell | f=6.0 → focus y≈5.8, inside cell; axial scan y=0–7 finds it |
| Lens job hits time limit | Two until=120 runs at res 25 take ~23 min on 4 cores | Keep 01:00:00 limit in `sim_14_metalens.sbatch`; stagger; use `fallback_data/` (Job 1071) for analysis |

### 3.6 Capstone proposal (O5.3, 30 min + lightning talks)

Pick one; 1 page + 5-min talk. Grading: convergence evidence + methods clarity.

- (a) BIC-inspired grating: start from Module 2 grating; add symmetry-breaking perturbation, track Q vs asymmetry with resolution table.
- (b) Sensing absorber: start from Module 4 MIM absorber; sweep background index, report nm/RIU + FWHM with PML/runtime controls.
- (c) Extended NA study: extend this lens (wider W or shorter f); report FWHM vs λ/2NA + efficiency vs NA, with res-20/25/30 convergence column.

Template: question, geometry + APIs, numeric gate, walltime budget (≤25 min/4 cores or fallback plan), risk + fallback.

## 4. Self-check + research bridge

Self-check:

1. Why must library T/phase be normalized to a bare-substrate run instead of quoting raw |E|?
2. The dense sweep reports unwrapped ptp 9.23 rad but circular coverage 6.20 rad with a 0.088 rad gap. Which metric controls whether an 8-level 0–2π set exists, and why does the deflector still hit 16.1° exactly?
3. Lens FWHM (0.625 um) is below λ/2NA (0.904 um) while efficiency is 0.420. Name two analysis choices (FWHM estimator, efficiency normalization, 2D vs 3D) that can bias each number, and what control you would run.

Research bridge: this module is the forward-solver baseline for inverse design. Next steps: `meep.adjoint` for gradient-based pillar-shape optimization against the 0.088 rad gap; Bayesian optimization over diameter/height using the library CSV as prior; MPB cross-check of the pillar waveguide dispersion behind the phase branch; fabrication constraints (aspect 12.5:1 at H=1.4, minimum 120 nm feature) that turn the T-gate (T≥0.25 keeps 6.20, Tmin 0.016 at isolated zero d≈0.52) and gap analysis into a yield model for the proposal.

> Tested: 2026-09-17, `sbatch sim_12_library.sbatch` Job 1138 + `sbatch sim_13_deflector.sbatch` Job 1070 + `sbatch sim_14_metalens.sbatch` Job 1071, meep/1.28.0, 4 tasks, ~51 s + ~740 s + ~1387 s per rank, outputs in `expected_figs/` (library.csv, T-phase.png, deflector.csv, deflector_spectrum.csv, farfield.png, focus.csv, axial.csv, focal-cut.png) — library GREEN: dense sweep n=269, circular 6.20 rad, gap 0.088 rad
