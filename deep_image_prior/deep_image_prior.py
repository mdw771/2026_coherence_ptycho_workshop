import marimo

__generated_with = "0.23.9"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import logging
    import sys
    from pathlib import Path
    import copy
    sys.path.append(Path(__file__).parent.parent.as_posix())
    logging.basicConfig(level=logging.INFO)

    import torch
    import matplotlib.pyplot as plt

    import ptychi.api as api
    from ptychi.api.task import PtychographyTask
    from ptychi.utils import get_suggested_object_size, get_default_complex_dtype, generate_initial_opr_mode_weights

    from util import load_ptychodus_data, plot_object

    return (
        Path,
        PtychographyTask,
        api,
        copy,
        get_default_complex_dtype,
        get_suggested_object_size,
        load_ptychodus_data,
        mo,
        plot_object,
        torch,
    )


@app.cell
def _(Path):
    PROJECT_ROOT = Path(__file__).parent.parent
    return (PROJECT_ROOT,)


@app.cell
def _(PROJECT_ROOT, load_ptychodus_data):
    data = load_ptychodus_data(
        dp_file=PROJECT_ROOT / "data/tungsten/ptychodus_dp.hdf5",
        para_file=PROJECT_ROOT / "data/tungsten/ptychodus_para.hdf5"
    )

    probe = data["probe"]
    positions_px = data["probe_positions"]
    pixel_size_m = data["pixel_size"]
    return data, pixel_size_m, positions_px, probe


@app.cell
def _(
    api,
    data,
    get_default_complex_dtype,
    get_suggested_object_size,
    pixel_size_m,
    positions_px,
    probe,
    torch,
):
    options = api.AutodiffPtychographyOptions()
    options.data_options.data = data["diffraction_patterns"]

    options.object_options.initial_guess = torch.ones(
        [1, *get_suggested_object_size(positions_px, probe.shape[-2:], extra=100)], 
        dtype=get_default_complex_dtype()
    )
    options.object_options.experimental.deep_image_prior_options.enabled = True
    options.object_options.experimental.deep_image_prior_options.model = api.enums.DIPModels.AUTOENCODER
    options.object_options.experimental.deep_image_prior_options.model_params = {
        "num_in_channels": 32,
        "num_levels": 4,
        "base_channels": 32,
        "use_batchnorm": True,
    }
    options.object_options.experimental.deep_image_prior_options.constrain_object_outside_network = False
    options.object_options.pixel_size_m = pixel_size_m
    options.object_options.optimizable = True
    options.object_options.optimizer = api.Optimizers.ADAM
    options.object_options.step_size = 1e-5

    options.probe_options.initial_guess = probe

    options.probe_position_options.position_x_px = positions_px[:, 1]
    options.probe_position_options.position_y_px = positions_px[:, 0]
    options.probe_position_options.optimizable = False

    options.reconstructor_options.batch_size = 100
    options.reconstructor_options.num_epochs = 100
    options.reconstructor_options.allow_nondeterministic_algorithms = False
    return (options,)


@app.cell
def _(PtychographyTask, options):
    task = PtychographyTask(options)
    task.run()
    return (task,)


@app.cell
def _(plot_object, task):
    recon = task.get_data_to_cpu('object', as_numpy=True)[0, 250:500, 250:500]
    plot_object(recon)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Now make a copy of the Options object and decimate the data by 20 times.
    """)
    return


@app.cell
def _(copy, options):
    options_downsampled = copy.deepcopy(options)
    options_downsampled.data_options.data = options.data_options.data[::20]
    options_downsampled.probe_position_options.position_x_px = options.probe_position_options.position_x_px[::20]
    options_downsampled.probe_position_options.position_y_px = options.probe_position_options.position_y_px[::20]
    return (options_downsampled,)


@app.cell
def _(PtychographyTask, options_downsampled):
    task_downsampled = PtychographyTask(options_downsampled)
    task_downsampled.run()
    return (task_downsampled,)


@app.cell
def _(plot_object, task_downsampled):
    recon_downsampled = task_downsampled.get_data_to_cpu('object', as_numpy=True)[0, 250:500, 250:500]
    plot_object(recon_downsampled)
    return


if __name__ == "__main__":
    app.run()
