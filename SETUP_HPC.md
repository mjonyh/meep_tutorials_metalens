# SETUP_HPC — Modules, SLURM, PyMeep Import on `compute`

Do this before any lab. All commands run from `00_setup/`. Do not submit from the repo root (Job 1012 lesson).

## 1. Objectives

- O1: Load the pinned toolchain (`gcc/12.4 openmpi/5.0.10 openblas/0.3.34 fftw/3.3.11 hdf5/1.14.6 python/3.11.9 meep/1.28.0`) and verify `python3` resolves to the PyMeep venv.
- O2: Run `import meep` via `srun`/`sbatch` on `compute` and confirm version 1.28.0 on every rank.
- O3: Submit and diagnose a batch job (`sbatch`, `squeue`, `slurm-%j.out/.err`); distinguish scheduler failure from code failure.
- O4: Detect the broken MPI decomposition: interpret `Using MPI version 3.1, 1 processes` per rank and flag the CO1 scaling study as invalid until fixed.

## 2. Outcomes — What You Must Show

| # | Artifact | Pass threshold |
|---|----------|----------------|
| E1 | `slurm-1013.out`: `PASS: import meep 1.28.x OK` on all 4 ranks | `meep version: 1.28.0`, 4/4 ranks PASS |
| E2 | `slurm-1013.out` timing lines | Per-rank elapsed <1 s (measured 0.0002 s); scheduler walltime ~1 min |
| E3 | Debug record: Job 1012 failure mode identified | Root cause: submitted from repo root, `test_meep.py` not found |
| E4 | MPI status call | Verdict recorded: 4x `1 processes` = 4 serial replicas; no parallel speedup claimable (fixed 2026-09-17 via `--mpi=pmix` — see note below; archived logs stay as detection exercise) |

## 3. Copy-pasteable procedure

Step 0 — load environment (every shell, every lesson):

```bash
module purge
module load gcc/12.4 openmpi/5.0.10 openblas/0.3.34 fftw/3.3.11 hdf5/1.14.6 python/3.11.9 meep/1.28.0
# or: source load_meep.sh
module list
which python3   # expect /opt/hpc/software/meep/1.28.0/venv/bin/python3
```

Step 1 — environment check:

```bash
cd /home/mjonyh/meep_tutorial/00_setup
bash env_check.sh
# expect: FOUND .../bin/meep, FOUND .../venv/bin/python, FOUND .../venv/lib/python3.11/site-packages
# expect: sinfo shows compute partition
```

Step 2 — import test (direct, short only):

```bash
python3 -m py_compile test_meep.py && echo COMPILE_OK
srun -n 1 python3 test_meep.py
# expect: "meep version: 1.28.0" + "PASS: import meep 1.28.x OK"
```

Step 3 — batch submit (canonical header, Job 1013 pattern):

```bash
sbatch --test-only scaling_template.sbatch
sbatch scaling_template.sbatch
squeue -u $USER
cat slurm-<jobid>.out
cat slurm-<jobid>.err   # expect empty
```

Reference `scaling_template.sbatch` (do not modify for this lesson):

```bash
#!/bin/bash
#SBATCH --partition=compute
#SBATCH --nodes=1 --ntasks=4 --cpus-per-task=1
#SBATCH --time=00:15:00 --job-name=meep-setup-test
#SBATCH --output=slurm-%j.out --error=slurm-%j.err
module purge
module load gcc/12.4 openmpi/5.0.10 openblas/0.3.34 fftw/3.3.11 hdf5/1.14.6 python/3.11.9 meep/1.28.0
srun --mpi=pmix -n 4 python3 test_meep.py
```

Verified output (`slurm-1013.out`, archived plain-`srun` record, 4 identical blocks, one per rank):

```text
Using MPI version 3.1, 1 processes
meep version: 1.28.0
PASS: import meep 1.28.x OK

 Elapsed run time = 0.0002 s
```

Reruns with the current `--mpi=pmix` template print `4 processes` instead of `1 processes` (fixed behavior, Job 1090); the 4x PASS lines are the gate. Raw Job-1013 log archived to `/tmp/opencode/repo_archive_2026-09-17/00_setup/`; transcript also in `expected_figs/import_test.txt`.

## 4. Queue etiquette (`compute`: 2 nodes, 12 CPU/node)

- One node, 4 tasks (`--nodes=1 --ntasks=4 --cpus-per-task=1`); `00:15:00` is sufficient here (~1 min measured).
- Jobs >2 min go through `sbatch`. No bare `mpirun` on the login node.
- Never `--exclusive`; never whole-node requests for 2D labs. Stagger launches (2-node limit).
- Lab budget: ≤25 min on 4 cores (except `14_metalens_2D`, ~23 min, `01:00:00` limit + `fallback_data/`).

## 5. Troubleshooting

| Symptom | Cause | Fix / status |
|---------|-------|--------------|
| Job 1012: `test_meep.py not found` | Submitted from repo root; relative path does not resolve | `cd 00_setup/` and resubmit |
| `FAIL: cannot import meep: No module named 'meep'` (cf. Job 1004) | Stale `PYTHONPATH` / missing bindings (install fault, not code) | Re-check `env_check.sh` FOUND lines; escalate to operator, do not edit sim code |
| Every rank prints `1 processes` | 4 independent serial instances; no domain decomposition | OPEN — do not quote speedup; CO1 scaling study invalid until launch is fixed |
| `slurm-<job>.err` non-empty / PASS on rank 0 only | Environment fault (module/paths), not physics | Check `module list`, `which python3`, resubmit from `00_setup/` |

Full log: `instructor/troubleshooting.md`. Honest gate log: `TEST_STATUS.md`.

## 6. Self-check + research bridge

1. Why must `sbatch scaling_template.sbatch` run from `00_setup/` and not the repo root?
2. `slurm-1013.out` shows 4 PASS lines. Why does this still fail the CO1 scaling gate?
3. Next job prints PASS on rank 0 but `ModuleNotFoundError` on ranks 1–3. Environment or code fault? What do you check first?

Research bridge: a green import test separates environment faults from physics faults for every later gate (vacuum `c±2%`, `R+T+A=1±0.02`, W1 >10 dB, Mie ±10 nm, deflector ±3°). The MPI finding propagates: until ranks share one decomposition, `-n 1/2/4` timing measures launch overhead, not FDTD scaling.

> Tested: 2026-09-16, `sbatch scaling_template.sbatch`, JobID 1013, meep/1.28.0, 4 tasks, ~1 min walltime, outputs in `expected_figs/`. Job 1012 kept as debug record (wrong submit directory).

Update 2026-09-17: launcher fixed to `srun --mpi=pmix -n 4` (diag Job 1090: plain srun → 4× size-1 singletons, pmix → world size 4; proven with Meep '4 processes' Jobs 1092+. mpirun rejected — BYCORE binding error). Canonical header + all 14 sim sbatches rolled out (Jobs 1103–1117 --test-only PASS). Quoted JobIDs ran serially (deterministic — physics stands).
