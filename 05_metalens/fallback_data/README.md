# Fallback data — 2D metalens (queue >30 min plan)

Precomputed outputs of `sim_14_metalens.py` so Day-5 analysis never blocks on the queue.
Use these files iff the live `sbatch sim_14_metalens.sbatch` job is still pending after 30 min; run the live job overnight and diff against this baseline.

| Item | Value |
|------|-------|
| Source job | Job 1071, `sbatch sim_14_metalens.sbatch` |
| Command | `srun --mpi=pmix -n 4 python3 sim_14_metalens.py --resolution 25` |
| Stack | meep/1.28.0, 4 tasks, ~1387 s/rank (~23 min) |
| Design | λ=1.55 µm, f=6.0 µm, W=20 µm cylindrical lens |
| Result | focus y=5.80 (design 6.0), FWHM=0.625 vs λ/2NA=0.904, eff=0.420 |

Files: `focus.csv` (transverse cut at focal plane, header carries y_focus/FWHM/eff), `axial.csv` (on-axis intensity vs y), `focal-cut.png` (figure).
Identical copies live in `../expected_figs/`.
