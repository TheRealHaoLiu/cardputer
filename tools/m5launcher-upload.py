#!/usr/bin/env python3
"""Upload firmware to M5Launcher SD card (/firmwares folder)."""

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


def curl(*args: str, check: bool = True) -> subprocess.CompletedProcess:
    """Run curl with common options."""
    cmd = ["curl", "-4", *args]
    return subprocess.run(cmd, check=check)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("file", nargs="?", help="Firmware file to upload")
    parser.add_argument("--url", default="http://launcher.local", help="M5Launcher URL")
    parser.add_argument("--user", default="admin", help="Username")
    parser.add_argument("--pass", dest="password", default="launcher", help="Password")
    args = parser.parse_args()

    # Find firmware file
    firmware = Path(args.file) if args.file else get_latest_firmware()

    if not firmware or not firmware.exists():
        print("Error: No firmware file found. Specify file or run 'poe firmware-download' first.")
        return 1

    cookie_file = "/tmp/m5launcher_cookies.txt"

    # Login
    print(f"Logging into M5Launcher at {args.url} ...")
    curl(
        "-c",
        cookie_file,
        f"{args.url}/login",
        "-X",
        "POST",
        "-H",
        "Content-Type: application/x-www-form-urlencoded",
        "-d",
        f"username={args.user}&password={args.password}",
        "--connect-timeout",
        "10",
        "-s",
        "-o",
        "/dev/null",
    )

    # Create folder
    print("Creating /firmwares folder (if needed)...")
    curl(
        "-b",
        cookie_file,
        f"{args.url}/file?name=/firmwares&action=create",
        "--connect-timeout",
        "5",
        "-s",
        "-o",
        "/dev/null",
        check=False,
    )

    # Upload
    print(f"Uploading {firmware} to /firmwares ...")
    curl(
        "-b",
        cookie_file,
        "-F",
        f"file=@{firmware}",
        "-F",
        "folder=/firmwares",
        f"{args.url}/",
        "--connect-timeout",
        "120",
        "-w",
        "HTTP %{http_code}\n",
    )

    print("Done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
