# 00_setup — Modules, SLURM, PyMeep import

## 1. Objectives

- O1: Load the pinned toolchain (`gcc/12.4 openmpi/5.0.10 openblas/0.3.34 fftw/3.3.11 hdf5/1.14.6 python/3.11.9 meep/1.28.0`) and verify `python3` resolves to the PyMeep venv.
- O2: Run `import meep` (`mp.__version__`) via `srun`/`sbatch` on the `compute` partition and confirm version `1.28.0` on every rank.
- O3: Submit and diagnose a SLURM batch job (`sbatch`, `squeue`, `slurm-%j.out/.err`); distinguish scheduler failure from code failure.
- O4: Detect broken MPI domain decomposition: interpret `Using MPI version 3.1, 1 processes` per rank and flag the CO1 scaling study as invalid until fixed.

## 2. Outcomes — What You Must Show

| # | Artifact | Pass threshold |
|---|----------|----------------|
| E1 | `slurm-1013.out`: `PASS: import meep 1.28.x OK` on all 4 ranks | `meep version: 1.28.0`, 4/4 ranks PASS |
| E2 | `slurm-1013.out` timing lines | Per-rank `Elapsed run time < 1 s` (measured `0.0002 s`) |
| E3 | Debug record: Job 1012 failure mode identified | Root cause stated: submitted from repo root, `test_meep.py` not found |
| E4 | MPI status call | Honest verdict recorded: 4x `1 processes` = 4 serial replicas, no parallel speedup claimable (CO1 scaling invalid; fixed 2026-09-17 via `--mpi=pmix` — see note below, archived logs stay as detection exercise) |

## 3. Body

### 3.1 Theory bite

`test_meep.py` does one thing: `import meep as mp`, print `mp.__version__`, assert `1.28.x`. No `Simulation`, no Yee grid, no PML. Purpose: separate environment faults (module chain, `PYTHONPATH`, working directory) from physics faults before any FDTD runs. SLURM runs 4 independent tasks (`--ntasks=4`); a correct MPI-MEEP build would report N processes cooperating on one decomposition. This run does not (see §3.5).

### 3.2 Commands (copy-pasteable)

All commands run from `00_setup/`. Do not submit from the repo root — `test_meep.py` resolves relative to the submit directory (Job 1012 lesson).

```bash
source ../00_setup/load_meep.sh
# expected: module list shows gcc/12.4 openmpi/5.0.10 openblas/0.3.34 fftw/3.3.11 hdf5/1.14.6 python/3.11.9 meep/1.28.0
# expected: which python3 -> /opt/hpc/software/meep/1.28.0/venv/bin/python3
```

```bash
bash env_check.sh
# expected: FOUND for meep binary, venv python, site-packages; sinfo shows compute partition
```

```bash
python3 -m py_compile test_meep.py && echo COMPILE_OK
sbatch --test-only scaling_template.sbatch
sbatch scaling_template.sbatch
squeue -u $USER
cat slurm-1013.out
```

Reference `scaling_template.sbatch` (canonical header, do not modify for this lesson):

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

`slurm-1013.err` is empty. Scheduler walltime ~1 min (per-rank elapsed <1 s + queue/launch overhead). Reruns with the current `--mpi=pmix` template print `4 processes` instead of `1 processes` — that is the fixed behavior (Job 1090); the 4x PASS lines are the gate.

### 3.3 Guided task (10 min)

1. `cd 00_setup/`. Run the command block in §3.2 in order.
2. Confirm `slurm-<jobid>.out` contains 4x `meep version: 1.28.0` and 4x `PASS`.
3. Confirm `slurm-<jobid>.err` is empty.

### 3.4 Stretch task (10 min)

1. Run `srun -n 1 python3 test_meep.py` interactively (short test only; longer runs go through `sbatch`).
2. Compare single-task vs 4-task output. Record: does the `1 processes` line change? (Verified finding: the interactive plain-`srun` rank reports `1 processes`; the 4-task template job now reports one world of `4 processes` under `--mpi=pmix` (Jobs 1090/1171–1173). Before the fix both printed `1 processes` — 4 serial replicas.)

### 3.5 Debug task (10 min) — read before claiming speedup

| Symptom | Cause | Fix / status |
|---------|-------|--------------|
| Job 1012 fails immediately, `test_meep.py not found` (or `python: can't open file`) | Submitted from repo root instead of `00_setup/`; relative path `test_meep.py` does not resolve | `cd 00_setup/` and resubmit. Kept as debug record; no code change needed. |
| Every rank prints `Using MPI version 3.1, 1 processes` (plain `srun`, Jobs 1013/1022/1023 era) | Each task runs an independent serial MEEP instance; no domain decomposition across ranks | FIXED 2026-09-17: `srun --mpi=pmix` gives true world sizes (diag Job 1090; `2/4 processes` in Jobs 1148/1149 and 1171/1172/1173 scaling table in `01_foundations/expected_figs/`). Raw logs archived to `/tmp/opencode/repo_archive_2026-09-17/`; transcripts quoted in lessons. |

### 3.6 Queue etiquette

- One node, 4 tasks, `00:15:00` limit is sufficient (~1 min walltime measured).
- Never `--exclusive`; never whole-node requests for this test. Stagger launches (2-node limit on `compute`).

## 4. Self-check + research bridge

1. Why must `sbatch scaling_template.sbatch` run from `00_setup/` and not the repo root? (Relate to Job 1012.)
2. `slurm-1013.out` shows 4 PASS lines. Why does this still fail the CO1 scaling gate? (Quote the MPI line.)
3. Your next job prints PASS on rank 0 but `ModuleNotFoundError` on ranks 1–3. Environment or code fault? What do you check first?

Research bridge: a green import test is the precondition for every later gate (vacuum-pulse `c±2%`, `R+T+A=1±0.02`, gap `±5%`, Mie `±10 nm`, deflector `±3°`). The MPI finding here matters beyond setup: until ranks share one decomposition, timing comparisons across `-n 1/2/4` measure launch overhead, not FDTD scaling — any speedup plot from this state would be invalid, and the same misreading would corrupt later convergence-vs-cost arguments in the capstone.

> Tested: 2026-09-16, `sbatch scaling_template.sbatch`, JobID 1013, meep/1.28.0, 4 tasks, ~1 min walltime, outputs in `expected_figs/`

Update 2026-09-17: launcher fixed to `srun --mpi=pmix -n 4` (diag Job 1090: plain srun → 4× size-1 singletons, pmix → world size 4; proven with Meep '4 processes' Jobs 1092+. mpirun rejected — BYCORE binding error). Canonical header + all 14 sim sbatches rolled out (Jobs 1103–1117 --test-only PASS). Quoted JobIDs ran serially (deterministic — physics stands).
