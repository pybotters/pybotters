#!/usr/bin/env bash

sudo apt-get -y update
sudo apt-get -y install bash-completion

pipx install poetry~=1.3.0
poetry completions bash >> ~/.bash_completion
poetry config virtualenvs.in-project true
poetry install
