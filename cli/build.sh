#!/usr/bin/env bash

set -euo pipefail

cd "$(dirname "$0")"

uv pip compile pyproject.toml -q --format pylock.toml -o build/pylock.toml

uv build --wheel --out-dir ./build

uv venv --clear build/install.venv

uv pip install -q --python build/install.venv -r build/pylock.toml

uv --color=never -q pip list --offline --strict --python build/install.venv --format freeze > build/requirements.all.txt

uvx pex==2.69.1 -v --include-tools \
          --layout=packed \
          --project=build/cli-0.1.0-py3-none-any.whl \
          --pip-version latest-compatible \
          --pre \
          --requirements=build/requirements.all.txt \
          --venv-repository build/install.venv/ \
          --max-install-jobs=-1 \
          -o dist/bin.pex
