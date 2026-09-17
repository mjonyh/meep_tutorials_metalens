"""Shared plotting style: labels, grids, R+T+A check plots."""

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


def setup():
    plt.rcParams.update({"figure.dpi": 150, "axes.grid": True, "grid.alpha": 0.3})


def spectrum(wls, R, T, title, outpath):
    import numpy as np

    setup()
    A = 1.0 - np.asarray(R) - np.asarray(T)
    fig, ax = plt.subplots()
    ax.plot(wls, R, label="R")
    ax.plot(wls, T, label="T")
    ax.plot(wls, A, label="A")
    ax.plot(wls, np.asarray(R) + np.asarray(T) + A, "--", label="R+T+A")
    ax.set_xlabel("wavelength (um)")
    ax.set_ylabel("fraction")
    ax.set_title(title)
    ax.legend()
    fig.tight_layout()
    fig.savefig(outpath)
    plt.close(fig)
