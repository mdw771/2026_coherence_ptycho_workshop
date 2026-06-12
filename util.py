import h5py
import numpy as np


def load_ptychodus_data(dp_file, para_file):
    with h5py.File(dp_file, "r") as dp_h5, h5py.File(para_file, "r") as para_h5:
        diffraction_patterns = dp_h5["dp"][:]
        probe = para_h5["probe"][:]
        obj = para_h5["object"][:]
        pixel_size = para_h5["object"].attrs["pixel_height_m"]
        
        if probe.ndim == 3:
            probe = probe[None, ...]  # Add OPR dimension if missing

        probe_positions_px = np.stack(
            (
                para_h5["probe_position_x_m"][:] / pixel_size,
                para_h5["probe_position_y_m"][:] / pixel_size,
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
