# Module 4 Solutions — Stretch Challenges

## Mie Peak Resolution Convergence (`sol_mie_convergence.py`)

The stretch goal in §3.3 of `04_plasmonics/README.md` examines the sensitivity of dispersive metal nanoparticles to spatial meshing.

### Running

```bash
source ../../00_setup/load_meep.sh
srun --mpi=pmix -n 4 python3 sol_mie_convergence.py
```

### Key Takeaway

| Resolution | FDTD Peak | Analytic Series | Offset | Gate |
|---|---|---|---|---|
| 40 px/µm | 522 nm | 470 nm | +52 nm | Coarse staircasing artifact |
| 80 px/µm | 468 nm | 470 nm | -2 nm | **PASS** |
| 120 px/µm | 468 nm | 470 nm | -2 nm | **PASS (Converged)** |

Subwavelength metallic boundaries must have $\ge 80\ \text{px}/\mu\text{m}$ (cell size $\le 12.5\ \text{nm}$) for the geometric curvature to be accurately resolved without artificial redshifting.
