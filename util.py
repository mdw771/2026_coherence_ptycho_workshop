from typing import Any
from pathlib import Path
import h5py
import numpy as np
import matplotlib.pyplot as plt


def load_ptychodus_data(dp_file: Path, para_file: Path) -> dict[str, Any]:
    with h5py.File(dp_file, "r") as dp_h5, h5py.File(para_file, "r") as para_h5:
        diffraction_patterns = dp_h5["dp"][:]
        probe = para_h5["probe"][:]
        obj = para_h5["object"][:]
        pixel_size = para_h5["object"].attrs["pixel_height_m"]
        
        if probe.ndim == 3:
            probe = probe[None, ...]  # Add OPR dimension if missing

        probe_positions_px = np.stack(
            (
                para_h5["probe_position_y_m"][:] / pixel_size,
                para_h5["probe_position_x_m"][:] / pixel_size,
            ),
            axis=1,
        )

    return {
        "diffraction_patterns": diffraction_patterns,
        "probe": probe,
        "object": obj,
        "pixel_size": pixel_size,
        "probe_positions": probe_positions_px,
    }


def plot_object(arr):
    fig, ax = plt.subplots(1, 2)
    if arr.ndim == 3:
        arr = arr[0]
    im_abs = ax[0].imshow(np.abs(arr))
    ax[0].set_title("Magnitude")
    im_phase = ax[1].imshow(np.angle(arr))
    ax[1].set_title("Phase")
    plt.colorbar(im_abs)
    plt.colorbar(im_phase)
    return fig
