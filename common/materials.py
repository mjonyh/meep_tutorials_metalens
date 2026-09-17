"""Vetted dispersive fits for Au/Ag/Si. Single source of truth — no inline metal epsilons.

Au/Ag delegate to the upstream PyMeep materials library (`meep.materials`,
Rakic et al. 1998 via `eV_um_scale`), which converts eV pole parameters to
MEEP frequency units. A previous version of this file passed raw eV numbers
as MEEP frequencies (24% error, top Au pole at 5.19 c/a) and blew up with
`fields are NaN or Inf` (Job 1035, 2026-09-16). Never hand-convert: use these.
"""

import meep as mp


def au_rakic():
    """Au (Rakic 1998, 6-oscillator) via upstream `meep.materials.Au`.

    Valid ~0.25–6 um. Stable at resolution >= 40 in tested 2D runs.
    """
    from meep.materials import Au

    return Au


def ag_rakic():
    """Ag (Rakic 1998) via upstream `meep.materials.Ag`. Valid ~0.25–12 um."""
    from meep.materials import Ag

    return Ag


def si_nir():
    """Si near-IR, nondispersive eps=11.7."""
    return mp.Medium(epsilon=11.7)


def sio2():
    """SiO2, nondispersive eps=2.1025."""
    return mp.Medium(epsilon=2.1025)
