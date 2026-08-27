"""Phase 0 smoke test — bukti env Python udah dipatenkan, bukan cuma direncanakan."""

import platform
import sys


def main() -> None:
    print("hello from career-hello")
    print(f"python   : {sys.version.split()[0]}")
    print(f"platform : {platform.system()} {platform.release()}")
    print(f"prefix   : {sys.prefix}")
