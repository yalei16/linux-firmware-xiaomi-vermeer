#!/usr/bin/env python3
"""打印 ath12k board-2.bin 里所有 BDF 条目名，并检查是否含目标设备条目。

用法: python3 check-board2.py <board-2.bin> [subsystem-device]
"""
import re
import sys


def names(data):
    return sorted({m.group(0).split(b"\x00")[0].decode("latin1")
                   for m in re.finditer(rb"bus=pci[ -~]{20,200}", data)})


def main():
    path = sys.argv[1]
    want_sd = sys.argv[2] if len(sys.argv) > 2 else "1107"
    data = open(path, "rb").read()
    magic = data[:8]
    print(f"file={path} size={len(data)} magic={magic!r}")
    found = names(data)
    if not found:
        print("ERROR: 没有找到任何 bus=pci,... 条目")
        return 1
    ok = False
    for n in found:
        hit = f"subsystem-device={want_sd}," in n
        ok = ok or hit
        print(("  OK   " if hit else "  miss ") + n)
    print("RESULT:", "MATCH" if ok else "NO_MATCH")
    return 0 if ok else 2


if __name__ == "__main__":
    sys.exit(main())
