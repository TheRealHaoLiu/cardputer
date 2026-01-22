#!/usr/bin/env python3
"""Upload firmware to Cardputer via FTP (faster than M5Launcher web)."""

import argparse
import subprocess
import sys
from pathlib import Path


def get_latest_firmware() -> Path | None:
    """Find the most recently modified .bin file in firmware/."""
    firmware_dir = Path("firmware")
    if not firmware_dir.exists():
        return None
    bins = sorted(firmware_dir.glob("*.bin"), key=lambda p: p.stat().st_mtime, reverse=True)
    return bins[0] if bins else None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("file", nargs="?", help="Firmware file to upload")
    parser.add_argument("--host", default="192.168.68.71", help="FTP host")
    parser.add_argument("--path", default="/sd", help="Remote path")
    parser.add_argument("--user", default="", help="FTP username (optional)")
    parser.add_argument("--pass", dest="password", default="", help="FTP password (optional)")
    args = parser.parse_args()

    # Find firmware file
    firmware = Path(args.file) if args.file else get_latest_firmware()

    if not firmware or not firmware.exists():
        print("Error: No firmware file found. Specify file or run 'poe firmware-download' first.")
        return 1

    # Build FTP URL with optional auth
    if args.user:
        auth = f"{args.user}:{args.password}@" if args.password else f"{args.user}@"
        remote_url = f"ftp://{auth}{args.host}{args.path}/{firmware.name}"
    else:
        remote_url = f"ftp://{args.host}{args.path}/{firmware.name}"

    print(f"Uploading {firmware} to ftp://{args.host}{args.path}/ ...")
    result = subprocess.run(
        [
            "curl",
            "--ftp-port",
            "-",
            "-T",
            str(firmware),
            remote_url,
            "--connect-timeout",
            "30",
        ],
        check=False,
    )

    if result.returncode != 0:
        print(f"Error: Upload failed with code {result.returncode}")
        return result.returncode

    print("Done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
