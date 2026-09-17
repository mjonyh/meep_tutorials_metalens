# Module 3: Photonic Crystals — Bands, W1 Waveguide, L3 Cavity

## 1. Objectives

- O3.1: Sweep Bloch `k_point` over Γ-X-M-Γ (`Simulation(k_point=...)`, `Harminv` at each k); apply `Mirror(X/Y)` symmetry to cut cell and runtime in cavity runs.
- O3.2: Excite with localized `GaussianSource` / `ContinuousSource` (note: `EigenModeSource` concept — these labs use equivalent localized drive + flux), extract waveguide transmission via `add_flux`/`get_fluxes` with empty-run normalization, extract cavity frequency and Q via `Harminv` / ringdown decay.

Prerequisites: Module 1–2 (`sbatch`, `add_flux`, R/T normalization). Walltime budget: bands ~1 min, W1 ~2 min, cavity ~6 min on 4 tasks.

## 2. Outcomes — What You Must Show

| # | Artifact | Pass threshold | Verified value |
|---|----------|----------------|----------------|
| E3.1 | `expected_figs/bands.png` + `bands.csv` | Band diagram Γ-X-M-Γ labeled; largest detected gap quoted | Gap bands 3–4: 0.5698–0.5785 (1.5%). **Caveat: higher-order mini-gap, NOT main TM gap. ±5%-vs-literature gate NOT claimed — no lit reference exists for this gap in this run.** |
| E3.2 | `expected_figs/w1.png` + `w1.csv` | In-gap suppression >10 dB vs out-gap passband | f=0.25: T=0.339; f=0.30: T=3.3e-05; f=0.36: T=1.0 (clipped). In-gap suppression 10·log10(0.339/3.3e-05) ≈ 40 dB. **PASS.** |
| E3.3 | `expected_figs/Ez.png` + `cavity.csv` | `Harminv` converges: single mode (f, Q) + steady-state Ez pattern | f=0.3076, Q=97.4, err ~2.4e-08. **PASS (converges).** |

## 3. Body

### 3.1 Files and commands

| Lab | Script | Batch | Default resolution |
|-----|--------|-------|--------------------|
| Bands (Lab 06) | `sim_06_band.py` | `sim_06_band.sbatch` | 24 px/a |
| W1 waveguide (Lab 07 / defect 1) | `sim_08_w1.py` | `sim_08_w1.sbatch` | 20 px/a |
| L3 cavity (Lab 08 / defect 2) | `sim_08_cavity.py` | `sim_08_cavity.sbatch` | 24 px/a |

> Note on numbering: The two defect labs (W1 line defect and L3 point defect) share the `sim_08_*` prefix in the implementation (`sim_08_w1.py` and `sim_08_cavity.py`).

Run (copy-paste; one batch per simulation; stagger launches — 2-node limit):

```bash
module purge
module load gcc/12.4 openmpi/5.0.10 openblas/0.3.34 fftw/3.3.11 hdf5/1.14.6 python/3.11.9 meep/1.28.0
sbatch sim_06_band.sbatch    # Job 1030, 4 tasks, ~7 s/rank elapsed
sbatch sim_08_w1.sbatch      # Job 1031, 4 tasks, ~37 s/rank elapsed
sbatch sim_08_cavity.sbatch  # Job 1034, 4 tasks, ~294 s/rank elapsed (~5 min)
```

Direct (short test / login-node check only for syntax, not production):

```bash
srun --mpi=pmix -n 4 python3 sim_06_band.py --resolution 24 --outdir outputs
srun --mpi=pmix -n 4 python3 sim_08_w1.py --resolution 20 --outdir outputs
srun --mpi=pmix -n 4 python3 sim_08_cavity.py --resolution 24 --outdir outputs
```

Check outputs:

```bash
head -n 5 outputs/bands.csv; cat outputs/w1.csv; cat outputs/cavity.csv
tail -n 20 slurm-1030.out; tail -n 20 slurm-1031.out; tail -n 20 slurm-1034.out
```

### 3.2 Theory bite

- Bloch theorem: eigenmodes at each `k_point` are periodic up to phase. Scanning Γ(0,0)→X(0.5,0)→M(0.5,0.5)→Γ traces band edges. A gap = frequency interval with no mode at any k on the path.
- `Harminv` fits time-ringdown to decaying exponentials. It returns (freq, Q, amplitude, error). Accept only modes with `err < 0.05` and amplitude well above noise; Bloch runs need `mp.use_complex_fields` equivalent (complex fields auto-enabled when `k_point ≠ 0`).
- W1 transmission must be normalized: `T(f) = flux_W1(f) / flux_empty(f)`. Raw flux is meaningless (source spectrum + grid). Clamp display to [1e-6, 1.0] for dB plots.
- Cavity Q: `Harminv` after broadband pulse gives f0; second run with `ContinuousSource(f0)` builds steady-state `Ez.png`. `Mirror(X)+Mirror(Y)` valid here because source at (0,0,0) and L3 defect are symmetric; do not use mirrors with off-center sources.

### 3.3 Guided tasks

1. Bands: submit `sim_06_band.sbatch`. Confirm `slurm-1030.out` ends with `gap: bands 3-4: 0.5698-0.5785 (1.5%)`. Open `outputs/bands.png`: 24 k-points, x-ticks G-X-M-G.
2. W1: submit `sim_08_w1.sbatch`. Confirm `outputs/w1.csv` matches `0.25→0.339, 0.30→3.3e-05, 0.36→1.0`. Compute suppression: `10*log10(0.339/3.32e-05) ≈ 40 dB`.
3. Cavity: submit `sim_08_cavity.sbatch`. Confirm `slurm-1034.out` shows `modes=[(0.3076, 97.4)]` with `err ~2.4e-08` on all ranks. Open `outputs/Ez.png`: localized spot at defect center.

### 3.4 Stretch tasks

1. Bands resolution: re-run `--resolution 32`. Gap edges move <2%? Record in lab notebook.
2. W1 frequency: add f=0.33 probe. Is it still suppressed? Map the gap edge.
3. Cavity runtime: halve ringdown (`until_after_sources=600→300` in local copy). Q changes? This is the decay-fit convergence test.

### 3.5 Debug table

| Symptom | Cause | Fix |
|---------|-------|-----|
| `bands.csv` all `nan` in columns 3–6 | `Harminv` found <6 modes (normal at some k); `All-NaN slice` RuntimeWarning in `slurm-1030.err` is benign | Check columns 1–2 still filled; increase `runtime` or `nbands*4` search if column 1 also empty |
| W1 T > 1 or negative dB in passband | Missing empty-run normalization (old bug) | Use `T_at()` = `flux_W1/flux_empty`; current code already does this |
| Cavity `modes=[]` / Q=0 | Runtime too short for high Q; probe at field node | Keep `until_after_sources=600`; probe at (0.3, 0.2), not (0,0); check `err` column |
| `Ez.png` uniform / no localization | Plotted before CW steady state or wrong f0 | Re-excite at Harminv f0, run `until=150` before `plot2D` |

### 3.6 Figures (verified runs, copies in `expected_figs/`)

- `expected_figs/bands.png` — square-lattice Si rods (r=0.2a, eps=11.7), TM, res=24, 4 tasks, ~7 s/rank. Bands 1–4 shown; gap 3–4 marked 0.5698–0.5785.
- `expected_figs/w1.png` — W1 T(dB, normalized) vs freq, res=20, 4 tasks, ~37 s/rank. Deep notch at 0.30.
- `expected_figs/Ez.png` — L3 mode Ez at f=0.3076, res=24, 4 tasks, ~294 s/rank. Field confined to 3-hole defect.

## 4. Self-check + research bridge

Self-check:

1. Why does the reported 1.5% gap not satisfy the "gap ±5% of literature" gate, and what would you need to claim it?
2. Why is empty-run normalization required for W1 T, and what goes wrong in dB if you skip it?
3. Why does the cavity script run Harminv first, then a second CW run for `Ez.png` instead of plotting the first run directly?

Research bridge: Bloch-scan + defect-transmission + Harminv-Q is the complete 2D PhC workflow. The same chain scales to W1 slow-light dispersion, L3 mode-volume (`Q/V`) estimates for Purcell enhancement, and — with dispersive metals from Module 4 — to plasmonic crystal defect cavities. Keep the normalization and convergence habits; they transfer unchanged.

> Tested: 2026-09-16, `sbatch sim_06_band.sbatch`, JobID 1030, meep/1.28.0, 4 tasks, ~7 s/rank, outputs in `expected_figs/` (bands.csv/png)
> Tested: 2026-09-16, `sbatch sim_08_w1.sbatch`, JobID 1031, meep/1.28.0, 4 tasks, ~37 s/rank, outputs in `expected_figs/` (w1.csv/png)
> Tested: 2026-09-16, `sbatch sim_08_cavity.sbatch`, JobID 1034 (confirm 1033), meep/1.28.0, 4 tasks, ~294 s/rank, outputs in `expected_figs/` (cavity.csv, Ez.png)
