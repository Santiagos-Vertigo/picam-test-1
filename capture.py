#!/usr/bin/env python3
import argparse
from pathlib import Path

from camera import STORAGE_DIR, capture_images


def main():
    parser = argparse.ArgumentParser(description="Capture JPEG images from the Raspberry Pi camera.")
    parser.add_argument("--count", type=int, default=1, help="number of images to capture (default: 1)")
    parser.add_argument(
        "--delay",
        type=float,
        default=2,
        help="seconds between captures (default: 2)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=STORAGE_DIR,
        help="output directory (default: storage/images)",
    )
    args = parser.parse_args()

    if args.count < 1:
        parser.error("--count must be at least 1")
    if args.delay < 0:
        parser.error("--delay cannot be negative")

    for output_path in capture_images(args.count, args.delay, args.output):
        print(output_path)


if __name__ == "__main__":
    main()
