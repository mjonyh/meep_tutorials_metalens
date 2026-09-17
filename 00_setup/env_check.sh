#!/bin/bash
# 00_setup env check | Objective: verify modules + paths | Outcome: PASS/FAIL table, no fake PASS
# Run: bash env_check.sh
set -u
echo "== modules =="
if command -v module >/dev/null 2>&1; then module list 2>&1 | head -n 15; else echo "lmod not in PATH; run: source /usr/share/lmod/lmod/init/zsh"; fi
echo "== paths =="
for p in /opt/hpc/software/meep/1.28.0/bin/meep /opt/hpc/software/meep/1.28.0/venv/bin/python "/opt/hpc/software/meep/1.28.0/venv/lib/python3.11/site-packages" /opt/hpc/software/meep/1.28.0/lib/python3.11/site-packages; do
	if [ -e "$p" ]; then echo "FOUND $p"; else echo "MISSING $p"; fi
done
echo "== partition =="
sinfo -s 2>&1 | head -n 5
