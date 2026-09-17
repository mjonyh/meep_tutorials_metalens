# Module 5 Solutions — Stretch Challenges

## Phase-to-Pillar Layout Synthesizer (`sol_phase_interpolator.py`)

The stretch challenge in Module 5 requires mapping the continuous phase profile $\phi(x) = -\frac{2\pi}{\lambda}(\sqrt{f^2 + x^2} - f)$ onto a physical arrangement of pillar diameters using the precomputed library (`expected_figs/library.csv`).

### Running

```bash
python3 sol_phase_interpolator.py --focal_length 6.0 --diameter 20.0
```

### Key Takeaway

By filtering out the narrow resonance dip (where transmission drops below 0.5) and selecting the monotonic high-transmission branch of the phase library, students can automatically generate CAD/layout arrays for metalenses of arbitrary numerical aperture and diameter.
