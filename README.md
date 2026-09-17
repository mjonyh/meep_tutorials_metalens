# Meta-Optics with MEEP on HPC — From Maxwell to Metalens in 15 Hours

PhD/researcher-level, 100% hands-on, broad sampler: Bragg/grating → photonic crystals → plasmonics/Mie → metasurface/metalens. 5 × 3 h. All simulations run on the cluster; no laptop MEEP.

## 1. Objectives

- O1: Load the pinned toolchain and run parallel PyMeep 1.28.0 via `sbatch`/`srun` on the `compute` partition (`Simulation`, `GaussianSource`, `PML`, `add_flux`, `Harminv`, dispersive `Medium`).
- O2: Extract R/T/A with empty-run normalization, compute bands/waveguide-T/cavity-Q, run stable lossy-metal FDTD, build a phase library → deflector → 2D metalens.
- O3: Apply convergence and HPC discipline: resolution sweeps, PML/runtime controls, energy checks, queue etiquette on a 2-node partition.

## 2. Outcomes — What You Must Show

| # | Artifact | Pass threshold |
|---|----------|----------------|
| E1 | `00_setup` import job + 10+ `sbatch`-ready sims with field maps + spectra | `import meep` 1.28.0 PASS (Job 1013); per-module gates in status table below |
| E2 | One resolution-convergence table | e.g. M1 Fabry-Perot sweep, M4 Mie 522→468→468 nm, M5 library res-20/40 check |
| E3 | Capstone mini-proposal (1 page + 5-min talk) | Graded on convergence evidence + methods clarity, not plot beauty |
| E4 | Scaling table + plot (`01_foundations/expected_figs/scaling.csv`, `speedup.png`) | MEASURED 2026-09-17 — W1@res40 Jobs 1171/1172/1173: 211/181/84 s (n=1/2/4), speedup 1.00/1.17/2.51, eff 100/58/63%; physics bit-identical. Negative exhibit: W1@res20 n=4 (Job 1150) timed out — problem too small to decompose |

## 3. HPC stack (verified, do not substitute)

| Item | Value |
|------|-------|
| Partition | `compute`: 2 nodes, 12 CPU/node, ~63 GB; SLURM 26.05.2 |
| MEEP | 1.28.0, CPU-only MPI + PyMeep; `/opt/hpc/software/meep/1.28.0` |
| Module chain | `gcc/12.4 openmpi/5.0.10 openblas/0.3.34 fftw/3.3.11 hdf5/1.14.6 python/3.11.9 meep/1.28.0` |
| Run pattern | `srun --mpi=pmix -n 4 python3 sim.py` (plain `srun` gives singletons — Job 1090); jobs >2 min go through `sbatch` |
| Budget | ≤25 min on 4 cores per lab (except `14_metalens_2D`, ~23 min, ships `fallback_data/`) |

Full procedure: `SETUP_HPC.md`. Schedule and exit tickets: `COURSE_SYLLABUS.md`.

## 4. Repo layout

```text
00_setup/ 01_foundations/ 02_sparams/ 03_phc/ 04_plasmonics/ 05_metalens/
  sim_*.py | *.sbatch | lesson.md | expected_figs/ | solutions/ | fallback_data/ (05 only)
common/ plot_utils.py materials.py slurm_header.snippet
capstone/ briefs.md rubric.md proposal_template.md
instructor/ timing.md troubleshooting.md grading_exit_tickets.md
README.md COURSE_SYLLABUS.md SETUP_HPC.md MASTER_PLAN.md AGENTS.md TEST_STATUS.md
```

Scratch, queue logs, HDF5 dumps: `/tmp/opencode/`, never committed. Never commit `slurm-*.out`, `*.h5`, `__pycache__`, venv paths, tokens, `.env`.

## 5. Module status + gates (honest, 2026-09-17)

| Module | Lesson | Status | Gate evidence (JobID) |
|--------|--------|--------|-----------------------|
| 00 setup / import | `00_setup/lesson.md` | GREEN | Job 1013: `import meep` 1.28.0 PASS 4/4 ranks, <1 s/rank. Historical MPI caveat (4x singletons) fixed 2026-09-17 via `--mpi=pmix` |
| M1 FDTD + Fabry-Perot | `01_foundations/lesson.md` | GREEN | Job 1022: c_err=0.0011 (≤0.02), echo=0.0 (<0.01). Job 1023: max\|R+T-1\|=0.000 (≤0.02) |
| M2 Bragg / grating / eff-medium | `02_sparams/lesson.md` | MARGINAL | Jobs 1024/1028/1026: Bragg peak R=1.003 (>0.95); median \|R+T-1\|=0.0037 PASS but 10/80 pts deviate to 0.096 at band-edge/short-λ; grating T=0.51–0.63; eff-medium collapse at λ/5 |
| M3 bands / W1 / L3 cavity | `03_phc/lesson.md` | MARGINAL | Job 1030: gap bands 3–4 = 0.5698–0.5785 (1.5% mini-gap, NOT main TM gap — ±5% lit gate not claimed). Job 1031: W1 suppression ~40 dB (>10 dB PASS). Jobs 1033/1034: f=0.3076, Q=97.4, Harminv converges PASS |
| M4 Mie / slit / absorber | `04_plasmonics/lesson.md` | GREEN | Mie Job 1146: 522→468→468 nm, analytic 470 nm, delta −2 nm PASS. Slit Job 1043: enhancement ~1.3x max, marginal. Absorber Job 1102: best A=0.902 at spacer=15nm/w=0.20 (gate >0.90 PASS, margin thin; 33.8% band-edge NaN by design) |
| M5 library / deflector / metalens | `05_metalens/lesson.md` | GREEN | Job 1138: circular 6.20 rad (gap 0.088 rad, n=269 dense sweep; unwrapped ptp 9.23 NOT the metric). Job 1070: 16.1°=16.1° (±3° PASS), eff 0.87, ~12 min. Job 1071: focus y=5.80 (design 6.0), FWHM=0.625 vs λ/2NA=0.904, eff=0.420, ~23 min |

Detail: `TEST_STATUS.md` (2026-09-17 update). Physics gates: `MASTER_PLAN.md` §7, `AGENTS.md` §7.

## 6. Quickstart

```bash
cd /home/mjonyh/meep_tutorial/00_setup
source load_meep.sh        # module purge + load chain; check python3 -> .../1.28.0/venv/bin/python3
bash env_check.sh          # FOUND lines for binary, venv python, site-packages; sinfo compute
python3 -m py_compile test_meep.py && echo COMPILE_OK
sbatch --test-only scaling_template.sbatch
sbatch scaling_template.sbatch   # verified pattern: Job 1013 PASS
squeue -u $USER
cat slurm-<jobid>.out      # expect 4x "meep version: 1.28.0" + 4x PASS
```

Next: `01_foundations/lesson.md` (Jobs 1022/1023 commands), then M2→M5 in order. One `.sbatch` per simulation; stagger launches (2-node limit); never `--exclusive`.

## 7. Self-check + research bridge

1. Which two modules are MARGINAL and what single caveat blocks each from GREEN?
2. The absorber gate passes at A=0.902 with a thin margin — what two evidence items in the lesson keep that claim honest?
3. Plain `srun -n 4` shows 4x size-1. Which JobID proved the `--mpi=pmix` fix with real Meep?

Research bridge: this stack is the reusable forward-solver baseline. M5 ends at gradient-design entry (`meep.adjoint`, Bayesian loops, MPB cross-check); the capstone ties one module to the student's own research question with convergence evidence.

> Tested: 2026-09-17, `sbatch scaling_template.sbatch`, JobID 1013, meep/1.28.0, 4 tasks, ~1 min walltime, outputs in `00_setup/expected_figs/`. Module JobIDs: 1022/1023 (M1), 1024/1028/1026 (M2), 1030/1031/1034 (M3), 1146/1043/1102 (M4; +diag_mie_analytic), 1138/1070/1071 (M5). MPI fix Job 1090, header rollout Jobs 1103–1117 (--test-only). Scaling: W1@res40 Jobs 1171/1172/1173 (211/181/84 s, speedup 1.00/1.17/2.51); res20 n=4 negative exhibit Job 1150 (timeout). Clean-dir re-run Job 1175 (vacuum.csv/png byte-identical). Lens fallback: `05_metalens/fallback_data/` (Job 1071). Raw queue logs + HDF5 archived to `/tmp/opencode/repo_archive_2026-09-17/`. Full log: `TEST_STATUS.md`.

Update 2026-09-17: launcher fixed to `srun --mpi=pmix -n 4` (diag Job 1090: plain srun → 4× size-1 singletons, pmix → world size 4; proven with Meep '4 processes' Jobs 1092+. mpirun rejected — BYCORE binding error). Canonical header + all 14 sim sbatches rolled out (Jobs 1103–1117 --test-only PASS). Quoted JobIDs ran serially (deterministic — physics stands).
