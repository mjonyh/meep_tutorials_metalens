# Capstone Rubric — meep_tutorial

## 1. Objectives

- O1: Grade convergence evidence and methods clarity, not plot beauty (MASTER_PLAN.md §5, Module 5).
- O2: Give students deterministic pass/fail criteria before they run.
- O3: Keep grading runnable from CSV + `slurm-*.out` without re-running jobs.

## 2. Outcomes — Grading table

Total 100 pts. Pass >=60. Distinction >=85.

| # | Criterion | Weight | Excellent (full) | Adequate (half) | Fail (0) |
|---|-----------|--------|------------------|-----------------|----------|
| G1 | Convergence evidence | 30 | Resolution table (>=2 res) + parameter sweep (>=5 pts); deltas quoted; conclusion states what is/is not converged | One sweep only, or deltas stated without numbers | Single run, no sweep; peak quoted as physics |
| G2 | Methods clarity / reproducibility | 25 | Full `module load` chain, `sbatch` command, JobID(s), resolution, cell/PML/runtime, normalization formula, CSV headers with `meep.__version__` | Most present; one load-bearing item missing (e.g. no normalization statement) | Commands not reproducible; version/resolution unstated |
| G3 | Correct gate + honest verdict | 20 | Numeric gate stated upfront; verdict PASS/FAIL/MARGINAL matches data; RED states kept and explained (cf. absorber A=0.361 vs >0.90) | Gate stated but verdict softened; caveats buried | No numeric gate;FAIL relabeled as pass; failures deleted |
| G4 | Physics interpretation | 15 | Result tied to mechanism (Q scaling, critical coupling, NA/diffraction limit); control experiment named (bare backplane, empty run, monotonic-branch check) | Mechanism named, no control | Numbers without mechanism |
| G5 | Talk + proposal quality | 10 | 1-page template complete; 5-min talk within time; figures labeled (axes, units, resolution, cores/walltime) | Template complete; figures missing labels or walltime | No proposal; plots unlabeled |

Deductions:

| Violation | Deduction |
|-----------|-----------|
| Inline metal epsilon instead of `common/materials.py` | -10 |
| `max(flux,eps)` signed-flux pattern (Jobs 1025/1027 bug) | -10 |
| Real-field CW amplitude without `force_complex_fields` (Job 1039 bug) | -10 |
| Claiming speedup from 4x-serial MPI state (`1 processes` per rank) | -10 |
| Quoting unwrapped phase span without circular-gap metric (1065/1069) | -5 |
| Deleting or hiding a failed run | -15 |
| Committing `slurm-*.out`, `*.h5`, tokens, `.env` | -10 |

## 3. Pass thresholds per brief

| Brief | Minimum for Pass (>=60) |
|-------|------------------------|
| (a) BIC grating | Q-vs-`delta` table (>=5 pts) + resolution column at smallest `delta` + `R+T+A` check |
| (b) Sensing absorber | GREEN baseline reproduced (Job 1102 config) + w=0 control; sensing fit graded with R^2 + FWHM; thin-margin caveat quoted |
| (c) NA study | >=3 NA points with FWHM vs lambda/2NA + efficiency, estimator/normalization stated + res column at one NA |

## 4. Self-check + research bridge

1. What earns full G1 vs half G1?
2. Your best number fails its gate. What do you write to keep G3 full marks?
3. Which deduction applies to `T = t/max(t0,eps)` on signed fluxes?

Research bridge: this rubric is a methods-section checklist. A proposal scoring >=85 here has the convergence table, controls, and honest failure log a reviewer expects.

> Tested: 2026-09-17, rubric gates align with TEST_STATUS.md 2026-09-17 update. No new code in this file.
