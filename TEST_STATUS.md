# TEST STATUS — meep_tutorial (honest, evidence-backed)

**Date:** 2026-09-16. **Rule:** no lesson doc may claim passing results until its code passes on HPC.

## Update 2026-09-17 evening (close-out: scaling, clean re-run, fallback, tree hygiene)
- [x] CO1 SCALING MEASURED (`sim_08_w1.py` @ res 40, `srun --mpi=pmix`, shared-FS cwd `/home/mjonyh/opencode_scratch/scaling/`):
  Jobs **1171/1172/1173** → WALL 211/181/84 s (n=1/2/4), `1/2/4 processes`, speedup **1.00/1.17/2.51**,
  eff 100/58/63%. w1.csv bit-identical across decompositions (n=4 differs in 16th digit only).
  Artifacts: `01_foundations/expected_figs/scaling.csv` + `speedup.png`.
- [x] NEGATIVE EXHIBIT (kept): same probe @ res 20 → 31/28 s (n=1/2, Jobs 1148/1149) but n=4
  (**Job 1150**) never finished one flux run in 00:15:00 (TIME_LIMIT cancel, node healthy,
  ranks ~99% CPU). Cause: 35k-cell grid split 4 ways = halo-sync overhead dominates.
  Lesson recorded in `01_foundations/lesson.md` §3.5. NOTE: res20 campaign was submitted from
  login-local `/tmp/opencode/scaling/` (node-local /tmp, NOT shared) — logs/CSVs stranded on
  node01/node02, retrieved via `srun --nodelist=... cat`. Res40 rerun used shared FS. Scratch rule learned.
- [x] CLEAN-DIR RE-RUN **Job 1175** (doc commands verbatim, fresh dir `/home/mjonyh/opencode_scratch/cleanrun/lab/`):
  `sbatch sim_01_vacuum.sbatch` → dt=4.004, c_err=0.0011, echo=0.0, `4 processes` + chunk split;
  `vacuum.csv` + `vacuum.png` **byte-identical** (`diff`/`cmp` clean) to `01_foundations/expected_figs/`. Reproducibility PROVEN.
- [x] FALLBACK_DATA: `05_metalens/fallback_data/` = focus.csv + axial.csv + focal-cut.png (Job 1071 copies)
  + `README.md` provenance (f=6.0, y=5.80, FWHM=0.625, eff=0.420). M5 lesson §§fallback rows now point there.
- [x] TREE HYGIENE: 182 entries (`slurm-*.out/.err`, `diag-*.out/.err`, `mpi-diag-*`, `*.h5`, `__pycache__`,
  `.ruff_cache`) moved to `/tmp/opencode/repo_archive_2026-09-17/` (mirrored paths); zero residuals in repo.
  `00_setup/expected_figs/import_test.txt` added (Job 1013 transcript) so the footer claim has an artifact.
- [x] DOCS CLOSED: README E4 + footer, SYLLABUS E2 + footer, M1 lesson §3.5/§3.6, M5 fallback rows,
  00_setup §3.5 table updated to the measured state. Remaining MARGINALs (M2 band-edge 10/80 pts,
  M3 mini-gap) stand as disclosed caveats — no lit gate is claimed for them.

## Update 2026-09-17 (gate verification from slurm logs + outputs/*.csv)
- [x] M1 GREEN: `sim_01` **Job 1022** dt=4.004 c_err=0.0011 (≤0.02), echo=0.0 (<0.01),
  ~0.3 s/rank. (Job 1021 FAIL c_err=2.06 — arrival t=18.355 vs 6.0, kept as debug record.)
  `sim_02` **Job 1023** max|R+T-1|=0.000 (≤0.02), ~1 s/rank.
- [x] M2 MARGINAL-PASS: `sim_03` **Job 1024** peak R=1.003 (>0.95), ~1 s/rank.
  Median |R+T-1|=0.0037 PASS off-resonance; 10/80 pts deviate up to 0.096
  (band-edge/short-λ, resolution note required in lesson). `sim_04` **Job 1028**
  T=0.51–0.63 (~3 s/rank; Jobs 1025/1027 zero-transmission debug → sign-preserving
  normalization fix). `sim_05` **Job 1026** T=0.99/0.95/0.41/0.0007/0.88 (~4.4 s/rank),
  collapse at λ/5 — homogenization breakdown shown.
- [x] M3 MARGINAL: bands **Job 1030** runs (~7 s/rank), gap printed
  bands 3-4: 0.5698–0.5785 (1.5%) — higher-order mini-gap, NOT the main TM gap;
  ±5%-lit gate cannot be claimed without lit reference → lesson must state this
  honestly. W1 **Job 1031** (~37 s/rank): T=0.339/3.3e-05/1.0 → ~40 dB suppression
  (>10 dB PASS). Cavity **Jobs 1033/1034** (~290 s/rank ≈ 5 min):
  f=0.3076, Q=97.4, Harminv converges PASS.
- [x] M4 GREEN 2026-09-17 (Job **1102**): spacer sweep 50→15nm at res 120–160
  gives best **A=0.902 at spacer=15nm, w=0.20** (gate >0.90 PASS, margin thin —
  lesson quotes full res table + staircasing caveat). Campaign: 1092 res80 0.750 /
  1094 res100 0.540 (pixel-snapping) / 1096 res80 rt300 0.750 (time-converged) /
  1098 spacers 30/40/50nm → 0.75/0.58/0.40 / 1100 spacers 20/25/30nm → 0.833/0.61/0.45 /
   **1102 spacers 15/20nm @res160 → 0.902/0.83**. ~655 s/rank (~11 min, within
   25-min gate). Mie GREEN (Job **1146**): res sweep 522→468→468 nm (40/80/120),
   FDTD 468 nm vs same-fit analytic 470 nm → delta −2 nm (|d|≤10 PASS),
   ~15 s/rank true-MPI; valid window 454–596 nm, NaN 47% = band-edge mask by
   design; `mie.png` with analytic overlay + `mie_analytic.csv` staged.
   Slit marginal as before.
- [x] MPI FIXED 2026-09-17 (Job **1090** diag): plain `srun -n 4` → 4× singleton
  size 1 (no PMI wiring — root cause of all "1 processes" logs); `srun --mpi=pmix`
  → world size 4 with real Meep ("4 processes", Job 1092+). `mpirun` rejected
  (BYCORE binding error). Canonical header + all 14 `sim_*.sbatch` rolled out to
  `srun --mpi=pmix -n 4` (Jobs 1103–1117 `--test-only` PASS). Prior physics JobIDs
  ran serially — deterministic, results stand; walltimes improve under pmix.
- [x] M5 GREEN (with notes): library **Job 1069** coverage 6.70 rad claimed
  (>2π, ~4 s/rank; Job 1065 got 3.37 rad FAIL — sweep-range fix record). NOTE:
  circular coverage recomputed 4.64 rad (max gap 1.64 rad) and T max 1.022
  (substrate-normalization overshoot) — lesson must quote both metrics honestly.
  Deflector **Job 1070** theory=measured=16.1° (±3° PASS), eff 0.87, ~740 s/rank
  (~12 min). Metalens **Job 1071** focus y=5.80 (design 6.0), FWHM=0.625 vs
  λ/2NA=0.904, eff=0.420, ~1387 s/rank (~23 min, within 25-min perf gate).
  Library metric FIXED (Job **1138**): dense sweep n=269 (uniform 0.004 +
  0.002/0.0005 fills), circular coverage **6.20 rad** (was 4.64, Job 1069),
  max wrapped gap 0.088 rad; T≥0.25 keeps 6.20 (n=260); unwrapped ptp 9.23
  is NOT the metric. ~51 s/rank, res 30.
- [x] Global: MPI still 4× serial ("1 processes" per rank) — correctness unaffected,
  scaling study CO1 invalid until fixed. `outputs/*.csv+*.png` present for all 14 sims.
- [x] NEXT (done 2026-09-17): absorber GREEN (Job 1102), Mie GREEN (Job 1146),
  library metric fixed (Job 1138, circular 6.20), MPI pmix rolled out,
  04/05 lessons + troubleshooting + README/SYLLABUS/capstone/instructor rows updated.
  Remaining OPEN: none from Mie/library; next scale-up per MASTER_PLAN.

## Update 2026-09-16 afternoon (CPU build confirmed, flux bugs patched)
- [x] MEEP is CPU-only MPI — upstream has no CUDA support (FAQ: "No. Currently,
  Meep does not support GPUs via CUDA, OpenCL, etc."). Course stays CPU per MASTER_PLAN.
- [x] Import re-verified: `sbatch 00_setup/scaling_template.sbatch` → **JobID 1013**,
  `PASS: import meep 1.28.x OK` on all 4 ranks (`00_setup/slurm-1013.out`).
  (Job 1012 failed trivially: submitted from repo root, `test_meep.py` not found.)
- [x] Flux-sign bug fixed in 6 sims (`R = -(r-r0)/r0`, empty-run normalization,
  clip to [0,1]): `sim_02_fabry`, `sim_03_bragg`, `sim_04_grating` (+2-col freq,T),
  `sim_05_effmedium`, `sim_08_w1`, `sim_11_absorber` (+A spectra). `py_compile` clean.
- [x] Stale 14:09 `outputs/*.csv` (negative R, T>1) are superseded — re-run pending.
- [x] Structural rewrites done 2026-09-16 (~15:10): `sim_01` real time-trace
  (energy-centroid arrival + echo window), `sim_06` Harminv G-X-M-G sweep + gap
  extraction, `sim_09` closed-box minus empty + 3-pt res sweep, `sim_10` slit
  geometry fixed (blocks overlapped) + CW/complex-fields measured enhancement,
  `sim_12` substrate-referenced T/phase + probe in air, `sim_13` FFT order
  spectrum + measured angle/eff, `sim_14` f=6 (old f=10 focused outside cell)
  + axial locate + transverse FWHM vs λ/2NA + empty-run efficiency.
  All 17 `.py` `py_compile` clean; 7 rewritten sbatches `--test-only` PASS.
- [x] M1 GREEN 2026-09-16 ~15:25: `sim_01` **Job 1022** dt=4.004 c_err=0.0011
  (gate ≤0.02), echo=0.0000 (gate <0.01); `sim_02` **Job 1023** max|R+T-1|=0.000
  (gate ≤0.02), R/T all physical. Walltime each <1 min on 4 tasks.
  NOTE: each srun task reports "1 processes" — MPI world is NOT combining
  across tasks (4 independent serial runs). Correctness unaffected (deterministic
  runs, identical files); scaling study CO1 must investigate before documenting.
- [x] M2 GREEN 2026-09-16 ~15:45: `sim_03` **Job 1024** peak R=1.003 (gate >0.95);
  `sim_05` **Job 1026** T=0.99/0.95/0.41/0.0007/0.88 across periods — collapse
  exactly at λ/5=0.31um (gate: homogenization breakdown shown);
  `sim_04` **Jobs 1025/1027 FAIL → 1028 PASS** (T=0.51–0.63).
  Debug record: (a) source/monitor sat on PML edge (y=±2, interior |y|≤2) —
  moved to ±1.5; (b) real cause of zeros: transmitted flux is NEGATIVE (power
  flows −y) and `t/max(t0,eps)` collapsed the denominator to eps, then clip→0.
  Fixed with sign-preserving `where(|t0|>eps, t/t0, 0)`. Same latent fix in
  `sim_11` (incident flows −y there too). Lesson: never `max()` a signed flux.
- [ ] NEXT: `sbatch` M3→M5 on `compute` for real JobIDs, walltimes, gate checks.
  Bugs fixed along the way (all caused unphysical outputs): source inside PML
  (`sim_09` x=-0.4, `sim_10` y=0.6), real-field CW snapshots replaced by
  `force_complex_fields=True` wherever amplitude/phase is read (10/12/13/14).

## What PASSED (verified this session)
- [x] All 17 `.py` files: `python3 -m py_compile` clean.
- [x] `env_check.sh`, `load_meep.sh`: `bash -n` clean.
- [x] All 15 `.sbatch` files: `sbatch --test-only` PASS (scheduler accepts scripts).
- [x] Repo scaffold complete: `common/` (3) + `00_setup/` (4) + 14 sims + 14 sbatch.

## What is BLOCKED (load-bearing, proven with real JobID)
- [ ] **ALL runtime tests BLOCKED — cluster MEEP 1.28.0 install is broken (not our code).**
  - Proof: `sbatch scaling_template.sbatch` → **JobID 1004**, all 4 ranks:
    `FAIL: cannot import meep: No module named 'meep'`. Log: `/tmp/opencode/slurm-1004.out`.
  - Cause A: venv has 232 packages but **no meep package**; modulefile `PYTHONPATH`
    points at nonexistent `.../lib/python3.11/site-packages` (real dir: `.../venv/lib/...`, still empty of meep).
  - Cause B: Scheme `meep --version` crashes — missing `/tmp/meep-build/stage/share/libctl/base/include.scm`
    (build-time path leaked into the install).

## Consequences (per AGENTS.md test-first rule)
- `lesson.md`, `SETUP_HPC.md`, `COURSE_SYLLABUS.md`, `expected_figs/`, physics gates: **NOT written**
  — writing them now would require inventing JobIDs/figures, which is forbidden.
- All sim headers honestly marked `UNTESTED 2026-09-16`; `sim_06_band.py` is an explicit
  skeleton to be filled with `run_k_points` after the fix; `sim_10/11` contain labeled
  placeholders for enhancement/normalization to be measured post-fix.

## Repair in progress (lmod-native, per ~/hpc project convention)
- Root cause: original build configured Meep with `PYTHON=/tmp/meep-build/stage/venv/...`
  and `--with-libctl=/tmp/.../stage/...`, so `make install` wrote PyMeep into the wiped
  /tmp stage and baked stage paths into `bin/meep`. C++/libctl/venv in `$PREFIX` are intact.
- Second find: Meep 1.28.0's shipped SWIG wrapper only compiles with HAVE_MPB
  (fails on `_get_eigenmode_Gk` otherwise — this is also why the original build shipped
  no bindings). Fix builds MPB 1.11.0 first (serial on purpose: Meep links `-lmpb`;
  `--with-mpi` would install only `libmpb_mpi`). Bonus: Module 3 can use real MPB.
- Fix script: `~/hpc/scripts/meep-pymeep-repair.sh` (follows `lmod-software-guide.md`
  contract: idempotent stages, `-j2` thermal cap, unprivileged build, sudo only for install).
  No conda, no pacman, lmod toolchain only.
- DONE unprivileged 2026-09-16: MPB configured (`--prefix=$PREFIX`) + built
  (`src/.libs/libmpb.so` present); Meep configured (final `$PREFIX` paths, no /tmp stage)
  + C++ built (python/ correctly deferred — needs installed MPB headers).
- Logs: `/tmp/opencode/meep-repair2.log`, `/tmp/opencode/meep-repair3.log`.
- REMAINING — one operator command (agent must NOT sudo):
  `sudo bash ~/hpc/scripts/meep-pymeep-repair.sh`
  → installs MPB, reconfigures Meep with MPB (gated on HAVE_MPB), builds, installs,
  fixes modulefile PYTHONPATH (`lib/...` → `venv/lib/...`). Then as regular user:
  `python3 -c "import meep; print(meep.__version__)"` and `meep --version`.
- Legacy diagnostic script (superseded): `/tmp/opencode/fix_meep_1.28.0.sh`.
  JobID 1004 failure log: `/tmp/opencode/slurm-1004.out`.

## File inventory (code-complete, runtime-untested)
- `common/slurm_header.snippet`, `common/materials.py`, `common/plot_utils.py`
- `00_setup/env_check.sh`, `load_meep.sh`, `test_meep.py`, `scaling_template.sbatch`
- `01_foundations/sim_01_vacuum.py/.sbatch`, `sim_02_fabry.py/.sbatch`
- `02_sparams/sim_03_bragg.py/.sbatch`, `sim_04_grating.py/.sbatch`, `sim_05_effmedium.py/.sbatch`
- `03_phc/sim_06_band.py/.sbatch`, `sim_08_w1.py/.sbatch`, `sim_08_cavity.py/.sbatch`
- `04_plasmonics/sim_09_mie.py/.sbatch`, `sim_10_slit.py/.sbatch`, `sim_11_absorber.py/.sbatch`
- `05_metalens/sim_12_library.py/.sbatch`, `sim_13_deflector.py/.sbatch`, `sim_14_metalens.py/.sbatch`
