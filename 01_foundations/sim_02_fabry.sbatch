#!/bin/bash
#SBATCH --partition=compute
#SBATCH --nodes=1 --ntasks=4 --cpus-per-task=1
#SBATCH --time=00:20:00 --job-name=m1-fabry
#SBATCH --output=slurm-%j.out --error=slurm-%j.err
module purge
module load gcc/12.4 openmpi/5.0.10 openblas/0.3.34 fftw/3.3.11 hdf5/1.14.6 python/3.11.9 meep/1.28.0
srun --mpi=pmix -n 4 python3 sim_02_fabry.py --resolution 30
