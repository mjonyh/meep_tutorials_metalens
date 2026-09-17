#!/bin/bash
# Canonical module load for all lessons. Source it: source ../00_setup/load_meep.sh
module purge
module load gcc/12.4 openmpi/5.0.10 openblas/0.3.34 fftw/3.3.11 hdf5/1.14.6 python/3.11.9 meep/1.28.0
# After load, `python3` resolves to the PyMeep venv python
# (/opt/hpc/software/meep/1.28.0/venv/bin/python3, first in PATH).
module list
which python3
