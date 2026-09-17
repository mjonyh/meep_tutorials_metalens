# Instructor Troubleshooting — real failures, kept, not deleted

## 1. Objectives

- O1: Diagnose every known failure from its `slurm-*.out`/CSV signature without re-running.
- O2: Apply the recorded fix; never edit docs to pass a RED gate.
- O3: Preserve failure logs as teaching exhibits.

## 2. Outcomes — Failure log (16 records)

Rule: keep `slurm-<jobid>.out/.err`; do not delete. Fix code, re-run, log new JobID.

| # | Job(s) | Symptom (`slurm-*.out`/CSV excerpt) | Cause | Fix (file:line / action) | Status |
|---|--------|--------------------------------------|-------|--------------------------|--------|
| F1 | 1012 | `python: can't open file 'test_meep.py': [Errno 2] No such file or directory` | Submitted from repo root; relative path unresolvable | `cd 00_setup/` and resubmit (Job 1013 PASS) | Closed, kept as exhibit |
| F2 | 1021 | `arrival t=18.355 (expect 6.0), c_err=2.0592 (gate <=0.02)` / `PML echo=0.0000` | Absolute arrival gated against source peak; Gaussian turn-on delay is model-dependent | Gate on probe-to-probe `dt=t2-t1` over `dx=4` (`sim_01_vacuum.py`); Job 1022: `dt=4.004 c_err=0.0011 echo=0.0000` | Closed (1022 PASS) |
| F3a | 1025/1027 | `T=0.00` across band (grating zeros) | Source/monitor at y=±2 sat on PML edge (cell 6 + PML 1.0 → interior \|y\|<=2) | Move to y=±1.5 (`sim_04_grating.py:20,36`) | Closed (1028 PASS) |
| F3b | 1025/1027 | Same zeros persist after move in first patch | Signed-flux collapse: both fluxes negative (power flows -y); `t/max(t0,eps)` collapses denominator to eps, clip→0 | Sign-preserving guard (`sim_04_grating.py:63-65`): `T = where(\|t0\|>eps, t/t0, 0)`. Lesson: never `max()` a signed flux. Job 1028: `T=0.51-0.63` | Closed (1028 PASS) |
| F4 | 1024 | `peak R=1.003`; `median \|R+T-1\|=0.0037 PASS` but `10/80 pts deviate up to 0.096` (band-edge/short-λ) | Fixed grid under-resolves thin high-index layers where phase accumulates fastest | Resolution note + rerun `--resolution 60` before quoting band-edge R; record convergence delta | Marginal-pass, documented |
| F5 | 1036/1037/1038 vs 1064 | `Mie peak 705 nm (1036/1037)`, `540 nm (1038)`, converged `521→490→490 nm res 40/60/80 (1063/1064, ~14 s/rank, no NaN)` | 1036/1037: axial Ez drive + unnormalized flux (peak = source center); 1038: Ez drove axial wire mode | Ey transverse drive + closed-box sign-corrected sum + empty-run probe normalization + weak-source mask (`sim_09_mie.py`); lit gate closed by F15 (Job 1146, delta −2 nm) | Closed (1146 GREEN; see F15) |
| F6 | 1035 | `fields are NaN or Inf` on first metal run | Hand-converted eV poles passed as MEEP frequencies (24% error; top Au pole at 5.19 c/a) | `common/materials.py` delegates to upstream `meep.materials.Au/Ag` (Rakic 1998 via `eV_um_scale`); no inline epsilons | Closed |
| F7 | 1039 → 1043 | `enhancement 0.1x center / 0.93x` (real-field snapshot) | Real-field CW snapshot reads arbitrary RF phase; TE drive cut off in slit | `force_complex_fields=True` + TM Ex drive (`sim_10_slit.py`); Job 1043 res 80: `0.14/0.93/1.27x center, 0.15/0.96/1.29x max` at λ=0.55/0.65/0.80 um — stable, marginal (~1.3x, off-resonance slit) | Closed (stability PASS) |
| F8 | 1056/1057/1058/1059 | `best A=0.034 / 0.044 / 0.115 / 0.361` (gate >0.90); `absorber_spectra.csv: 72 NaN cells (36% of cells; 45% of A-bins)` | Under-coupling, not numerics: 1057/1058 pre-contact air gaps (175+50 nm) → A~0.03-0.04; 1059 layers-in-contact 30 nm spacer → A=0.361; NaNs are band-edge incident mask (\|r0\|<5% max), expected | Fix-and-rerun: w=0 control (A~0) → width 0.05-0.38 um sweep → spacer 20-60 nm → res 60/80/100 (>=3 cells across spacer). Outputs NOT in `expected_figs/` | RED OPEN |
| F9a | 1065 → 1069 | `coverage 3.37 rad (1065 FAIL)` → `6.70 rad claimed (1069, ~4 s/rank)` | Sweep range / pillar height too narrow (H=0.9 covers 3.88 rad) | H=1.4, d=0.12-0.62, 13 pts (`sim_12_library.py`); log-span >2π | Closed (log-span PASS) |
| F9b | 1069 note | `circular coverage 4.64 rad, max wrapped gap 1.64 rad`; `T max 1.022` | Unwrapped ptp double-counts non-monotonic resonance branch; substrate-ratio probe interference (not gain) | Quote both metrics; pick deflector/lens diameters from monotonic branch; res sweep to shrink T overshoot toward ≤1.0 | Closed (metric fixed Job 1138; see F16) |
| F10 | 1013-1071 global | `Using MPI version 3.1, 1 processes` per rank (4x serial replicas) | `srun -n 4` launches independent serial MEEP instances; no domain decomposition | OPEN: correctness unaffected (deterministic, identical files); scaling study CO1 invalid until launch fixed. Do not quote speedup | Open |
| F11 | pre-1071 | Lens focus outside cell / no peak (old f=10 → focus y~8.7, cell \|y\|<=8) | Design focus beyond cell | f=6.0 → focus y=5.80; axial scan y=0-7 (`sim_14_metalens.py`); Job 1071: `FWHM=0.625 vs dl=0.904, eff=0.420, ~1387 s/rank` | Closed (1071 PASS) |
| F12 | 1056-1058 | `A=1.0 at lowest bin` | Division by vanishing incident spectrum | Band-edge mask → NaN; `nanmax` peak | Closed (mask in current code) |
| F13 | 1090 | 4x `Using MPI version 3.1, 1 processes` (singletons) under plain `srun -n 4`; `mpirun` rejected (BYCORE binding error) | No PMI wiring under plain srun — each task size-1 singleton, no domain decomposition | Fix: `srun --mpi=pmix -n 4` (diag Job 1090: pmix → world size 4; proven with Meep `4 processes` Jobs 1092+). Canonical header + all 14 sim sbatches rolled out (Jobs 1103–1117 --test-only PASS). Quoted JobIDs ran serially (deterministic — physics stands) | Closed (launch fixed; F10 superseded) |
| F14 | 1056-1059 → 1092/1094/1096/1098/1100/1102 | Absorber per-job A: 1056-1059 ≤0.361 RED → 1092 0.750 → 1094 0.540 → 1096 0.750 → 1098 spacer trend → 1100 0.833 → 1102 0.902 PASS | Under-coupling + discretization: gapped stack, unsigned normalization, off-critical spacer, coarse res | Fixes: res 60→160, contacting layers, sign-preserving normalization, spacer 50→15 nm, `--run_time` argparse added. Controls: 1094 dip = pixel-snapping (30 nm @ res 100 = 3.0 cells); 1096 `run_time` 120→300 unchanged = time-converged. NaN 33.8% = band-edge mask by design | Closed (1102 GREEN, margin thin) |
| F15 | 1064–1146 | Mie "converged" 490 nm (res/probe/cell/BC controls all confirmed it) vs analytic 470 nm — stable +20 nm offset that survived every physics knob | Mask-edge artifact, not physics: fcen=1/0.55 put the analytic 470 nm peak at 5% source weight (masked bins), so the FDTD peak sat at the 490 nm mask edge. Analytic pinned via `diag_mie_analytic.py` (direct `Au.epsilon(f)` eval, eps@500nm=−2.978+2.983i; 2D-Mie series at 0.1% vs quasistatic; caught missing i^n phases, 1/k0² norm, (4/k) far-field norm) | Fix: recenter fcen=1/0.52, df=1.0. Job 1146: sweep 522→468→468 nm, FDTD 468 vs analytic 470 → delta −2 nm PASS; valid window 454–596 nm, NaN 47% by design | Closed (1146 GREEN; F5 superseded) |
| F16 | 1069–1138 | Library unwrapped-ptp metric overstated coverage (6.70/9.23 rad) while circular coverage lagged (4.64 rad, gap 1.64 rad); 1131 wrong-direction sweep FAIL; 1133 denser sweep REGRESSED 5.45→5.09 | Unwrapped ptp double-counts winding + non-monotonic resonance branch; sweep direction/branch sampling, not pillar physics. 1133 lesson: fills on the non-monotonic branch add wrapped points without closing the max gap | Dense sweep with correct direction + resonance-branch fills (n=269): 1132 5.45 → 1133 5.09 → 1134 5.92 → 1135 5.92 tail → 1136 6.08 → 1137 6.18 → 1138 6.20 rad, gap 0.088 rad; T≥0.25 keeps 6.20 | Closed (1138 GREEN; F9b superseded) |

## 3. Quick-triage table (symptom → record)

| You see | Check | Record |
|---------|-------|--------|
| `can't open file` at launch | Submit directory (`pwd`) | F1 |
| `c_err ~2.0`, echo ~0 | Absolute vs differential arrival | F2 |
| All-zero T with physical geometry | Sign of `t0`; `max()` on flux | F3b |
| T zeros + PML warnings | Source/monitor vs PML interior | F3a |
| `R+T-1` spikes at band edge only | Resolution column | F4 |
| Mie peak = source center | Normalization + drive polarization | F5 |
| `NaN or Inf` with metals | Epsilon source (inline vs `materials.py`) | F6 |
| Enhancement <0.5x on resonance | `force_complex_fields` + polarization | F7 |
| Absorber A flat ~0.03 | Layer contact (air gaps?) | F8 |
| Library span <4 rad | Height + diameter range | F9a |
| `1 processes` per rank | MPI launch, not physics | F10 |
| 4x size-1 singletons, `mpirun` BYCORE error | `--mpi=pmix` wiring (Job 1090) | F13 |
| Absorber A stuck <0.9 or dips at finer res | Spacer sweep, cell-snapping, runtime control | F14 |
| Mie peak converged but offset ~20 nm from analytic across all knobs | Source center vs mask edge (check peak vs valid window) | F15 |
| Library span grows but circular coverage stalls or regresses | Sweep direction + branch sampling; quote wrapped gap | F16 |
| No lens focus peak | Design f vs cell half-height | F11 |

## 4. Self-check + research bridge

1. Grating T is identically zero. Do you move the monitor first or fix the normalization first, and what distinguishes the two faults?
2. Absorber shows A=0.36 with NaNs at band edges. Numerics or coupling failure, and what is the next knob?
3. Library unwrapped span is 9.23 rad but circular coverage is 6.20 rad. Which metric decides, and why did 16.1° still hit exactly?

Research bridge: every record above is a capstone risk entry. Cite the F-number in the proposal fallback column.

> Tested: 2026-09-17, excerpts from `slurm-1012.out`, `slurm-1021/1022.out`, Jobs 1024-1071 per TEST_STATUS.md 2026-09-17 update, meep/1.28.0.
