#!/bin/bash
#SBATCH --partition=compute
#SBATCH --nodes=1 --ntasks=1 --cpus-per-task=1
#SBATCH --time=00:10:00 --job-name=m4-mie-r25
#SBATCH --output=diag-mie-r25-%j.out --error=diag-mie-r25-%j.err
module purge
module load gcc/12.4 openmpi/5.0.10 openblas/0.3.34 fftw/3.3.11 hdf5/1.14.6 python/3.11.9 meep/1.28.0
python3 diag_mie_r25.py
