
set -euo pipefail

uv export -q --format pylock.toml --no-emit-project --project server -o pylock.toml

rm -rf /tmp/native.venv/

uv venv /tmp/native.venv

rm -rf /tmp/foreign.venv/

uv venv /tmp/foreign.venv

uv pip install --python /tmp/native.venv -r pylock.toml

# uv pip install --python-platform amd64-unknown-linux-gnu --python /tmp/foreign.venv -r pylock.toml
uv pip install --python-platform x86_64-manylinux2014 --python /tmp/foreign.venv -r pylock.toml

cd server

time pex -v --include-tools \
 -e main \
 --layout=packed \
 --sources-dir=. \
 --venv-repository /tmp/native.venv/ \
 --venv-repository /tmp/foreign.venv/ \
 -o test.pex
# docker build --platform=linux/amd64 -t test-server-amd64 .

# docker build -t test-server-aarch64 .

