#!/usr/bin/env bash

set -euo pipefail

# Helper function for pretty printing headers
log_header() {
    echo -e "\n\033[1;34m=== $1 ===\033[0m"
}

# Helper function to measure and print time
# Usage: measure "Label" command args...
measure() {
    local label="$1"
    shift
    echo -e "\033[0;33m[Running] $label\033[0m"
    echo "Command: $*"

    # Construct the command string that includes redirection to null
    local command_to_run_silently="$* >/dev/null 2>&1"
    # Execute this silent command using 'bash -c' and time it.
    # The timing output from /usr/bin/time will now be visible,
    # while the command's own output is suppressed.
    /usr/bin/time -h bash -c "${command_to_run_silently}"
}

log_header "Starting Benchmark: Pants vs Grog"

# --- Pants Section ---
cd pants/

log_header "Pants: Preparation"
echo "Cleaning Pants cache..."
rm -rf ~/.cache/pants/

log_header "Pants: Benchmarks"

# Cold-start pex builds only
measure "Pants: Cold start (No Daemon, No Cache) - cli pex" \
    pants --no-pantsd --no-local-cache --no-remote-cache-read package cli:cli_bin

# Warm up cache for the next step (not measured)
echo "Warming up Pants cache..."
pants package cli:cli_bin  > /dev/null 2>&1
pants package cli:docker > /dev/null 2>&1


# Cold start (No Daemon) but with populated caches
measure "Pants: Cold start (No Daemon, With Cache) - cli pex" \
    pants --no-pantsd package cli:cli_bin

# Warm start (Daemon active) with caches - building Docker image
measure "Pants: Warm start (With Daemon & Cache) - cli image" \
    pants package cli:docker

cd ..

# --- Grog Section ---

log_header "Grog/uv/pex: Preparation"
echo "Cleaning uv/pex caches..."
uv cache clean --force
rm -rf ~/.pex


log_header "Grog: Benchmarks"

# Cold start (Grog specific)
measure "Uv/pex: Cold start (No Cache) - cli pex" \
    ./cli/build.sh

# Warm start (re-running immediately usually benefits from cache)
measure "Uv/pex: Warm start (with uv caches) - cli pex" \
    ./cli/build.sh

echo "Warming up Grog cache..."
grog build //cli:image

# Grog Docker image build
measure "Grog: Docker Image Build - cli image" \
    grog build //cli:image

log_header "Benchmark Complete"
