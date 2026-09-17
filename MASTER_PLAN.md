# MASTER PLAN — Meta-Optics with MEEP on HPC
## From Maxwell to Metalens: Hands-On FDTD Simulation of Metamaterials in 15 Hours

**Version:** 1.0 (master, approved for build) — 2026-09-16
**Location:** `/home/mjonyh/meep_tutorial`
**Audience:** PhD students / researchers (EM + Python background, little/no FDTD)
**Format:** 5 × 3 h intensive workshop, 100% hands-on
**Track:** Broad sampler — gratings, Bragg, photonic crystals, plasmonics/Mie, metasurface + metalens teaser
**Deliverable form:** Markdown lessons + runnable `.py` + Slurm templates, all tested on this cluster
**Two hard rules (locked):**
1. Every documentation file states specific **Objectives** and explicit **Outcomes/Success Criteria**.
2. **Code is tested on HPC before its documentation is written.** Docs quote only verified job IDs, walltimes, figures.

---

## 1. Vision & Selling Points

### 1.1 Objectives (course-level intent)
- CO-INTENT-1: Give researchers a runnable, parallel MEEP workflow on SLURM they can reuse the day after the course.
- CO-INTENT-2: Cover the full meta-optics arc 1D → 2D → resonant → lossy-dispersive → phase-gradient so any follow-up topic (BIC, topology, inverse design) has a landing pad.
- CO-INTENT-3: Teach convergence and HPC discipline (resolution, PML, runtime, scaling) that separates publishable from broken simulations.

### 1.2 Outcomes (what the advertisement promises, verifiable)
By end of 15 h each student possesses:
1. Portfolio of 10+ `sbatch`-ready simulations with field maps + spectra (listed in §4).
2. One scaling report (speedup 1/2/4 cores) and one resolution-convergence table.
3. One capstone mini-proposal (1 page + 5-min lightning talk) linked to their own research.
4. A research starter-kit: `materials.py` (Au/Ag/Si fits), `plot_utils.py`, Slurm header snippet, troubleshooting cheat-sheet.

Poster tagline: *"Stop watching field animations — produce them. Simulate your first metalens in 15 hours on a real cluster."*

---

## 2. Verified HPC Environment (do not document from memory — re-verify at build)

- Cluster: `compute` partition, 2 nodes (`node[01-02]`), 12 CPUs/node, ~63 GB, `gpu:2` (unused).
- Scheduler: SLURM 26.05.2. Commands: `sbatch / srun / squeue / sinfo`.
- MEEP: `1.28.0 MPI + PyMeep` at `/opt/hpc/software/meep/1.28.0`.
  - Modulefile: `/opt/hpc/modules/Core/meep/1.28.0.lua`
  - Preload chain: `gcc/12.4 openmpi/5.0.10 openblas/0.3.34 fftw/3.3.11 hdf5/1.14.6 python/3.11.9`
  - Binaries: `.../bin/meep`, `.../venv/bin/python`, `PYTHONPATH=.../lib/python3.11/site-packages`
  - Run pattern: `srun python3 sim.py`, `srun -n 4 python3 sim.py`
- Workspace starts empty. All materials live under `/home/mjonyh/meep_tutorial` per §6.

> Build rule: `SETUP_HPC.md` is written only after `env_check.sh` + `test_meep.py` pass with a real JobID.

---

## 3. Pedagogical Standard

### 3.1 Objectives (teaching method)
- Teach in loops: 20' recap + 30' concept crash + 30' live demo on login node + 90' paired lab (guided → stretch → debug) + 10' show-and-tell + exit ticket.
- Zero 60-minute lectures. Every lab produces plots, not just "it ran".
- Convergence-first: every module contains a resolution sweep or scaling task.

### 3.2 Outcomes (teaching discipline)
- No task exceeds 25 min walltime on 4 cores, except flagged long job `14_metalens_2D.py` which ships with `fallback_data/` so class never blocks on queue.
- Every lab ends with 2 deliverable plots + 1 numerical check (e.g., energy conservation, analytic overlay).
- Exit ticket per day checks artifacts, not attendance.

### 3.3 Mandatory documentation template (every `.md`)
```markdown
## 1. Objectives (by end of this unit, you will be able to...)
- O1: ...
- O2: ...

## 2. Outcomes — What You Must Show
| # | Artifact | Pass threshold |
|---|----------|----------------|
| E1 | file.csv/png | numeric gate |

## 3. Body (theory bite, commands, tasks)
## 4. Self-check + research bridge
> Tested: date, sbatch file, JobID, meep/1.28.0, cores, walltime, outputs in expected_figs/
```

---

## 4. Course-Level Objectives & Outcomes Matrix

| ID | Objective (capability) | Outcome artifact + pass gate |
|----|------------------------|------------------------------|
| CO1 | Load modules + run parallel PyMeep via SLURM | `scaling_template.sbatch` + `speedup.png`; PML echo <1% in vacuum test |
| CO2 | Extract R/T/A with empty-run normalization for dispersive stacks/gratings | Bragg R>95% stopband vs TMM overlay; grating efficiency CSV; R+T+A=1±0.02 off-resonance |
| CO3 | Compute bands, waveguide T, cavity Q via Harminv | Band PNG with gap %; W1 suppression >10 dB; L3 Q + decay fit |
| CO4 | Simulate Au/Ag without instability; quantify enhancement/absorption | Mie peak ±10 nm vs analytic; SPP enhancement map; MIM absorber A>90% + res. sweep |
| CO5 | Build phase library → deflector → 2D metalens; evaluate efficiency/FWHM | 0–2π library; deflector angle ±3° vs generalized Snell; focal FWHM vs λ/2NA + efficiency |

Prerequisites (stated to students): Maxwell differential form, complex permittivity, Python+numpy+matplotlib, basic Linux + sbatch. Pre-course self-test + `00_setup` validation job provided.

---

## 5. Module-by-Module Plan (5 × 3 h)

### Module 1 — FDTD & HPC Foundations (3 h)
**Objectives:**
- O1.1: Build `Simulation` with `GaussianSource`, `PML`, `add_flux`, `output_efield`, `resolution`.
- O1.2: Submit/monitor `sbatch`, run `srun -n X`, read `slurm-*.out`.
- O1.3: Explain Yee grid, Courant CFL, PML reflection, runtime-truncation ripple.

**Hands-on labs (all `sbatch`-tested):**
1. `01_vacuum_pulse.py` — 1D pulse, verify c, PML check.
2. `02_fabry_perot.py` — Si slab fringes vs analytic Fresnel; resolution sweep 20→60 px/µm.
3. Scaling study — same job `-n 1/2/4`, plot speedup; learn node-request etiquette.

**Outcomes:**
- E1.1 `vacuum_pulse.png`: arrival at c±2%, echo <1%.
- E1.2 `fabry_perot.csv` + overlay + `resolution_sweep.png`.
- E1.3 `speedup.png` with efficiency comment.
- Exit question: why does flux ripple if runtime too short?

**MEEP APIs:** `Simulation, PML, GaussianSource, Volume, add_flux/get_fluxes, output_efield`.

### Module 2 — Dispersion, Effective Media & S-Parameters (3 h)
**Objectives:**
- O2.1: Implement `Medium` with `LorentzianSusceptibility/DrudeSusceptibility`; fit Au/Ag.
- O2.2: Normalize with empty run; extract R/T/A.
- O2.3: Explain homogenization validity limit.

**Labs:**
1. `03_bragg_mirror.py` — 8-bilayer Si/SiO2 DBR vs TMM.
2. `04_grating.py` — 1D Si grating 0th/1st order vs angle; Wood anomaly field.
3. `05_effective_medium.py` — subwavelength stack vs `epsilon_eff`; breakdown at period ~λ/5.

**Outcomes:**
- E2.1 DBR stopband PNG with TMM overlay, R peak quoted.
- E2.2 Grating efficiency table CSV.
- E2.3 `period_sweep.png` showing homogenization failure.
- Gate: R+T+A=1±0.02 off-resonance.

### Module 3 — Photonic Crystals: Bands, Gaps & Cavities (3 h)
**Objectives:**
- O3.1: Sweep `k_point` over Γ-X-M-Γ; use `Mirror` symmetry for 4× speedup.
- O3.2: Drive with `EigenModeSource`; extract Q via `Harminv`/decay fit.

**Labs:**
1. `06_phc_band.py` — 2D square lattice Si rods, TM gap, gap-midgap %.
2. `07_phc_waveguide.py` — W1 line defect, in-gap vs out-gap transmission.
3. `08_L3_cavity.py` — L3 cavity mode pattern, Q + mode-volume estimate.

**Outcomes:**
- E3.1 Band PNG with gap labeled (within 5% of literature).
- E3.2 Waveguide T suppression >10 dB in gap.
- E3.3 `Ez.png` + Q + ringdown fit residual.

### Module 4 — Plasmonics & Mie: Lossy, Subwavelength, Resonant (3 h)
**Objectives:**
- O4.1: Run stable dispersive-metal FDTD (`ComplexFields`, interface meshing, Courant care).
- O4.2: Quantify scattering/absorption/enhancement with convergence note.

**Labs:**
1. `09_mie_sphere.py` — Au cylinder/sphere scattering vs analytic Mie dipolar peak.
2. `10_spp_slit.py` — MIM slit extraordinary transmission, `|E|/|E0|` map.
3. `11_perfect_absorber.py` — MIM patch absorber, patch-width sweep to >90%.

**Outcomes:**
- E4.1 Scattering CSV + overlay, peak ±10 nm at converged resolution.
- E4.2 Enhancement factor quoted on map.
- E4.3 A(λ) peak + sweep + resolution table proving convergence (trap: Q drifts if under-resolved).
- Gate: no NaN/blow-up; loss accounted for.

### Module 5 — Gradient Metasurfaces, Metalens Teaser & Capstone (3 h)
**Objectives:**
- O5.1: Build pillar meta-atom library (T + phase via `get_field_point`).
- O5.2: Assemble supercell deflector + hyperboloidal lens `φ(r)=-2π/λ(√(f²+r²)-f)`.
- O5.3: Propose follow-up research with efficiency/chromaticity/fabrication limits.

**Labs:**
1. `12_meta_atom_library.py` — Si pillar on SiO2 at λ=1.55 µm, diameter sweep → 8 levels 0–2π.
2. `13_beam_deflector.py` — 8-element supercell, angle vs generalized Snell.
3. `14_metalens_2D.py` — 20-µm cylindrical lens, focal spot FWHM vs diffraction limit + efficiency. Long job with precomputed fallback.

**Outcomes:**
- E5.1 `T-phase.png` library covering full 2π.
- E5.2 Deflector angle within 3° of theory.
- E5.3 `focal-cut.png` FWHM + efficiency + 1-page capstone proposal + lightning talk.
- Capstone choice: (a) BIC-inspired grating, (b) sensing absorber, (c) extended NA study. Graded on convergence evidence, not prettiness.

**Research bridge (30'):** `meep.adjoint` gradients, Bayesian loop, MPB comparison, fabrication constraints, how to frame next paper.

---

## 6. Repository Build Order (test-first, no docs before green run)

```
meep_tutorial/
  MASTER_PLAN.md (this file)
  README.md + COURSE_SYLLABUS.md + SETUP_HPC.md   # written after 00_setup passes
  00_setup/ env_check.sh load_meep.sh test_meep.py scaling_template.sbatch
  01_foundations/ 02_sparams/ 03_phc/ 04_plasmonics/ 05_metalens/
    sim_*.py *.sbatch lesson.md solutions/ expected_figs/ fallback_data/ (M5 only)
  common/ plot_utils.py materials.py slurm_header.snippet
  capstone/ briefs.md rubric.md proposal_template.md
  instructor/ timing.md troubleshooting.md grading_exit_tickets.md
```

Build sequence per module: draft code → compile check → `sbatch` on `compute` → collect `*.h5/*.csv/*.png + slurm-*.out` → physics gate (§7) → then write `lesson.md` quoting real JobID/walltime/figures → clean-dir re-run using pasted commands.

---

## 7. Test Gates (code must pass before its doc is unlocked)

| Test | Evidence | Gate |
|------|----------|------|
| Import | `srun python3 test_meep.py` | `import meep` 1.28.0 OK |
| Vacuum | `01` | c±2%, PML echo <1% |
| S-param | `02/03/04` | R+T+A=1±0.02, no truncation ripple |
| Bands/Q | `06/08` | gap ±5%, Harminv fit converges |
| Metals | `09/10/11` | stable, Mie ±10 nm, A>90% + res. sweep |
| Metalens | `12/13/14` | 0–2π coverage, angle ±3°, focus + efficiency |
| Perf | scaling | <25 min on 4 cores (except 14 + fallback) |

Lesson footer records: `Tested: date, sbatch, JobID, meep/1.28.0, cores, walltime, outputs`.

---

## 8. Risks & Mitigations

- Only 2 nodes → stagger launches, 2D-first, 3D demo-only, fallback data for M5, queue etiquette in M1.
- Metal instability → vetted Drude-Lorentz params in `common/materials.py`, resolution rule-of-thumb card.
- Mixed levels → pre-course primer + stretch tasks for advanced; blind beta-run of M4 by one PhD before release.

---

## 9. Next Actions After This Master Plan

1. Build + test `00_setup` (env_check, load script, import test, scaling template).
2. Build + test M1 code, then write M1 docs; repeat M2→M5.
3. Write `COURSE_SYLLABUS.md`, `README.md`, `capstone/`, `instructor/` from verified runs.
4. Final audit: timing, re-run from clean dir, figure gallery for poster.

*End of master plan. Implementation must not deviate from test-first + objectives/outcomes rules without updating this file.*
