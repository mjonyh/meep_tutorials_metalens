# Instructor Timing — 5 x 3 h (20/30/30/90/10)

## 1. Objectives

- O1: Hold every 3 h block to 20' recap / 30' crash / 30' demo / 90' lab / 10' show-and-tell + exit ticket.
- O2: Keep all student jobs inside walltime and queue limits (2 nodes, `compute`, 4 tasks/job).
- O3: Never block class on the queue; fallback path ready for every long job.

## 2. Outcomes — Per-module timing + walltime budget

Standard block (180 min):

| Segment | Min | Activity |
|---------|-----|----------|
| Recap | 20 | Exit-ticket answers, gate numbers from prior day |
| Crash | 30 | Concepts only; no live coding |
| Demo | 30 | Instructor runs one short job live; students read `slurm-*.out` gate line |
| Lab | 90 | Guided (30') -> stretch (30') -> debug (30'); pairs, one `sbatch` per simulation |
| Show-and-tell + exit | 10 | 2 pairs show PNG + gate; exit ticket collected |

Per-module lab plan (measured walltimes, 4 tasks, meep/1.28.0):

| Module | Labs + verified walltime/rank | Lab-90 allocation | Fallback if queue >30 min |
|--------|-------------------------------|-------------------|---------------------------|
| M1 foundations | vacuum ~0.3 s (Job 1022); fabry ~1 s (Job 1023) | 30' vacuum + 30' fabry + 30' res sweep + MPI-caveat read | None needed; rerun from `expected_figs/` CSVs |
| M2 sparams | bragg ~1 s (1024); grating ~3 s (1028); effmedium ~4.4 s (1026) | 30' bragg + 30' grating debug + 30' effmedium | None needed; keep 1025/1027 debug exhibit on slides |
| M3 phc | bands ~7 s (1030); W1 ~37 s (1031); cavity ~294 s/~5 min (1034) | 25' bands + 30' W1 + 35' cavity submit-early | Submit cavity first in block; analyze prior `expected_figs/Ez.png` while queued |
| M4 plasmonics | mie ~14 s (1064); slit ~229 s (1043); absorber ~11 min (1102, res 160, GREEN) | 25' mie + 30' slit + 35' absorber spacer-sweep analysis | Slit/absorber: precompute one width; pairs sweep different widths in parallel slots |
| M5 metalens+capstone | library ~4 s (1069); deflector ~740 s/~12 min (1070); lens ~1387 s/~23 min (1071) | 20' library + 30' deflector + 40' lens submit + capstone pitches | Lens: 60-min limit sbatch; class analyzes `expected_figs/` + `fallback_data/`; lens runs overnight |

## 3. Queue-stagger plan (2 nodes, 12 CPU/node)

- Never `--exclusive`; never whole-node requests for 2D labs. One node, 4 tasks/job is the default.
- Max ~2-3 concurrent 4-task jobs comfortably; class of N pairs staggers: half launch at :00, half at :10. Instructor keeps `squeue -u` visible.
- Long jobs first: M3 cavity, M4 slit, M5 deflector/lens submitted at lab start; short sweeps fill queue gaps.
- `sim_14` lens: single submission per pair, 60-min limit, stagger across pairs; no resubmits without `scancel` of stale job.
- MPI note (open): `srun -n 4` currently runs 4 serial replicas (`1 processes` per rank). Do not schedule a scaling-race demo until the launch is fixed; M1 scaling slot is correctness-gate reading instead.

## 4. Self-check + research bridge

1. Which job in each block is submitted first, and why?
2. Queue hits 40 min in M5. What do students analyze, and what runs overnight?
3. Why is staggering required on 2 nodes even though each job asks for only 4 tasks?

Research bridge: stagger + fallback + measured walltime is the transferable HPC habit; capstone proposals inherit the same budget table.

> Tested: 2026-09-17, walltimes from TEST_STATUS.md 2026-09-17 update (Jobs 1022-1071), meep/1.28.0.
