FROM mcr.microsoft.com/vscode/devcontainers/base:noble
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ARG containerWorkspaceFolder
RUN mkdir -p -m 777 "${containerWorkspaceFolder}/.venv"
