# Capstone Briefs — meep_tutorial

## 1. Objectives

- O1: Execute one independent extension of a verified lab, reusing its normalization, PML, and resolution discipline.
- O2: Produce convergence evidence (resolution and/or parameter sweep) sufficient to separate physics from grid artifact.
- O3: Deliver a 1-page proposal plus 5-minute lightning talk graded per `rubric.md`.

## 2. Outcomes — What You Must Show

| # | Artifact | Pass threshold |
|---|----------|----------------|
| E1 | `proposal.md` (per `proposal_template.md`) + 5-min talk | All template fields filled; gate numeric and falsifiable |
| E2 | Data + figures (CSV + PNG, labeled axes/units/resolution) | Minimum dataset per brief below; raw CSV committed to `expected_figs/` equivalent |
| E3 | Convergence table (resolution and/or parameter sweep) | >=2 resolutions or >=5 parameter points; delta quoted |
| E4 | Methods note (APIs, normalization, walltime, JobIDs) | Reproducible `sbatch` command + module chain stated |

General constraints: 2D only. Walltime <=25 min on 4 tasks (`compute`), except (c) which may use the `sim_14` 60-min limit with fallback plan. Metals only via `common/materials.py`. Rank-0 I/O. Quote real JobIDs.

---

## Brief (a) — BIC-inspired grating

Start: `02_sparams/sim_04_grating.py` (Job 1028: T=0.51-0.63, ~3 s/rank).

Task: introduce a symmetry-breaking perturbation (dimerized widths, slant, or notch depth `delta`) to a subwavelength Si grating. Track resonance Q vs asymmetry parameter.

| Item | Requirement |
|------|-------------|
| Geometry | Period 0.8 um baseline; perturbation `delta` = 0, 0.02, 0.05, 0.10 (fractional, >=5 points) |
| APIs | `add_flux`/`get_fluxes`, sign-safe normalization `where(\|t0\|>eps,t/t0,0)`; `Harminv` or Lorentzian fit for Q |
| Data | Transmission spectra CSV per `delta`; Q-vs-`delta` table + log-log plot; field map at narrowest resonance |
| Gate | State scaling hypothesis (e.g. Q ~ 1/delta^2) and fit exponent with uncertainty; report where it breaks |
| Convergence | Resolution table at smallest `delta` (res 30/40/60): Q delta quoted; `max\|R+T-1\|` off-resonance <=0.02 |
| Walltime | Each spectrum <=10 min/4 tasks; stagger launches |
| Risks | Perturbation under-resolved at res 30; Q diverges into runtime-truncation ripple — extend `until_after_sources`, re-check |

## Brief (b) — Sensing absorber (builds on absorber debug campaign)

Start: `04_plasmonics/sim_11_absorber.py` (Job 1102 GREEN: best A=0.902 at spacer=15nm/w=0.20, res 160; campaign history Jobs 1056-1059 RED 0.361 → 1092/1098/1100 spacer sweep → 1102 PASS).

Task: reproduce the GREEN baseline, then quantify refractive-index sensing.

| Item | Requirement |
|------|-------------|
| Step 1 reproduce | Rerun Job 1102 config (res 160, spacer 15nm); confirm A ~0.90 peak + NaN mask behavior; log JobID |
| Step 2 fix | Width sweep 0.05-0.38 um in 0.02 um steps at res 60; then spacer sweep 20-60 nm at best width; then resolution table 60/80/100 at best point (>=3 cells across spacer) |
| Step 3 sense | Background index sweep n=1.00/1.01/1.02/1.03 at fixed geometry; linear fit sensitivity S (nm/RIU), FWHM, FOM=S/FWHM |
| APIs | `A=1-R` with sign-preserving empty-run normalization; bare-backplane (w=0) control must give A~0 |
| Data | `absorber.csv` + `absorber_spectra.csv` per width; S-fit CSV + plot; control spectrum |
| Gate | Fix gate A>0.90 before sensing numbers are claimable; sensing gate: S with fit R^2 + FWHM quoted, not S alone |
| Convergence | Resolution column at best width; band-edge mask documented (NaN expected, not instability) |
| Walltime | Full spacer×width sweep ~11 min/rank at res 160 (Job 1102); single-width check ~1 min; stagger (2-node limit) |
| Risks | Under-coupling persists (air-gap geometry gave A~0.03-0.11, Jobs 1057/1058/1056); spacer too thin to mesh — raise resolution before concluding physics |

## Brief (c) — Extended NA study

Start: `05_metalens/sim_12_library.py` (Job 1069) + `sim_14_metalens.py` (Job 1071: focus y=5.80 vs design 6.0, FWHM=0.625 vs dl=0.904, eff=0.420, ~1387 s/rank).

Task: extend the lens aperture or focal length; map FWHM vs diffraction limit and efficiency vs NA.

| Item | Requirement |
|------|-------------|
| Geometry | Baseline W=20 um, f=6.0, NA=0.857; test >=3 NA points (e.g. f=6/8/10 at fixed W, or W=20/30 at fixed f; keep focus inside cell) |
| APIs | `get_field_point` with `force_complex_fields=True`; library diameters from monotonic branch only (see 1065/1069 note) |
| Data | Per NA: `axial.csv` + `focus.csv` (y_focus, FWHM, dl=lambda/2NA, eff); `focal-cut.png` transverse cuts overlaid |
| Gate | FWHM vs lambda/2NA table with estimator stated (Gaussian vs sinc lobe fit); efficiency with normalization stated (lobe \|x\|<=1.5*FWHM vs empty-run power) |
| Convergence | Resolution column res 20/25/30 at one NA; phase-library coverage quoted both ways (unwrapped span + circular max-gap) |
| Walltime | ~23 min/4 tasks per NA at res 25 (Job 1071); use 60-min limit; queue >30 min -> analyze `fallback_data/`/`expected_figs/`, run overnight |
| Risks | Focus falls outside cell (old f=10 failure); T-max 1.022 substrate overshoot biases efficiency — resolution sweep controls it; library max gap 0.088 rad (Job 1138) is far below the 45° level spacing |

## 4. Self-check + research bridge

1. Which brief reuses your own module strength, and what is its falsifiable gate?
2. What is your convergence column, and what walltime does it cost?
3. If the queue blocks your final run, what precomputed data carries the talk?

Research bridge: each brief is a starter for a paper methods section — (a) toward Q-factor engineering, (b) toward critical-coupling sensor design, (c) toward NA/efficiency tradeoff analysis. The graded asset is the convergence argument, not the peak number.

> Tested: 2026-09-17, briefs reference verified JobIDs 1028/1059/1069/1071, meep/1.28.0. No new code in this file.
