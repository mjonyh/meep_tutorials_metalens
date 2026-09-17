# Module 1 Solutions — Stretch Challenges

## Resolution Convergence Sweep (`sol_res_sweep.py`)

The stretch goal in §3.4 of `01_foundations/README.md` asks students to execute a resolution sweep from 20 to 60 px/µm to confirm:
1. Energy conservation error $\max |R + T - 1| \le 0.02$ holds across all grid sizes.
2. The peak reflectance and fringe spacing converge smoothly without discretization artifacts.

### Running

```bash
source ../../00_setup/load_meep.sh
srun --mpi=pmix -n 4 python3 sol_res_sweep.py
```

### Expected Output

```
Res (px/um)  max|R+T-1|      Fringe peak R   Gate      
20           0.0004          0.7048          PASS      
30           0.0003          0.7049          PASS      
40           0.0003          0.7050          PASS      
60           0.0002          0.7051          PASS      
```
Energy error remains $\le 0.0004$ across all tested resolutions; walltime increases cubically ($O(\Delta x^{-3})$ in space-time).
