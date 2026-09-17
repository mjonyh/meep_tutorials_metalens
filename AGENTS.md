# AGENTS.md — meep_tutorial (Meta-Optics with MEEP on HPC)

> Project rulebook for every agent/human implementing this 15 h hands-on workshop.
> Source of truth for scope: `MASTER_PLAN.md`. If conflict, `MASTER_PLAN.md` wins on scope; this file wins on workflow.

## 1. Project identity

- Course: 15 h, 5×3 h, PhD/researcher level, 100% hands-on, broad sampler (Bragg/grating → PhC → plasmonics/Mie → metasurface/metalens).
- Stack: PyMeep 1.28.0 (MPI, CPU-only) on SLURM `compute`. No laptop MEEP, no GPU MEEP, no unpinned versions.
- Deliverables: runnable `.py` + `.sbatch` + `README.md` per lab, all tested on this cluster before documenting.
- Two hard rules:
  1. Every `.md` has **Objectives** + **Outcomes/Success Criteria** with numeric gates.
  2. **Test code first, write docs second.** Docs quote only verified JobID, walltime, figures.

## 2. Verified HPC environment (re-check, never assume)

```
Partition : compute (2 nodes, 12 CPU/node, ~63 GB) | SLURM 26.05.2
Meep      : /opt/hpc/software/meep/1.28.0 | modulefile /opt/hpc/modules/Core/meep/1.28.0.lua
Load chain: gcc/12.4 openmpi/5.0.10 openblas/0.3.34 fftw/3.3.11 hdf5/1.14.6 python/3.11.9 + meep/1.28.0
Run       : srun python3 sim.py | srun --mpi=pmix -n 4 python3 sim.py
Python    : .../1.28.0/venv/bin/python + PYTHONPATH=.../lib/python3.11/site-packages
```

- Use `sbatch` for everything students run longer than 2 min. No bare `mpirun` on login node.
- Keep jobs ≤25 min on 4 cores. Exception: `14_metalens_2D.py` ships with `fallback_data/`.
- 2D-first. 3D only as instructor demo with precomputed output.

## 3. Repo layout (create as needed, no extra top-level dirs)

```
00_setup/ 01_foundations/ 02_sparams/ 03_phc/ 04_plasmonics/ 05_metalens/
  sim_*.py | *.sbatch | README.md | expected_figs/ | solutions/ | fallback_data/ (05 only)
common/ plot_utils.py materials.py slurm_header.snippet
capstone/ briefs.md rubric.md proposal_template.md
instructor/ timing.md troubleshooting.md grading_exit_tickets.md
scripts/ test_repo.sh
README.md COURSE_SYLLABUS.md SETUP_HPC.md MASTER_PLAN.md AGENTS.md
```

- Scratch, queue logs, HDF5 dumps: `/tmp/opencode/`, never committed.
- Never commit `slurm-*.out`, `*.h5`, `__pycache__`, venv paths, tokens, `.env`.

## 4. Test-first workflow (mandatory order per lab)

1. Draft `sim_*.py` + `*.sbatch`. No `README.md` yet.
2. `python3 -m py_compile sim.py` + `bash -n *.sh` + `sbatch --test-only` where possible.
3. `sbatch *.sbatch` on `compute`. Record JobID, cores, walltime, `slurm-*.out`.
4. Physics gate (§7). Fail → fix code, re-run. Never paper over with doc edits.
5. Copy verified `*.csv/*.png` to `expected_figs/`. Write module `README.md` quoting real numbers.
6. Clean-dir re-run using exactly the commands pasted in the doc. Fix drift immediately.

`SETUP_HPC.md`, `README.md`, `COURSE_SYLLABUS.md` are written only after `00_setup/test_meep.py` passes.

## 5. Python/MEEP code standard

- Header docstring in every `sim_*.py` (required):
  ```python
  """<lab name> | Objective: <1 line> | Outcome: <artifact + gate>
  Run: module load <chain> && srun --mpi=pmix -n 4 python3 <file> [--resolution R]
  Saves: outputs/*.csv, outputs/*.png | Walltime: <measured, e.g. ~6 min on 4 cores>
  """
  ```
- `argparse` for `--resolution --fcen --df --run_time --outdir` (defaults = tested values).
- Deterministic: `random.seed` where applicable, log `meep.__version__`, resolution, cell size to CSV header.
- Save both data and figure: `np.savetxt(outputs/*.csv)` + `matplotlib` PNG with labeled axes, units, resolution in title.
- Shared fits only from `common/materials.py` (Au/Ag/Si vetted Drude-Lorentz). No inline metal epsilons.
- Plotting only via `common/plot_utils.py` style (labels, grids, `R+T+A` check plots).
- MPI-safe: rank-0 writes files, guard with `meep.am_master()`.

## 6. Slurm standard (`common/slurm_header.snippet` is canonical)

```bash
#!/bin/bash
#SBATCH --partition=compute
#SBATCH --nodes=1 --ntasks=4 --cpus-per-task=1
#SBATCH --time=00:30:00 --job-name=meep-lab
#SBATCH --output=slurm-%j.out --error=slurm-%j.err
module purge
module load gcc/12.4 openmpi/5.0.10 openblas/0.3.34 fftw/3.3.11 hdf5/1.14.6 python/3.11.9 meep/1.28.0
srun --mpi=pmix -n 4 python3 sim_XX.py --resolution 30
```

- One `.sbatch` per simulation. Time limit = measured walltime + 50% headroom, max 30 min (except 14).
- Never `--exclusive`, never whole-node requests for 2D labs. Stagger launches (2-node limit).

## 7. Physics acceptance gates (doc unlocked only on pass)

| Lab | Gate |
|-----|------|
| 00 import/vacuum | `import meep` 1.28.0 OK; pulse at c±2%, PML echo <1% |
| 01–02 Fabry-Perot/Bragg/grating | R+T+A=1±0.02 off-resonance; TMM/Fresnel overlay; no truncation ripple |
| 06–08 bands/cavity | gap ±5% lit.; W1 suppression >10 dB; Harminv fit converges |
| 09–11 metals | stable (no NaN); Mie peak ±10 nm; absorber A>90% + resolution table |
| 12–14 metalens | 0–2π coverage; deflector ±3° vs theory; focus FWHM vs λ/2NA + efficiency |

Lesson footer (required):
```markdown
> Tested: YYYY-MM-DD, `sbatch <file>`, JobID <id>, meep/1.28.0, <n> tasks, <walltime>, outputs in `expected_figs/`
```

## 8. Documentation standard (professionalism)

- Tone: concise, CLI-toned, imperative. Tables over prose. No hype, no emojis.
- Every `.md` opens with `## 1. Objectives` (O1..On, verbs + API + concept) and `## 2. Outcomes` (E1..En table: artifact + numeric threshold). Close with self-check (3 Qs) + research bridge (1 para: what this unlocks next).
- Commands are copy-pasteable with full `module load` line. No "install MEEP yourself" sections.
- Figures: `expected_figs/` copies of real runs, captioned with resolution/cores/walltime.
- Failures go to `instructor/troubleshooting.md` with `slurm-*.out` excerpt + fix, not deleted.

## 9. Verification before "done" (per lab)

- [ ] `py_compile` + `bash -n` clean
- [ ] `sbatch` PASS with JobID logged, outputs in `expected_figs/`
- [ ] Physics gate met, numbers quoted in module `README.md`
- [ ] Clean-dir re-run with doc commands reproduces artifacts
- [ ] No secrets, no `*.h5`/`slurm-*.out` staged; `git status` clean except intended files

## 10. Privileges, secrets, git

- Never `sudo`/`su`/`doas`. Need privilege → write script to `/tmp/opencode/`, `bash -n` it, surface exact operator command.
- Never print/copy/commit SSH keys, tokens, `.env`, credentials, PII.
- Conventional commits (`feat:`, `fix:`, `docs:`, `chore:`). Never commit/push unless explicitly asked. Stage only touched files.
- Multi-step work: track with TodoWrite (one `in_progress` at a time), mark completed on evidence, not intent.

## 11. Workshop delivery discipline

- Timing per 3 h block: 20' recap · 30' crash · 30' demo · 90' lab (guided→stretch→debug) · 10' show-and-tell + exit ticket.
- Each lab folder states prerequisites, walltime, fallback if queue >30 min (05 only).
- Capstone graded on convergence evidence + methods clarity, not plot beauty (`capstone/rubric.md`).
