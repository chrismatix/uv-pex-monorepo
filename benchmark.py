#!/usr/bin/env -S uv run --script
# /// script
# dependencies = [
#   "statistics==1.0.3.5",
#   "tqdm==4.67.1",
# ]
# ///
import argparse
import math
import os
import shutil
import statistics
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, List, Optional, Sequence
from tqdm import tqdm


# ----------------------------
# Utilities
# ----------------------------

BLUE = "\033[1;34m"
YELLOW = "\033[0;33m"
RESET = "\033[0m"


def log_header(msg: str) -> None:
    print(f"\n{BLUE}=== {msg} ==={RESET}")



def run(
    cmd: Sequence[str], cwd: Optional[Path] = None, quiet: bool = False
) -> None:
    stdout = subprocess.DEVNULL if quiet else None
    stderr = subprocess.DEVNULL if quiet else None
    max_retries = 3
    for attempt in range(max_retries):
        try:
            subprocess.run(
                cmd,
                cwd=str(cwd) if cwd else None,
                check=True,
                stdout=stdout,
                stderr=stderr,
            )
            break
        except subprocess.CalledProcessError:
            if attempt == max_retries - 1:
                raise


def rm_rf(path: Path) -> None:
    if not path.exists():
        return
    if path.is_symlink() or path.is_file():
        path.unlink(missing_ok=True)
        return
    shutil.rmtree(path, ignore_errors=True)


def timed_run(cmd: Sequence[str], cwd: Optional[Path] = None) -> float:
    """
    Measures wall-clock seconds (error bars will be computed over repeated runs).
    """
    t0 = time.perf_counter()
    subprocess.run(cmd, cwd=str(cwd) if cwd else None, check=True)
    t1 = time.perf_counter()
    return t1 - t0


@dataclass(frozen=True)
class Bench:
    label: str
    cwd: Path
    cmd: List[str]
    reset: Callable[[], None]
    warmup: Optional[Callable[[], None]] = None


def summarize(samples: List[float]) -> dict:
    """
    Returns mean/stddev and a 95% CI half-width (normal approx) for convenience.
    """
    n = len(samples)
    mean = statistics.mean(samples)
    stdev = statistics.stdev(samples) if n >= 2 else 0.0
    ci95 = 1.96 * (stdev / math.sqrt(n)) if n >= 2 else 0.0
    return {
        "n": n,
        "mean_s": mean,
        "stdev_s": stdev,
        "ci95_s": ci95,
        "min_s": min(samples),
        "max_s": max(samples),
    }


def run_bench(bench: Bench, repeats: int) -> dict:
    print(f"{YELLOW}[Running]{RESET} {bench.label}")
    print(f"Command: {' '.join(bench.cmd)}")
    samples: List[float] = []

    for i in range(1, repeats + 1):
        # Pre-conditions MUST be reset for each measured run
        if bench.reset is not None:
            bench.reset()
        # If the scenario requires a warmed state, do it AFTER reset, BEFORE measuring
        if bench.warmup is not None:
            bench.warmup()

        dt = timed_run(bench.cmd, cwd=bench.cwd)
        samples.append(dt)
        print(f"  run {i:>2}/{repeats}: {dt:.3f}s")

    stats = summarize(samples)
    print(
        f"  => mean {stats['mean_s']:.3f}s "
        f"± {stats['stdev_s']:.3f}s (stddev), "
        f"95% CI ± {stats['ci95_s']:.3f}s, "
        f"range [{stats['min_s']:.3f}, {stats['max_s']:.3f}]"
    )
    return {"label": bench.label, "command": bench.cmd, **stats}


def main() -> int:
    parser = argparse.ArgumentParser(description="Benchmark: Pants vs Grog with error bars.")
    parser.add_argument("--repeats", type=int, default=5, help="How many repetitions per benchmark.")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parent
    pants_dir = repo_root / "pants"

    # Common cache locations used in your original script
    pants_cache = Path.home() / ".cache" / "pants"
    pex_cache = Path.home() / ".pex"

    def reset_pants_cold_no_cache() -> None:
        # Equivalent intent: "No Daemon, No Cache" + ensure clean preconditions each time.
        rm_rf(pants_cache)

    def reset_pants_cached_no_daemon() -> None:
        # Start from a consistent base: wipe caches, then warmup will repopulate them.
        rm_rf(pants_cache)

    def warmup_pants_cache() -> None:
        # Not measured; ensures subsequent measured command sees populated caches.
        run(["pants", "package", "cli:docker"], cwd=pants_dir, quiet=False)

    def reset_uv_pex_cold() -> None:
        # Equivalent intent: uv cache clean + remove ~/.pex for each measured cold run.
        run(["uv", "cache", "clean", "--force"], cwd=repo_root)
        rm_rf(pex_cache)

    def reset_uv_pex_warm() -> None:
        # Warm case should still be "reset to known warm precondition":
        # clear caches then warmup by building once, then measure.
        run(["uv", "cache", "clean", "--force"], cwd=repo_root)
        rm_rf(pex_cache)

    def warmup_uv_pex() -> None:
        run(["bash", "./cli/build.sh"], cwd=repo_root, quiet=True)

    def reset_grog_image_build() -> None:
        # Keep it aligned with your original flow: clean uv/pex caches each time,
        # then warmup grog state before measuring image build.
        run(["uv", "cache", "clean", "--force"], cwd=repo_root)
        rm_rf(pex_cache)

    def warmup_grog_image() -> None:
        run(["grog", "build", "//cli:image"], cwd=repo_root, quiet=True)

    log_header("Starting Benchmark: Pants vs Grog (with error bars)")

    benches: List[Bench] = [
        Bench(
            label="Pants: Cold start (No Daemon, No Cache) - cli pex",
            cwd=pants_dir,
            cmd=["pants", "--no-pantsd", "--no-local-cache", "--no-remote-cache-read", "package", "cli:cli_bin"],
            reset=reset_pants_cold_no_cache,
            warmup=None,
        ),
        Bench(
            label="Pants: Cold start (No Daemon, With Cache) - cli pex",
            cwd=pants_dir,
            cmd=["pants", "--no-pantsd", "package", "cli:cli_bin"],
            reset=None,
            warmup=warmup_pants_cache,
        ),
        Bench(
            label="Pants: Warm start (With Daemon & Cache) - cli image",
            cwd=pants_dir,
            cmd=["pants", "package", "cli:docker"],
            reset=None,
            warmup=warmup_pants_cache,
        ),
        Bench(
            label="Uv/pex: Cold start (No Cache) - cli pex",
            cwd=repo_root,
            cmd=["bash", "./cli/build.sh"],
            reset=reset_uv_pex_cold,
            warmup=None,
        ),
        Bench(
            label="Uv/pex: Warm start (with uv caches) - cli pex",
            cwd=repo_root,
            cmd=["bash", "./cli/build.sh"],
            reset=reset_uv_pex_warm,
            warmup=warmup_uv_pex,
        ),
        Bench(
            label="Grog: Docker Image Build - cli image",
            cwd=repo_root,
            cmd=["grog", "build", "//cli:image"],
            reset=reset_grog_image_build,
            warmup=warmup_grog_image,
        ),
    ]

    results = []

    for b in tqdm(benches):
        log_header(b.label)
        results.append(run_bench(b, repeats=args.repeats))

    log_header("Summary (mean ± 95% CI)")
    for r in results:
        print(f"- {r['label']}")
        print(f"  mean: {r['mean_s']:.3f}s, 95% CI: ±{r['ci95_s']:.3f}s, n={r['n']}")

    log_header("Benchmark Complete")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
