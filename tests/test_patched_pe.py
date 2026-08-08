#!/usr/bin/env python3
"""Static checks for binaries produced by tools/patch_hybrid_binaries.py."""
from __future__ import annotations

import argparse
import hashlib
import struct
from pathlib import Path

EXPECTED = {
    "x86": "597325ad1ef1d19a90c317a86789282ec3f400a5fb77ebea0ba7b524f5a97307",
    "x64": "bca02c5400a753ebce3924515d74160140c16650369c76d60af47feeae8641b9",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def machine(path: Path) -> int:
    data = path.read_bytes()
    pe = struct.unpack_from("<I", data, 0x3C)[0]
    assert data[pe:pe + 4] == b"PE\0\0"
    return struct.unpack_from("<H", data, pe + 4)[0]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--x86", type=Path, required=True)
    ap.add_argument("--x64", type=Path, required=True)
    args = ap.parse_args()
    assert sha(args.x86) == EXPECTED["x86"]
    assert sha(args.x64) == EXPECTED["x64"]
    assert machine(args.x86) == 0x014C
    assert machine(args.x64) == 0x8664
    print("patched PE tests: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
