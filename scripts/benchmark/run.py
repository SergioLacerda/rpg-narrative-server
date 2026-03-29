import argparse
import asyncio
import sys
from pathlib import Path

from scripts.benchmark.engine_factory import create_engine
from scripts.benchmark.metrics import print_report
from scripts.benchmark.scenarios import run_concurrent

ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT))


async def compare(args):
    for mode in ["io", "jitter", "cpu"]:
        print(f"\n===== MODE: {mode.upper()} =====")

        engine = create_engine(
            mode=mode,
            batch=args.batch,
            cpu_work=args.cpu_work,
            workers=args.workers,
        )

        report = await run_concurrent(
            engine,
            n=args.n,
            same_query=not args.no_dedup,
        )

        print_report(report)


async def main(args):
    if args.compare:
        await compare(args)
        return

    engine = create_engine(
        mode=args.mode,
        batch=args.batch,
        cpu_work=args.cpu_work,
        workers=args.workers,
    )

    report = await run_concurrent(
        engine,
        n=args.n,
        same_query=not args.no_dedup,
    )

    print_report(report)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--n", type=int, default=50)
    parser.add_argument("--mode", choices=["io", "cpu", "jitter"], default="io")
    parser.add_argument("--compare", action="store_true")

    parser.add_argument("--no-dedup", action="store_true")
    parser.add_argument("--batch", action="store_true")

    parser.add_argument("--workers", type=int, default=None)
    parser.add_argument("--cpu-work", type=int, default=2_000_000)

    args = parser.parse_args()

    asyncio.run(main(args))
