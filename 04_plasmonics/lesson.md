# Module 4: Plasmonics & Mie — Lossy, Subwavelength, Resonant

## 1. Objectives

- O4.1: Run stable dispersive-metal FDTD. Use `force_complex_fields=True` for CW
  runs, mesh metal interfaces at resolution >= 40, respect the Courant limit
  (MEEP sets `dt` from resolution; do not override it). Import Au/Ag only from
  `common/materials.py` (`au_rakic`, `ag_rakic` — upstream `meep.materials`,
  Rakic 1998 via `eV_um_scale`). No inline metal epsilons, no hand-converted
  eV poles (Job 1035 blew up with `fields are NaN or Inf` from that error).
- O4.2: Quantify scattering, absorption, and field enhancement with a
  convergence note. Extract a Mie absorption-width spectrum with empty-run
  normalization, quote slit enhancement `|E|/|E0|` at the converged
  resolution, and report absorber peak `A` with a patch-width sweep plus a
  resolution table.

## 2. Outcomes — What You Must Show

| # | Artifact | Pass threshold | Verdict |
|---|----------|----------------|---------|
| E4.1 | `expected_figs/mie.csv` + `mie.png` (with analytic overlay) + `mie_res_sweep.csv` + `mie_analytic.csv` | Convergence + lit-match: res sweep 522 → 468 → 468 nm (40/80/120); FDTD 468 nm vs same-fit analytic 470 nm → delta −2 nm (gate \|d\| ≤ 10 PASS); stable, no blow-up; NaN 47% = band-edge mask by design | **PASS (GREEN)** — Job 1146: `srun --mpi=pmix -n 4 python3 sim_09_mie.py --resolution 120`, meep/1.28.0, 4 true-MPI tasks, ~15 s/rank. Valid window 454–596 nm. Staged in `expected_figs/` |
| E4.2 | `expected_figs/slit.csv` + field map (`slit-*.h5`) | Enhancement quoted at res 80: center 0.14/0.93/1.27x, max 0.15/0.96/1.29x at λ = 0.55/0.65/0.80 um; stable, no NaN | PASS (stability). Enhancement **MARGINAL** (~1.3x max) — quote, do not oversell |
| E4.3 | `expected_figs/absorber.csv` + `absorber_spectra.csv` + `absorber.png` + spacer slices (`absorber_spacer15nm.csv`, `absorber_spacer20nm.csv`, `absorber_spectra_spacer15nm.csv`) | Gate A > 0.90 | **PASS (GREEN)** — Job 1102: best A = 0.902 at w = 0.20 um, spacer 15 nm, res 160, `run_time` 120. Spacer trend: 50 nm→0.40 / 40 nm→0.58 / 30 nm→0.75 (res 80, Job 1098) / 20 nm→0.833 (res 120, Job 1100) / 15 nm→0.902 (res 160, Job 1102). NaN 33.8% = band-edge incident mask (<5% max), by design. Staged in `expected_figs/` |

## 3. Body

### 3.1 Concept crash (15')

Dispersive metals need auxiliary-differential-equation FDTD: each Lorentz/Drude
pole adds internal fields, tightens the Courant limit, and punishes coarse
interface meshing. Three rules carry the module:

1. CW steady-state amplitude requires complex fields (`force_complex_fields`).
   A real-field snapshot at one time step reads an arbitrary RF phase.
2. Flux has a sign. MEEP orients every flux region along the fixed +axis, so a
   closed-box "sum" must be sign-corrected, and reflected power must be
   normalized against the empty run with the sign preserved.
3. Loss must be accounted for: opaque backplane implies T = 0 so A = 1 − R,
   but only where the incident spectrum is nonzero (mask band edges to NaN).

### 3.2 Commands (copy-pasteable)

```bash
module purge
module load gcc/12.4 openmpi/5.0.10 openblas/0.3.34 fftw/3.3.11 hdf5/1.14.6 python/3.11.9 meep/1.28.0
cd /home/mjonyh/meep_tutorial/04_plasmonics
sbatch sim_09_mie.sbatch        # Au cylinder, --resolution 60, sweep {40,60,80}
sbatch sim_10_slit.sbatch       # Ag slit array, --resolution 80, λ = 0.55/0.65/0.80 um
sbatch sim_11_absorber.sbatch   # MIM patch, --resolution 60, widths 0.15–0.30 um
```

| Lab | sbatch | JobID | Walltime (max rank) | Output |
|-----|--------|-------|---------------------|--------|
| 09 Mie | `sim_09_mie.sbatch` | 1146 (campaign 1064–1144) | ~15 s/rank | `outputs/mie.csv`, `mie_res_sweep.csv`, `mie.png` (analytic overlay), `mie_analytic.csv` |
| 10 slit | `sim_10_slit.sbatch` | 1043 | ~229 s/rank | `outputs/slit.csv`, `slit-*.h5` |
| 11 absorber | `sim_11_absorber.sbatch` | 1102 (campaign 1092/1094/1096/1098/1100) | ~655 s/rank (~11 min) | `expected_figs/absorber.csv`, `absorber_spectra.csv`, `absorber.png` + spacer slices |

### 3.3 Guided — Lab 09 Mie (Au cylinder, absorption width)

`sim_09_mie.py`: radius 0.05 um Au cylinder (`au_rakic`), Ey line source
(transverse to the wire axis — excites the dipolar LSP), closed-box flux
monitors with outward sign correction (`-left + right + top - bot`), incident
intensity probe at the particle plane in the empty run. Absorption width
σ = (box0 − box) / I0_empty; bins with I0 < 5% max masked to NaN.

Convergence table (`expected_figs/mie_res_sweep.csv`, Job 1146):

| resolution (px/um) | 40 | 80 | 120 |
|---|---|---|---|
| dipolar peak (nm) | 522 | 468 | 468 |

Read: peak stable 80 → 120. No blow-up. Convergence gate: PASS.

Lit-match status: **PASS (GREEN).** FDTD 468 nm vs same-fit analytic 470 nm
(`expected_figs/mie_analytic.csv`, `diag_mie_analytic.py`) → delta −2 nm
(gate |d| ≤ 10). Valid window 454–596 nm; NaN 47% = bins with I0 < 5% max
masked, by design. `mie.png` carries the analytic overlay.

Reference pinning (condensed): analytic = 2D-cylinder Mie series driven by
direct `Au.epsilon(f)` eval (eps@500nm = −2.978+2.983i), validated to 0.1% vs
quasistatic (caught during validation: missing i^n phases = exactly 1/2;
1/k0² normalization; (4/k) far-field norm; wrong spherical-derivative identity
in an abandoned sphere check). Old +20 nm offset (Jobs 1064–1144) was a
mask-edge artifact: fcen=1/0.55 put the analytic 470 nm at 5% source weight
(masked), so FDTD "converged" to the 490 nm mask edge across res/probe/cell/BC
controls (all refuted); fix = recenter fcen=1/0.52, df=1.0. Detail: F15 in
`instructor/troubleshooting.md`.

### 3.4 Guided — Lab 10 slit (Ag MIM slit, enhancement map)

`sim_10_slit.py`: Ag film (period 0.4 um, thickness 0.15 um, slit 0.08 um),
TM Ex line source, `k_point=0` periodic array, `force_complex_fields=True`,
`run(until=120)`. Enhancement = loaded / empty at slit center plus max over 9
aperture points, swept over λ = 0.55/0.65/0.80 um at fixed geometry (single-λ
gave 0.9x off-resonance).

Results (`expected_figs/slit.csv`, res 80, Job 1043):

| λ (um) | enh_center | enh_max |
|---|---|---|
| 0.55 | 0.14x | 0.15x |
| 0.65 | 0.93x | 0.96x |
| 0.80 | 1.27x | 1.29x |

Read: stable, no NaN. Best center 1.27x at 0.80 um; max-in-slit 1.29x.
Enhancement is **marginal** — consistent with an off-resonance slit
Fabry-Perot (`t ≈ λ/2n_eff` not hit). Quote 1.3x max, do not claim EOT.

### 3.5 Stretch — Lab 11 absorber (MIM patch; GREEN, Job 1102)

`sim_11_absorber.py`: Au backplane + SiO2 spacer + Au patch, period 0.4 um,
two-period cell, Ex source, `A = 1 − R` with sign-preserving empty-run
normalization, band-edge mask (|r0| < 5% max → NaN), `--run_time` argparse.

Verified run: `srun --mpi=pmix -n 4 python3 sim_11_absorber.py --resolution 160 --run_time 120`
(Job 1102, 2026-09-17, meep/1.28.0, 4 true-MPI tasks), elapsed 655 s/rank
(~11 min, within 25-min gate).

Campaign summary (RED → GREEN):

| Job | Config | Best A | Note |
|-----|--------|--------|------|
| 1056–1059 | res 60, pre-contact → contact | ≤0.361 | RED baseline; 1059 layers-in-contact 30 nm spacer |
| 1092 | contacting stack, sign-preserving normalization | 0.750 | under-coupling broken; new baseline |
| 1094 | res 100 | 0.540 | pixel-snapping noise — 30 nm at res 100 = exactly 3.0 cells |
| 1096 | `run_time` 120 → 300 | 0.750 unchanged | time-converged; runtime ruled out |
| 1098 | spacer sweep, res 80 | 50 nm→0.40 / 40 nm→0.58 / 30 nm→0.75 | critical coupling lives at one spacer per width |
| 1100 | spacer 20 nm, res 120 | 0.833 | trend holds with resolution |
| 1102 | spacer 15 nm, res 160, w = 0.20 um | **0.902 — GATE PASS (>0.90), margin thin** | state honestly; do not round up |

Gate A > 0.90: **PASS (GREEN)** on Job 1102. `absorber_spectra.csv`: NaN
33.8% of cells, all at band edges from the incident mask — by design, not
instability. No `fields are NaN` blow-up at any step. Staged in
`expected_figs/`: `absorber.csv`, `absorber_spectra.csv`, `absorber.png`,
`absorber_spacer15nm.csv`, `absorber_spacer20nm.csv`,
`absorber_spectra_spacer15nm.csv`.

What the debugging taught: (1) geometry contact first — air gaps around the
spacer killed the gap plasmon (0.03 → 0.36); (2) normalization sign second —
sign-preserving `R = −(r − r0)/r0` against the w = 0 control (A ≈ 0);
(3) spacer sweep third — one critical thickness per width (50→15 nm:
0.40 → 0.902); (4) resolution last with ≥3 cells across the spacer
(res 60→160); (5) controls that ruled knobs out: `run_time` 120→300
unchanged (time-converged), res-100 dip as discretization noise (3.0 cells).

### 3.6 Debug log (what broke, what fixed it)

| Symptom (Job) | Cause | Fix (in current code) |
|---|---|---|
| `fields are NaN or Inf` (1035) | Hand-converted eV poles passed as MEEP frequencies (24% error, top Au pole at 5.19 c/a) | `common/materials.py` delegates to upstream `meep.materials.Au/Ag` |
| Mie peak 705 nm = source center (1036/1037) | Unnormalized flux; spectrum carried `\|source(f)\|^2` | Empty-run probe normalization; mask weak-source bins |
| Mie 540 nm, no LSP (1038) | Ez drove the axial wire mode | Ey transverse drive |
| Slit 0.1x (1039) | Real-field CW snapshot reads arbitrary RF phase; TE cut off in slit | `force_complex_fields=True` + TM Ex drive |
| Absorber A = 1.0 at lowest bin (1056–1058) | Division by vanishing incident spectrum | Band-edge mask → NaN; `nanmax` peak |
| Absorber A ≈ 0.03 broadband (1056–1058) | 175 nm + 50 nm air gaps around spacer — no gap plasmon | Layers in contact (Job 1059: A = 0.361) |

## 4. Self-check + research bridge

Q1. Why does a CW run without `force_complex_fields` report an arbitrary
enhancement between 0 and the true value?
Q2. MEEP orients all flux regions along +axis. Write the outward-oriented
closed-box sum and explain what the naive all-plus sum measures instead.
Q3. The absorber campaign ran 0.36 (Job 1059, RED) → 0.902 (Job 1102, GREEN).
Which knobs moved the gate (layer contact, sign-preserving normalization,
spacer 50→15 nm, res 60→160), which controls ruled knobs out (`run_time`
120→300 unchanged in Job 1096 = time-converged; res-100 dip to 0.540 =
pixel-snapping at exactly 3.0 cells), and why are the remaining 33.8% NaNs
expected (incident <5% max mask) rather than instability?

Research bridge: this module is the stability floor for everything lossy that
follows — the vetted Au/Ag fits, the empty-run normalization habit, and the
resolution-table discipline transfer directly to the sensing-absorber capstone
(b) and to any gap-plasmon or EOT device in your own research; once Lab 11
clears A > 0.90 with a converged width/spacer map, you own a reusable
critical-coupling workflow, not just one plot.

> Tested: 2026-09-17, `srun --mpi=pmix -n 4 python3 sim_09_mie.py --resolution 120` (JobID 1146), meep/1.28.0, 4 true-MPI tasks, ~15 s/rank, outputs in `expected_figs/` (mie.csv, mie_res_sweep.csv, mie.png with analytic overlay, mie_analytic.csv) — **GREEN: res sweep 522→468→468 nm, analytic 470 nm, delta −2 nm (|d|≤10 PASS)**
> Tested: 2026-09-16, `sbatch sim_10_slit.sbatch`, JobID 1043, meep/1.28.0, 4 tasks, ~229 s/rank, outputs in `expected_figs/` (slit.csv)
> Tested: 2026-09-17, `srun --mpi=pmix -n 4 python3 sim_11_absorber.py --resolution 160 --run_time 120` (JobID 1102), meep/1.28.0, 4 true-MPI tasks, ~655 s/rank (~11 min, within 25-min gate), outputs in `expected_figs/` (absorber.csv, absorber_spectra.csv, absorber.png, absorber_spacer15nm.csv, absorber_spacer20nm.csv, absorber_spectra_spacer15nm.csv) — **GREEN: best A = 0.902 at w = 0.20 um, gate > 0.90 PASS (margin thin)**
