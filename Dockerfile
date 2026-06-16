FROM ubuntu:24.04

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

ENV DEBIAN_FRONTEND=noninteractive
ENV HOME=/root
ENV UV_TOOL_BIN_DIR=/usr/local/bin
ENV PATH="/root/.local/bin:/usr/local/bin:${PATH}"
ENV LD_LIBRARY_PATH="/root/local/xcb-xinerama/usr/lib/x86_64-linux-gnu:${LD_LIBRARY_PATH}"

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ca-certificates \
        curl \
        git \
        wget \
    && rm -rf /var/lib/apt/lists/*

RUN curl -LsSf https://astral.sh/uv/install.sh | sh

RUN uv tool install 'ptychodus[globus,gui,ptychi]' --reinstall-package torch

RUN apt-get update \
    && mkdir -p "$HOME/local/xcb-xinerama" \
    && apt-get download libxcb-xinerama0 \
    && dpkg-deb -x libxcb-xinerama0_*.deb "$HOME/local/xcb-xinerama" \
    && rm libxcb-xinerama0_*.deb \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p "$HOME/Downloads" \
    && cd "$HOME/Downloads" \
    && wget https://github.com/git-lfs/git-lfs/releases/download/v3.7.1/git-lfs-linux-amd64-v3.7.1.tar.gz \
    && tar xvzf git-lfs-linux-amd64-v3.7.1.tar.gz \
    && cd git-lfs-3.7.1 \
    && ./install.sh \
    && git lfs install --system \
    && rm -rf "$HOME/Downloads/git-lfs-3.7.1" \
        "$HOME/Downloads/git-lfs-linux-amd64-v3.7.1.tar.gz"

WORKDIR /workspace

CMD ["/bin/bash"]
