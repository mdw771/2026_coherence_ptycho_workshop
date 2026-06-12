import marimo

__generated_with = "0.23.9"
app = marimo.App(width="medium")


@app.cell
def _():
    import sys
    from pathlib import Path
    sys.path.append(Path(__file__).parent.parent.as_posix())
    print(sys.path)

    import torch

    import ptychi.api as api
    from ptychi.api.task import PtychographyTask
    from ptychi.utils import get_suggested_object_size, get_default_complex_dtype, generate_initial_opr_mode_weights

    from util import load_ptychodus_data

    return (
        Path,
        PtychographyTask,
        api,
        get_default_complex_dtype,
        get_suggested_object_size,
        load_ptychodus_data,
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
    PtychographyTask,
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
    options.probe_options.optimizable = True
    options.probe_options.optimizer = api.Optimizers.SGD
    options.probe_options.step_size = 0.1

    options.probe_position_options.position_x_px = positions_px[:, 1]
    options.probe_position_options.position_y_px = positions_px[:, 0]
    options.probe_position_options.optimizable = False

    options.reconstructor_options.batch_size = 100
    options.reconstructor_options.num_epochs = 16
    options.reconstructor_options.allow_nondeterministic_algorithms = False

    task = PtychographyTask(options)
    task.run()
    return (task,)


@app.cell
def _(task):
    recon = task.get_data_to_cpu('object', as_numpy=True)[0, 250:500, 250:500]
    return


if __name__ == "__main__":
    app.run()
