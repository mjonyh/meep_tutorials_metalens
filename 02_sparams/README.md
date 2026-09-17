# Module 2: Dispersion, Effective Media & S-Parameters

## 1. Objectives

By end of this unit, you will be able to:

- O2.1: Build a dispersive/layered `Medium` stack (`Medium(epsilon=...)`, `LorentzianSusceptibility`/`DrudeSusceptibility` pattern) and state where the fit enters the `Simulation` geometry.
- O2.2: Extract S-parameters with empty-run normalization: `add_flux` / `get_fluxes`, `R = -(r - r0)/r0`, `T = t/t0`, `A = 1 - R - T`, with sign-safe guards and clip to `[0, 1]`.
- O2.3: State the homogenization limit: a subwavelength stack behaves as one effective medium only while period << λ (breakdown demonstrated at period ~λ/5).

## 2. Outcomes — What You Must Show

| # | Artifact | Pass threshold |
|---|----------|----------------|
| E2.1 | `expected_figs/bragg.csv` + `expected_figs/bragg.png` (8-bilayer Si/SiO2 DBR) | Stopband peak R = 1.003 (gate: R > 0.95); TMM/Fresnel overlay shape matches |
| E2.2 | `expected_figs/grating.csv` + `expected_figs/grating.png` (Si grating, period 0.8 um) | T = 0.51–0.63 across band, no NaN, no T > 1 after fix |
| E2.3 | `expected_figs/effmedium.csv` + `expected_figs/period_sweep.png` (period sweep) | T = 0.99 / 0.95 / 0.41 / 0.0007 / 0.88 at periods 0.05 / 0.10 / 0.20 / 0.31 / 0.50 um; collapse at λ/5 = 0.31 um demonstrates breakdown |
| Gate | Energy check on Bragg off-resonance | Median \|R+T-1\| = 0.0037 (PASS, gate 1±0.02 off-resonance); caveat: band-edge/short-λ points deviate up to 0.096 — resolution note applies, see §3.5 |

## 3. Body

### 3.1 Prerequisites and files

| Lab | Script | Sbatch | Figure |
|-----|--------|--------|--------|
| 03 Bragg DBR | `sim_03_bragg.py` | `sim_03_bragg.sbatch` | `expected_figs/bragg.png` |
| 04 Grating | `sim_04_grating.py` | `sim_04_grating.sbatch` | `expected_figs/grating.png` |
| 05 Effective medium | `sim_05_effmedium.py` | `sim_05_effmedium.sbatch` | `expected_figs/period_sweep.png` |

All runs: resolution 30, 4 MPI tasks, `meep/1.28.0`.

### 3.2 Run commands (copy-pasteable)

```bash
module purge
module load gcc/12.4 openmpi/5.0.10 openblas/0.3.34 fftw/3.3.11 hdf5/1.14.6 python/3.11.9 meep/1.28.0
cd /home/mjonyh/meep_tutorial/02_sparams
sbatch sim_03_bragg.sbatch      # Job 1024, ~1 s/rank
sbatch sim_04_grating.sbatch    # Job 1028, ~3 s/rank
sbatch sim_05_effmedium.sbatch  # Job 1026, ~4.4 s/rank
squeue -u $USER
```

Verify outputs:

```bash
head -3 expected_figs/bragg.csv expected_figs/grating.csv expected_figs/effmedium.csv
python3 -m py_compile sim_03_bragg.py sim_04_grating.py sim_05_effmedium.py
```

### 3.3 Lab 03 — Bragg mirror (guided)

8-bilayer Si (eps 11.7, d = 0.11 um) / SiO2 (eps 2.1025, d = 0.27 um), cell 10 um, PML 1.0, fcen 0.65 / df 0.7 / nfreq 80, `until_after_sources=150`.

Key lines (`sim_03_bragg.py:71-75`):

```python
R = -(r - r0) / np.maximum(r0, 1e-12)
T = t / np.maximum(t0, 1e-12)
R = np.clip(R, 0.0, None)
T = np.clip(T, 0.0, None)
```

Result (Job 1024): peak R = 1.003, gate > 0.95 PASS. Off-resonance median |R+T-1| = 0.0037 PASS.

Stretch: overlay analytic TMM on `bragg.png`; sweep resolution 20 → 60 and record peak-R drift.

### 3.4 Lab 04 — Grating (guided + debug record)

Si block grating, period 0.8 um, fill 0.5, h 0.4 um; PML only in Y; normal incidence.

Debug record (Jobs 1025/1027 FAIL → 1028 PASS):

| Job | Symptom | Fix |
|-----|---------|-----|
| 1025/1027 | Source/monitor at y = ±2 sat on PML edge (cell 6 + PML 1.0 → interior \|y\| ≤ 2); unphysical T | Move source/monitor to y = ±1.5 (`sim_04_grating.py:20,36`) |
| 1025/1027 | Signed-flux collapse: both fluxes negative (power flows -y), so `max(t0, eps)` collapses to eps | Sign-safe guard (`sim_04_grating.py:63-65`): `T = where(|t0|>eps, t/t0, 0)` |

Signed-flux lesson: **never `max()` a signed flux.** `get_fluxes` returns signed power. Dividing two same-sign fluxes is positive; clamping the denominator with `max(x, eps)` destroys the sign. Use `where(|ref|>eps, x/ref, 0)`.

Result (Job 1028): T = 0.51–0.63 over 20 points, ~3 s/rank.

Stretch: tilt `k_point` for 1st-order scan; locate Wood anomaly.

### 3.5 Lab 05 — Effective medium (guided)

6-cell Si/SiO2 stack at λ = 1.55 um; periods 0.05 / 0.10 / 0.20 / 0.31 / 0.50 um; normalize by empty-run flux; clip T to [0, 1].

Result (Job 1026), ~4.4 s/rank:

| Period (um) | T |
|-------------|------|
| 0.05 | 0.99 |
| 0.10 | 0.95 |
| 0.20 | 0.41 |
| 0.31 (= λ/5) | 0.0007 |
| 0.50 | 0.88 |

Read: T ≈ 1 while period << λ; collapse at λ/5 = 0.31 um is the homogenization breakdown. Period 0.50 um recovers high T via a different interference condition, not via homogenization.

Stretch: add period 0.15 um; compare against volume-averaged `epsilon_eff` TMM prediction.

### 3.6 Resolution caveat (Bragg)

Bragg at resolution 30: median |R+T-1| = 0.0037 (PASS), but band-edge/short-λ points deviate up to 0.096. Cause: fixed grid under-resolves thin high-index layers where phase accumulates fastest. Action: re-run `--resolution 60` before quoting band-edge R in a proposal; record the convergence delta.

### 3.7 Flux-sign fix (applies to all three labs)

- R monitor sees incident + reflected: `R = -(r - r0)/r0`. Old form `-r/r0` gives R-1 (unphysical negative R).
- Always run the empty geometry with identical cell/source/monitor; never divide by an analytic constant.
- Clip to [0, 1] after normalization; log `meep.__version__`, resolution, cell size to CSV header.

## 4. Self-check + research bridge

Self-check:

1. Why does the R monitor require subtracting the empty run, while the T monitor only requires division?
2. What goes wrong when a flux monitor or source sits on the PML edge, and how do you detect it?
3. At what period-to-wavelength ratio did the stack stop behaving as an effective medium, and what observable proved it?

Research bridge: empty-run-normalized S-parameters are the input to every retrieval that follows — band-edge group-delay extraction (Module 3), absorber impedance matching (Module 4), and meta-atom T/phase libraries (Module 5). The homogenization breakdown measured here is the reason metasurface design uses full-wave phase libraries instead of effective-index shortcuts.

> Tested: 2026-09-16, `sbatch sim_03_bragg.sbatch` (JobID 1024, peak R=1.003, ~1 s/rank), `sbatch sim_04_grating.sbatch` (JobID 1028, T=0.51–0.63, ~3 s/rank; Jobs 1025/1027 FAIL→1028 PASS), `sbatch sim_05_effmedium.sbatch` (JobID 1026, T=0.99/0.95/0.41/0.0007/0.88, ~4.4 s/rank), meep/1.28.0, 4 tasks, resolution 30, outputs in `expected_figs/`
