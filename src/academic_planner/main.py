"""Command-line entry point for academic demand planning."""

import argparse
import json

from .config import RANDOM_SEED
from .database import export_pipeline


def main():
    parser = argparse.ArgumentParser(
        description="Academic demand forecasting and allocation."
    )

    parser.add_argument(
        "--scale",
        choices=["starter", "full"],
        default="starter",
    )

    parser.add_argument(
        "--seed",
        type=int,
        default=RANDOM_SEED,
    )

    parser.add_argument(
        "--output",
        default="data/output",
    )

    args = parser.parse_args()

    manifest = export_pipeline(
        scale=args.scale,
        output_dir=args.output,
        seed=args.seed,
    )

    print("\nPIPELINE COMPLETED")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()