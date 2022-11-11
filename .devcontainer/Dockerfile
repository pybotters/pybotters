FROM mcr.microsoft.com/devcontainers/python:0-3.7-bullseye

RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends \
    bash-completion \
    && rm -rf /var/lib/apt/lists/*

ENV POETRY_HOME="/etc/poetry" \
    POETRY_VIRTUALENVS_CREATE="false"
ENV PATH="$POETRY_HOME/bin:$PATH"
RUN curl -sSL https://install.python-poetry.org | POETRY_VERSION=1.1.15 python3 - \
    && poetry completions bash > /etc/bash_completion.d/poetry.bash-completion

RUN rm -rf "$PIPX_HOME"
