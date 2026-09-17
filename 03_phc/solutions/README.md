# Module 3 Solutions — Stretch Challenges

## W1 Frequency Notch Mapping (`sol_w1_freq_probe.py`)

The stretch goal in §3.4 of `03_phc/README.md` asks students to probe intermediate frequencies, specifically $f = 0.33\ c/a$, to map the boundary between the deep in-gap defect state and the out-gap passbands.

### Running

```bash
source ../../00_setup/load_meep.sh
srun --mpi=pmix -n 4 python3 sol_w1_freq_probe.py
```

### Key Takeaway

Transmission is suppressed by $\sim 40\ \text{dB}$ deep in the gap ($f = 0.30\ c/a$), but recovers sharply near $f = 0.33\text{--}0.36\ c/a$, delineating the edge of the line-defect band within the bulk photonic bandgap.
