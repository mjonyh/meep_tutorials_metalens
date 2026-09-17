# Module 2 Solutions — Stretch Challenges

## Effective Medium Intermediate Period (`sol_effective_medium.py`)

The stretch goal in §3.5 of `02_sparams/lesson.md` asks students to:
1. Probe an intermediate period of $\Lambda = 0.15\ \mu\text{m}$ ($\approx \lambda/10$).
2. Compare the FDTD measured transmission with the theoretical transmission through a homogeneous dielectric slab having volume-averaged permittivity $\epsilon_{\text{eff}} = f \epsilon_{\text{Si}} + (1-f) \epsilon_{\text{SiO}_2}$.

### Running

```bash
source ../../00_setup/load_meep.sh
srun --mpi=pmix -n 4 python3 sol_effective_medium.py
```

### Key Takeaway

At $\Lambda = 0.15\ \mu\text{m}$, the subwavelength structure behaves as an effective medium without noticeable diffraction scattering, and its Fabry-Perot transmission closely tracks the uniform dielectric prediction ($\epsilon_{\text{eff}} \approx 6.90$). Once the period exceeds $\lambda/5 \approx 0.31\ \mu\text{m}$, spatial dispersion causes homogenization to collapse.
