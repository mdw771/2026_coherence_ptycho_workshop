from pathlib import Path
import sys
sys.path.append(Path(__file__).parent.parent.as_posix())

import argparse
import logging

import numpy as np
import torch
import tifffile

import ptychi.api as api
from ptychi.api.task import PtychographyTask
from ptychi.utils import (
    get_suggested_object_size, 
    get_default_complex_dtype, 
)

from util import load_ptychodus_data

logging.basicConfig(level=logging.INFO)


def reconstruct(
    diffraction_patterns: np.ndarray,
    probe: np.ndarray,
    probe_positions_px: np.ndarray,
    pixel_size_m: float
) -> PtychographyTask:
    options = api.LSQMLOptions()
    options.data_options.data = diffraction_patterns

    options.object_options.initial_guess = torch.ones(
        [1, *get_suggested_object_size(probe_positions_px, probe.shape[-2:], extra=100)], 
        dtype=get_default_complex_dtype()
    )
    options.object_options.pixel_size_m = pixel_size_m
    options.object_options.optimizable = True

    options.probe_options.initial_guess = probe

    options.probe_position_options.position_x_px = probe_positions_px[:, 1]
    options.probe_position_options.position_y_px = probe_positions_px[:, 0]
    options.probe_position_options.optimizable = False

    options.reconstructor_options.batch_size = 100
    options.reconstructor_options.num_epochs = 100
    
    task = PtychographyTask(options)
    task.run()
    
    return task


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("dp_file", type=Path)
    parser.add_argument("para_file", type=Path)
    parser.add_argument("output_dir", type=Path)
    args = parser.parse_args()
    
    data = load_ptychodus_data(args.dp_file, args.para_file)
    
    task = reconstruct(
        diffraction_patterns=data["diffraction_patterns"],
        probe=data["probe"],
        probe_positions_px=data["probe_positions"],
        pixel_size_m=data["pixel_size"],
    )
    recon = task.get_data_to_cpu('object', as_numpy=True)
    tifffile.imwrite(args.output_dir / "recon_phase.tiff", np.angle(recon[0]))
    tifffile.imwrite(args.output_dir / "recon_mag.tiff", np.abs(recon[0]))


if __name__ == "__main__":
    main()