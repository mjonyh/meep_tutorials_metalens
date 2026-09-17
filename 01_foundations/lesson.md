# Module 1: FDTD and HPC Foundations

## 1. Objectives

- O1.1: Build a `Simulation` with `GaussianSource`, `PML`, `add_flux`/`get_fluxes`, `get_field_point` probes, and `resolution`. Run the vacuum-pulse and Si-slab Fabry-Perot labs.
- O1.2: Submit and monitor batch work with `sbatch`/`srun`/`squeue`; read `slurm-<jobid>.out` for the physics gate line and elapsed time.
- O1.3: Explain Yee grid, Courant (CFL) stability, PML reflection, and runtime-truncation ripple in flux spectra.

## 2. Outcomes — What You Must Show

| # | Artifact | Pass threshold |
|---|----------|----------------|
| E1.1 | `expected_figs/vacuum.png` + `vacuum.csv` | `c_err=0.0011` (gate `<=0.02`); `echo=0.0000` (gate `<0.01`) |
| E1.2 | `expected_figs/fabry.png` + `fabry.csv` (60 freq points, res 30) | `max\|R+T-1\|=0.000` in stdout, `0.0003` recomputed from CSV (gate `<=0.02`); all R/T in `[0,1]` |
| E1.3 | Scaling note + MPI caveat statement | State per-rank elapsed (`~0.3 s` vacuum, `~1 s` fabry) and that `srun -n 4` here ran 4 serial replicas (`1 processes` per rank); correctness unaffected |

## 3. Body

### 3.1 Environment and run commands

Load chain (copy-pasteable, no substitutions):

```bash
module purge
module load gcc/12.4 openmpi/5.0.10 openblas/0.3.34 fftw/3.3.11 hdf5/1.14.6 python/3.11.9 meep/1.28.0
```

Submit (one `.sbatch` per simulation, `compute` partition, 4 tasks):

```bash
sbatch sim_01_vacuum.sbatch   # Job 1022
sbatch sim_02_fabry.sbatch    # Job 1023
squeue -j <jobid>             # monitor; 2-node limit — stagger launches
cat slurm-<jobid>.out         # gate line + elapsed time
```

Reproduce locally from this directory:

```bash
module purge && module load gcc/12.4 openmpi/5.0.10 openblas/0.3.34 fftw/3.3.11 hdf5/1.14.6 python/3.11.9 meep/1.28.0
srun --mpi=pmix -n 4 python3 sim_01_vacuum.py --resolution 30
srun --mpi=pmix -n 4 python3 sim_02_fabry.py --resolution 30
```

| File | SBATCH | Defaults |
|------|--------|----------|
| `sim_01_vacuum.py` | `sim_01_vacuum.sbatch` (`--time=00:15:00`, `m1-vacuum`) | `--resolution 30` |
| `sim_02_fabry.py` | `sim_02_fabry.sbatch` (`--time=00:20:00`, `m1-fabry`) | `--resolution 30`, `fcen=0.5`, `df=0.4`, `nfreq=60`, `run_time=120` |

### 3.2 Guided — Lab 1: vacuum pulse (`sim_01_vacuum.py`)

Theory bite: Yee grid staggers E/H in space and time (second-order accurate). MEEP sets `dt` from the CFL limit automatically. PML absorbs outgoing waves; residual reflection returns as a late echo. Gate on the differential arrival, not absolute time: probes at `x=-2,+2` (`dx=4`) give `dt=4` at `c=1`, cancelling the `GaussianSource` turn-on delay.

What the script does:

1. 1D cell `Lx=12`, `PML(1.0)`, point `Ez` source at `x=-4` (`fcen=0.5`, `df=0.4`).
2. Records `Ez` at `x=±2` every `dt=0.05` until `t=26`.
3. Envelope-centroid arrival per probe; reports `dt`, `c_err=|dt-4|/4`, and post-pulse echo ratio.

Verify:

```bash
head -1 outputs/vacuum.csv
# meep=1.28.0 res=30.0 cols=t,Ez1,Ez2 dt=4.004 c_err=0.0011 echo=0.0000
grep -h "c_err" slurm-1022.out
# dt=4.004 (expect 4.0), c_err=0.0011 (gate <=0.02)
# PML echo=0.0000 (gate <0.01)
```

Figure: `expected_figs/vacuum.png` — `Ez(x=-2)` and `Ez(x=+2)` vs `t`, centroid markers `t1/t2`. Resolution 30, 4 tasks, `~0.3 s`/rank.

### 3.3 Guided — Lab 2: Si-slab Fabry-Perot (`sim_02_fabry.py`)

Theory bite: a slab (`eps=11.7`, thickness `1.0`) produces interference fringes in R/T. Flux monitors need an empty-run normalization (`r0`, `t0`); the reflection monitor sees incident + reflected, so `R=-(r-r0)/r0`, `T=t/t0`. Stopping the run too soon after the source decays truncates the ringdown and leaves ripple on the spectrum — `until_after_sources=120` avoids it here.

What the script does:

1. Cell `Lx=8`, `PML(1.0)`, `Ez` source at `x=-3`; flux planes at `x=∓2`.
2. Two runs at the same resolution: with slab, then empty (`[]`).
3. Writes `freq,R,T` (60 points, `f=0.3–0.7`); plots R/T vs wavelength (`1/f`).

Verify:

```bash
head -1 outputs/fabry.csv
# meep=1.28.0 res=30.0 cols=freq,R,T
grep -h "R+T-1" slurm-1023.out
# max|R+T-1| off-res check: 0.000 (gate ≤0.02)
python3 -c "import numpy as np; d=np.loadtxt('expected_figs/fabry.csv',delimiter=','); R,T=d[:,1],d[:,2]; print(f'max|R+T-1|={np.max(np.abs(R+T-1)):.4f}')"
# max|R+T-1|=0.0003
```

Figure: `expected_figs/fabry.png` — Si-slab R/T vs wavelength, res 30, 4 tasks, `~1 s`/rank. R spans `0.002–0.705`, T spans `0.295–0.998`; all values physical.

### 3.4 Stretch — resolution sweep 20 → 60

Run the documented convergence task before claiming a number is publishable:

```bash
for R in 20 30 40 60; do srun --mpi=pmix -n 4 python3 sim_02_fabry.py --resolution $R --outdir outputs/res$R; done
```

Record per resolution: `max|R+T-1|`, fringe-peak frequency, walltime. Expect the energy error flat at `~0.000` (already converged at 30) and cost rising with R. Keep the table; Module 4 repeats this discipline where under-resolution moves peaks.

### 3.5 Scaling note and MPI caveat

- Measured per-rank elapsed: vacuum `~0.3 s` (Job 1022), fabry `~1 s` (Job 1023). Both far under their `--time` limits (`00:15:00` / `00:20:00`).
- MPI caveat: `slurm-1022.out` and `slurm-1023.out` (archived) logged `1 processes` per rank — those runs used plain `srun -n 4` as 4 serial replicas, not one domain-decomposed job; correctness (gates above) is unaffected. True decomposition verified 2026-09-17 with `srun --mpi=pmix` (diag Job 1090) and the `1/2/4`-task scaling table below.
- Etiquette: never `--exclusive`, never whole-node requests for these 2D labs; stagger launches (2-node `compute` limit).
- Scaling (CO1, measured 2026-09-17, `sim_08_w1.py` @ res 40, `srun --mpi=pmix`): Jobs 1171/1172/1173 → wall 211/181/84 s for n=1/2/4; speedup 1.00/1.17/2.51, efficiency 100/58/63%. Physics bit-identical across decompositions (w1.csv matches to 15 digits). Table + plot: `expected_figs/scaling.csv`, `expected_figs/speedup.png`.
- Negative result (kept as teaching point): same probe @ res 20 gave 31/28 s for n=1/2 but n=4 (Job 1150) never finished one flux run inside 00:15:00 (CANCELLED, healthy node, ranks at ~99% CPU) — decomposing a 35k-cell grid 4 ways is pure halo-sync overhead. Lesson: scale the problem before scaling the ranks; the res-40 table above is the quotable one.

### 3.6 Debug record — Job 1021 (FAIL, kept)

```text
arrival t=18.355 (expect 6.0), c_err=2.0592 (gate <=0.02)
PML echo=0.0000 (gate <0.01)
```

Cause: absolute arrival time gated against the source peak (`t~6` for `df=0.4`) instead of the probe-to-probe difference. The `GaussianSource` turn-on delay is model-dependent; absolute `t` cannot verify `c`. Fix (in `sim_01_vacuum.py`): gate on `dt=t2-t1` over `dx=4` (`dt=4.004`, `c_err=0.0011`, Job 1022). Raw logs archived to `/tmp/opencode/repo_archive_2026-09-17/01_foundations/`; transcript quoted in §3.6 above.

## 4. Self-check + research bridge

Self-check:

1. Why does `sim_01_vacuum.py` gate on the probe-to-probe `dt` rather than the absolute arrival time, and what failed in Job 1021?
2. Your flux spectrum shows ripple with `R+T-1` swinging `±0.1`. Name two causes (runtime truncation vs PML) and the diagnostic that separates them.
3. `srun -n 4` logs `1 processes` per rank. Does this invalidate the R/T gate? What must you rerun before quoting speedup?

Research bridge: differential time-of-flight and empty-run flux normalization are the minimal trusted pair underneath every later module — Bragg stopbands, waveguide suppression, absorber `A>90%`, and metalens efficiency all reduce to comparing a structure run against a calibrated reference with converged resolution and runtime. Master the reference first; resonances only amplify errors you already have.

> Tested: 2026-09-16, `sbatch sim_01_vacuum.sbatch` (JobID 1022) and `sbatch sim_02_fabry.sbatch` (JobID 1023; debug record JobID 1021 retained), meep/1.28.0, 4 tasks, ~0.3 s/rank (vacuum) and ~1 s/rank (fabry), outputs in `expected_figs/` (`vacuum.csv`/`vacuum.png`, `fabry.csv`/`fabry.png`)

Update 2026-09-17: launcher fixed to `srun --mpi=pmix -n 4` (diag Job 1090: plain srun → 4× size-1 singletons, pmix → world size 4; proven with Meep '4 processes' Jobs 1092+. mpirun rejected — BYCORE binding error). Canonical header + all 14 sim sbatches rolled out (Jobs 1103–1117 --test-only PASS). Quoted JobIDs ran serially (deterministic — physics stands).
