"""00_setup import test | Objective: verify PyMeep import + version | Outcome: prints version or FAILs loudly.
Run: module load <chain> && srun python3 test_meep.py
Saves: nothing | Walltime: <1 min (UNTESTED — bindings missing 2026-09-16) | Status: BLOCKED
"""

import sys


def main():
    try:
        import meep as mp
    except ImportError as e:
        print(f"FAIL: cannot import meep: {e}")
        print(
            "HINT: modulefile PYTHONPATH is stale; operator must reinstall PyMeep bindings."
        )
        sys.exit(1)
    print(f"meep version: {mp.__version__}")
    assert mp.__version__.startswith("1.28"), f"expected 1.28.x, got {mp.__version__}"
    print("PASS: import meep 1.28.x OK")


if __name__ == "__main__":
    main()
