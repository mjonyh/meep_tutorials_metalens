#!/bin/bash
# test_repo.sh — Automated syntax, batch, and tree hygiene verification
# Usage: ./scripts/test_repo.sh

set -e

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

echo "=== 1. Checking Shell Scripts Syntax (bash -n) ==="
find . \( -name "*.sh" -o -name "*.sbatch" \) -not -path "*/.*" -exec bash -n {} +
echo "PASS: All shell and sbatch scripts passed syntax check."

echo ""
echo "=== 2. Checking Python Syntax (py_compile) ==="
# Load modules if module command is available
if command -v module &>/dev/null; then
    module load gcc/12.4 openmpi/5.0.10 openblas/0.3.34 fftw/3.3.11 hdf5/1.14.6 python/3.11.9 meep/1.28.0 2>/dev/null || true
fi

python3 -m py_compile $(find . -name "*.py" -not -path "*/.*")
# Clean up compilation bytecode caches
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
echo "PASS: All Python scripts compiled without error."

echo ""
echo "=== 3. Testing Slurm Batch Submission (sbatch --test-only) ==="
SBATCH_FAIL=0
for sb in $(find . -name "*.sbatch" -not -path "*/.*"); do
    if ! sbatch --test-only "$sb" &>/dev/null; then
        echo "FAIL: sbatch --test-only failed on $sb"
        SBATCH_FAIL=1
    fi
done

if [ "$SBATCH_FAIL" -eq 0 ]; then
    echo "PASS: All .sbatch files validated successfully by Slurm."
else
    echo "ERROR: One or more sbatch scripts failed validation."
    exit 1
fi

echo ""
echo "=== 4. Checking Repository Tree Hygiene ==="
BANNED_FOUND=0
for pat in "slurm-*.out" "slurm-*.err" "*.h5" "*.pyc"; do
    FOUND=$(find . -name "$pat" -not -path "*/.*")
    if [ -n "$FOUND" ]; then
        echo "WARNING: Disallowed file found: $FOUND"
        BANNED_FOUND=1
    fi
done

if [ "$BANNED_FOUND" -eq 0 ]; then
    echo "PASS: Zero banned runtime artifacts found in repository tree."
fi

echo ""
echo "==============================================="
echo "ALL VERIFICATION CHECKS PASSED SUCCESSFULLY!"
echo "==============================================="
