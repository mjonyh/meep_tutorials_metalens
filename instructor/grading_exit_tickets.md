# Grading + Exit Tickets — meep_tutorial (per-day artifact checks)

## 1. Objectives

- O1: Check artifacts, not attendance (MASTER_PLAN.md §3.2).
- O2: Give binary pass/fail per day with numeric thresholds from verified gates.
- O3: Feed recap of next block; RED states trigger fix-and-rerun, not doc edits.

## 2. Outcomes — Exit-ticket table (5 days)

Collect in last 10' of block. Each ticket: 3 questions, show CSV/PNG or `slurm-*.out` line.

### Day 1 — Foundations (M1 + setup)

| Q | Check | Pass threshold |
|---|-------|----------------|
| D1.1 | Vacuum pulse: quote `dt`, `c_err`, `echo` from `slurm-1022.out` / `vacuum.csv` header | `c_err<=0.02` (verified 0.0011); `echo<0.01` (verified 0.0000) |
| D1.2 | Fabry-Perot: quote `max\|R+T-1\|` from stdout + CSV recompute | `<=0.02` (verified 0.000 / 0.0003); all R/T in [0,1] |
| D1.3 | MPI: quote the `processes` line; is a speedup plot claimable? | Must answer: `1 processes` per rank = 4 serial replicas; NO speedup claim (CO1 invalid) |

Pass: 3/3. Fail D1.3 (claiming speedup) fails the day.

### Day 2 — S-parameters (M2)

| Q | Check | Pass threshold |
|---|-------|----------------|
| D2.1 | Bragg: peak R + TMM overlay shape; off-resonance `median\|R+T-1\|` | R>0.95 (verified 1.003); median 0.0037 PASS; must state 10/80-pt band-edge caveat (up to 0.096, res note) |
| D2.2 | Grating: T range + normalization formula written from memory | T=0.51-0.63 (Job 1028); formula sign-safe `where(\|t0\|>eps,t/t0,0)`; never `max()` a signed flux |
| D2.3 | Effmedium: T at 5 periods; where is breakdown? | 0.99/0.95/0.41/0.0007/0.88; collapse at λ/5=0.31 um |

Pass: 3/3 with formulas exact.

### Day 3 — PhC (M3)

| Q | Check | Pass threshold |
|---|-------|----------------|
| D3.1 | Bands: gap interval + band indices from `bands.csv` | 0.5698-0.5785 bands 3-4 (1.5%); must state: mini-gap, NOT main TM gap, ±5%-lit NOT claimed |
| D3.2 | W1: T at 0.25/0.30/0.36 + suppression in dB | 0.339/3.3e-05/1.0; ~40 dB (>10 dB PASS); normalization `flux_W1/flux_empty` stated |
| D3.3 | Cavity: Harminv (f, Q, err) from `slurm-1034.out` | f=0.3076, Q=97.4, err~2.4e-08; converges = PASS |

Pass: 3/3 with honest gap caveat (claiming lit pass fails the day).

### Day 4 — Plasmonics (M4)

| Q | Check | Pass threshold |
|---|-------|----------------|
| D4.1 | Mie: res-sweep peaks + analytic delta + verdict | 522→468→468 nm (res 40/80/120, Job 1146); analytic 470 nm, delta −2 nm (\|d\|≤10 PASS); valid window 454–596 nm, NaN 47% = band-edge mask by design |
| D4.2 | Slit: center/max enhancement at 3 λ + stability | 0.14/0.93/1.27x center, 0.15/0.96/1.29x max; no NaN; verdict MARGINAL (~1.3x, no EOT claim) |
| D4.3 | Absorber: best A + NaN fraction + honesty items | A=0.902 (gate >0.90 PASS, margin thin); 33.8% NaN = band-edge mask by design; spacer/res staircasing table quoted |

Pass: D4.3 passes on A=0.902 WITH the thin-margin + staircasing caveats (calling it unconditionally clean fails the day).

### Day 5 — Metalens + capstone (M5)

| Q | Check | Pass threshold |
|---|-------|----------------|
| D5.1 | Library: coverage both metrics + T gate | Circular 6.20 rad (gap 0.088 rad, n=269, Job 1138) + unwrapped ptp 9.23 NOT the metric; T≥0.25 keeps 6.20 (Tmin 0.016 at isolated zero d≈0.52) |
| D5.2 | Deflector: theory vs measured angle + efficiency | 16.1° = 16.1°, err 0.0° (±3° PASS); eff 0.87 stated as propagating-power fraction |
| D5.3 | Metalens: y_focus, FWHM vs λ/2NA, eff + proposal filed | y=5.80 (design 6.0); FWHM=0.625 vs dl=0.904; eff=0.420 with normalization stated; 1-page proposal submitted |

Pass: 3/3 + proposal. Capstone graded per `capstone/rubric.md` (convergence + methods, not beauty).

## 3. Grading mechanics

- Per-day: PASS / CONDITIONAL (one fix-and-rerun item) / FAIL. Conditional clears on re-submitted CSV line, no re-attendance.
- OPEN/MARGINAL verdicts (slit enhancement, thin-margin absorber) still PASS the ticket if the student quotes the caveat honestly with numbers — the ticket grades diagnosis, not the gate.
- Record: date, JobID(s) quoted, walltime, artifact path. Example: `D2.1 PASS 2026-09-16 Job1024 R=1.003`.

## 4. Self-check + research bridge

1. Which tickets can PASS while their physics gate is OPEN/MARGINAL, and what must the student write?
2. What single line in `slurm-*.out` invalidates any speedup claim, and on which days does it apply?
3. Your pairmate quotes only the 9.23 rad unwrapped library span. What follow-up question do you ask?

Research bridge: exit-ticket answers are the capstone proposal's evidence column. Keep them.

> Tested: 2026-09-17, thresholds from TEST_STATUS.md 2026-09-17 update (Jobs 1013/1022-1071), meep/1.28.0.
