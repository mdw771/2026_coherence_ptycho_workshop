# Launching Dectris Cloud session

Launch it from the `Ubuntu 24.04 Utilities v2` environment. **Select 64GB for software storage**.

It is okay if it says an error happened while launching the session. 
Just go to Analysis -> My Sessions, you'll see the session is actually running.
![session failure](docs/asset/img/session_failure.png)

# Setting up environment and installing packages

## If conda is not available

Install Miniforge:
```
curl -L -O "https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-$(uname)-$(uname -m).sh"
```
Then install Miniforge with `bash Miniforge3-Linux-x86_64.sh`. When asked about installation path, use `/dectris_data/miniforge3`.

Open a new bash terminal or source the bashrc `source ~/.bashrc` to enable conda.

## Installing software

### Installing Ptychodus with Pty-Chi

```
conda create -y -n ptycho python==3.11
conda activate ptycho

pip install ptychodus[globus,gui,ptychi]
```
The Dectris Cloud environment misses some libraries. Install the native Qt/XCB libraries required by the GUI:

```
conda install -c conda-forge \
  libxcb libxkbcommon \
  xcb-util xcb-util-image xcb-util-keysyms \
  xcb-util-renderutil xcb-util-wm
```

Make the conda environment libraries visible to Qt:

```
export LD_LIBRARY_PATH="$CONDA_PREFIX/lib:${LD_LIBRARY_PATH:-}"
```

Launch Ptychodus:
```
ptychodus
```

> If you want to install Pty-Chi alone, just do `pip install pty-chi`. If you prefer local, project-specific environment, we recommend `uv` which always delivers strictly deterministic dependencies. Git clone Pty-Chi using `git clone https://github.com/AdvancedPhotonSource/pty-chi`, then run `uv sync` in the project root. 

# Downloading data and scripts for this workshop

Under `/dectris_cloud`, clone this repository:

```
https://github.com/mdw771/2026_coherence_ptycho_workshop.git
```

Some data files are tracked by Git LFS and may take time to download.
