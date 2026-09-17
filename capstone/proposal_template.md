# Capstone Proposal Template — meep_tutorial (1 page)

## 1. Objectives

- O1: Force a falsifiable plan before queue time is spent.
- O2: Bind every claim to a convergence check, a walltime budget, and a fallback.

## 2. Outcomes — Fill every field; proposals with blank fields are returned ungraded

Copy from `---` to `---`. Keep to 1 page (~450 words + 1 table).

---

Title:
Author / pair:
Brief choice: (a) BIC grating / (b) sensing absorber / (c) extended NA study
Prerequisite lab + JobID reproduced:

1. Research question (1-2 sentences, falsifiable):

2. Method (geometry, materials, APIs):

- Geometry (periods, thicknesses, sweep parameter + range + step):
- Materials (from `common/materials.py`, no inline epsilons):
- MEEP APIs (`add_flux`, `Harminv`, `get_field_point`, `force_complex_fields`, `k_point` as applicable):
- Normalization + controls (empty run, bare backplane / bare substrate, sign-safe formula):

3. Numeric gate (PASS/FAIL threshold + verdict rule):

- Gate:
- Energy/conservation check:
- What counts as FAIL (write before running):

4. Convergence plan (table):

| Sweep | Points | Resolutions | Cost per run (tasks x walltime) | Total queue budget |
|-------|--------|-------------|---------------------------------|--------------------|
| Param | | | | |
| Res | | | | |

5. Resources (commands):

```bash
module purge
module load gcc/12.4 openmpi/5.0.10 openblas/0.3.34 fftw/3.3.11 hdf5/1.14.6 python/3.11.9 meep/1.28.0
sbatch <your>.sbatch
```

Expected outputs (CSV/PNG names):

6. Risks + fallback (at least 2):

| Risk | Signal in `slurm-*.out`/CSV | Fallback |
|------|------------------------------|----------|
| | | |
| | | |

7. Lightning-talk figure sketch (1 figure, axes + units + what the gate looks like on it):

---

## 3. Example (filled gate lines, do not copy blindly)

- (a): Q vs `delta` over 5 asymmetries; gate: fit exponent of Q(`delta`) with uncertainty; convergence: res 30/40/60 at smallest `delta`.
- (b): width 0.05-0.38 um + spacer 20-60 nm; gate: A>0.90 then S (nm/RIU) + FWHM + FOM; control: w=0 gives A~0.
- (c): >=3 NA points; gate: FWHM vs lambda/2NA + efficiency with estimator/normalization stated; fallback: `expected_figs/` if queue >30 min.

> Tested: 2026-09-17, template fields map to `rubric.md` G1-G5. No new code in this file.
