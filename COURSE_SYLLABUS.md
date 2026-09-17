# COURSE SYLLABUS — Meta-Optics with MEEP on HPC (15 h, 5 × 3 h)

Broad sampler, 100% hands-on, PhD/researcher level. Stack: PyMeep 1.28.0 CPU-MPI on SLURM `compute`. Environment: `SETUP_HPC.md`. Scope source of truth: `MASTER_PLAN.md`.

## 1. Objectives

- O1: Run the full meta-optics arc 1D → 2D → resonant → lossy-dispersive → phase-gradient on the cluster, reusing one `sbatch` + normalization + convergence workflow the day after the course.
- O2: Produce publishable-grade evidence per module: analytic overlays, energy checks, resolution tables, efficiency/FWHM numbers with stated caveats.
- O3: Convert one module into a capstone mini-proposal linked to the student's own research, graded on convergence evidence and methods clarity.

## 2. Outcomes — What You Must Show

| # | Artifact | Pass threshold |
|---|----------|----------------|
| E1 | Portfolio: vacuum + Fabry-Perot + Bragg + grating + eff-medium + bands + W1 + cavity + Mie + slit + absorber + library + deflector + metalens (CSV + PNG each) | Per-module gates in §4 (all GREEN/MARGINAL; open caveats quoted, nothing hidden) |
| E2 | One resolution-convergence table + scaling table | Convergence shown (e.g. Mie res sweep, absorber spacer/res table); scaling MEASURED 2026-09-17: W1@res40 Jobs 1171/1172/1173 → 211/181/84 s (n=1/2/4), speedup 1.00/1.17/2.51 (`01_foundations/expected_figs/scaling.csv` + `speedup.png`) |
| E3 | Capstone: 1 page + 5-min lightning talk (brief a/b/c) | Rubric: convergence evidence + methods clarity; walltime budget ≤25 min/4 cores or fallback plan |
| E4 | 5 exit tickets (one per block) | Artifact checks, not attendance (see §5) |

## 3. Prerequisites

Maxwell differential form, complex permittivity, Python + numpy + matplotlib, basic Linux + `sbatch`. Pre-course: complete `00_setup` validation job (Job 1013 pattern) before Day 1.

## 4. Schedule — 5 × 3 h blocks

Timing per block: 20' recap · 30' concept crash · 30' live demo · 90' paired lab (guided → stretch → debug) · 10' show-and-tell + exit ticket.

| Block | Module + lesson | Lab (90') | Objectives summary | Outcomes summary (gate) | Status |
|-------|-----------------|-----------|--------------------|--------------------------|--------|
| Day 1 (3 h) | M1 FDTD + HPC foundations — `01_foundations/lesson.md` | `sim_01_vacuum.py` (Job 1022); `sim_02_fabry.py` (Job 1023); scaling note | O1.1 `Simulation` + `GaussianSource` + `PML` + `add_flux`; O1.2 `sbatch`/`srun`/`squeue`; O1.3 Yee/CFL/PML/ripple | E1.1 arrival c±2%, echo <1% (c_err=0.0011, echo=0.0); E1.2 max\|R+T-1\|=0.000 (≤0.02); E1.3 MPI-caveat statement | GREEN |
| Day 2 (3 h) | M2 S-parameters + effective media — `02_sparams/lesson.md` | `sim_03_bragg.py` (Job 1024); `sim_04_grating.py` (Job 1028); `sim_05_effmedium.py` (Job 1026) | O2.1 dispersive/layered `Medium`; O2.2 empty-run R/T/A with sign-safe guards; O2.3 homogenization limit | E2.1 Bragg peak R=1.003 (>0.95) + TMM overlay; E2.2 grating T=0.51–0.63; E2.3 collapse at λ/5; median \|R+T-1\|=0.0037 with 10/80 band-edge pts to 0.096 | MARGINAL |
| Day 3 (3 h) | M3 bands / W1 / L3 cavity — `03_phc/lesson.md` | `sim_06_band.py` (Job 1030); `sim_08_w1.py` (Job 1031); `sim_08_cavity.py` (Job 1034) | O3.1 `k_point` Γ-X-M-Γ sweep + `Mirror` symmetry; O3.2 localized drive + flux normalization + `Harminv`/decay Q | E3.1 mini-gap 0.5698–0.5785 (1.5%, NOT main gap — no lit claim); E3.2 W1 ~40 dB suppression (>10 dB PASS); E3.3 f=0.3076, Q=97.4, Harminv converges | MARGINAL |
| Day 4 (3 h) | M4 plasmonics + Mie — `04_plasmonics/lesson.md` | `sim_09_mie.py` (Job 1146); `sim_10_slit.py` (Job 1043); `sim_11_absorber.py` (Job 1102) | O4.1 stable dispersive-metal FDTD (`ComplexFields`, res ≥40, vetted fits only); O4.2 enhancement/absorption + convergence note | E4.1 res sweep 522→468→468 nm, analytic 470 nm, delta −2 nm PASS; E4.2 ~1.3x max enhancement; E4.3 best A=0.902 at spacer=15nm/w=0.20 (gate >0.90 PASS, margin thin) | GREEN |
| Day 5 (3 h) | M5 metasurface + metalens + capstone — `05_metalens/lesson.md` | `sim_12_library.py` (Job 1138); `sim_13_deflector.py` (Job 1070); `sim_14_metalens.py` (Job 1071) | O5.1 pillar library T/phase via `get_field_point`; O5.2 supercell deflector + hyperboloidal φ(r); O5.3 capstone proposal | E5.1 circular 6.20 rad (gap 0.088 rad, n=269); E5.2 16.1°=16.1° (±3° PASS), eff 0.87; E5.3 FWHM=0.625 vs λ/2NA=0.904, eff=0.420 | GREEN |

Walltimes (per rank, 4 tasks): M1 <1 min each; M2 ~1/~3/~4 s; M3 ~7 s / ~37 s / ~5 min; M4 Mie ~15 s, slit ~229 s, absorber ~11 min (Job 1102, res 160, true MPI); M5 ~51 s / ~12 min / ~23 min. Queue >30 min on Day 5 → analyze precomputed `05_metalens/expected_figs/`, run overnight.

## 5. Exit tickets (artifact checks)

| Day | Question | Expected answer |
|-----|----------|-----------------|
| 1 | Why does flux ripple if runtime is too short? | Truncated ringdown leaks into spectrum; extend `until_after_sources` until R+T stabilizes |
| 2 | When does homogenization fail, and what is the evidence? | Period ~λ/5; `period_sweep.png` collapse (T 0.99→0.0007 at 0.31 um) |
| 3 | Your band run shows a 1.5% gap. Can you claim the literature TM gap? | No — bands 3–4 mini-gap, no lit reference for this gap in this run |
| 4 | Mie verdict + absorber A=0.902 with NaNs at band edges. Pass or fail, and what keeps it honest? | Mie GREEN Job 1146: 522→468→468 nm, analytic 470 nm, delta −2 nm PASS. Absorber PASS (gate >0.90); NaNs are masked zero-spectrum edges by design; thin margin + spacer/res staircasing table quoted |
| 5 | Library circular coverage 6.20 rad but unwrapped ptp 9.23 rad. Which metric picks the 8 deflector diameters? | Circular/wrapped-gap metric (monotonic branch); unwrapped ptp double-counts winding + resonance branch |

## 6. Capstone (Day 5, 90' lab tail + talks)

Pick one; 1 page + 5-min lightning talk. Template: question, geometry + APIs, numeric gate, walltime budget (≤25 min/4 cores or fallback plan), risk + fallback.

- (a) BIC-inspired grating: from M2 grating, add symmetry-breaking perturbation; track Q vs asymmetry with resolution table.
- (b) Sensing absorber: from M4 MIM absorber (Job 1102 GREEN baseline A=0.902); sweep background index, report nm/RIU + FWHM with PML/runtime controls.
- (c) Extended NA study: extend M5 lens (wider W or shorter f); report FWHM vs λ/2NA + efficiency vs NA with res-20/25/30 convergence column.

Grading: convergence evidence + methods clarity, not plot beauty. Full briefs/rubric/template: `capstone/` (briefs a/b/c, `rubric.md`, `proposal_template.md`).

## 7. Self-check + research bridge

1. A student submits only PNGs, no CSVs or JobIDs. Which outcome (E1–E4) fails first?
2. Which module cannot be scheduled as "run during class, analyze same day" without fallback data, and what is its walltime?
3. Why was the MPI scaling study listed as OPEN before 2026-09-17, and what fixed it?

Research bridge: each module lands on a follow-up — M2→BIC gratings, M3→MPB cross-check and topology inputs, M4→sensing figures of merit, M5→`meep.adjoint` gradients and Bayesian loops over the library CSV. The capstone is the bridge document into the student's own paper.

> Tested: 2026-09-17, `sbatch scaling_template.sbatch`, JobID 1013, meep/1.28.0, 4 tasks, ~1 min walltime. Module evidence Jobs 1022/1023, 1024/1028/1026, 1030/1031/1034, 1146/1043/1102, 1138/1070/1071. Scaling Jobs 1171/1172/1173 (speedup 1.00/1.17/2.51) + negative exhibit Job 1150; clean-dir re-run Job 1175 (byte-identical); lens fallback `05_metalens/fallback_data/` (Job 1071). Status table: GREEN / MARGINAL as in §4; detail in `TEST_STATUS.md`.

Update 2026-09-17: launcher fixed to `srun --mpi=pmix -n 4` (diag Job 1090: plain srun → 4× size-1 singletons, pmix → world size 4; proven with Meep '4 processes' Jobs 1092+. mpirun rejected — BYCORE binding error). Canonical header + all 14 sim sbatches rolled out (Jobs 1103–1117 --test-only PASS). Quoted JobIDs ran serially (deterministic — physics stands).
