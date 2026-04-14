#!/usr/bin/env python3
"""
One-command local launcher for PC-NEST.

Examples:
  python run_site.py
  python run_site.py --sqlite
  python run_site.py --db-engine postgresql --host 0.0.0.0 --port 8000
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys


def run_manage(py: str, args: list[str], env: dict[str, str]) -> None:
    cmd = [py, "manage.py", *args]
    print(f"[run_site] {' '.join(cmd)}")
    subprocess.run(cmd, check=True, env=env)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run PC-NEST quickly.")
    parser.add_argument("--host", default="127.0.0.1", help="Django host (default: 127.0.0.1)")
    parser.add_argument("--port", default="8000", help="Django port (default: 8000)")
    parser.add_argument(
        "--db-engine",
        choices=["sqlite", "postgresql"],
        default=None,
        help="Override DB_ENGINE for this run.",
    )
    parser.add_argument(
        "--sqlite",
        action="store_true",
        help="Shortcut for --db-engine sqlite.",
    )
    parser.add_argument(
        "--no-migrate",
        action="store_true",
        help="Skip migrations before starting server.",
    )
    parser.add_argument(
        "--seed-demo",
        action="store_true",
        help="Run `python manage.py seed_demo_data` before server start.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    env = os.environ.copy()
    env.setdefault("DEBUG", "True")

    if args.sqlite:
        env["DB_ENGINE"] = "sqlite"
    elif args.db_engine:
        env["DB_ENGINE"] = args.db_engine

    python_bin = sys.executable

    try:
        run_manage(python_bin, ["check"], env)
        if not args.no_migrate:
            run_manage(python_bin, ["migrate"], env)
        if args.seed_demo:
            run_manage(python_bin, ["seed_demo_data"], env)
        run_manage(python_bin, ["runserver", f"{args.host}:{args.port}"], env)
    except subprocess.CalledProcessError as exc:
        print(f"[run_site] command failed with exit code {exc.returncode}")
        return exc.returncode
    except KeyboardInterrupt:
        print("\n[run_site] stopped.")
        return 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
