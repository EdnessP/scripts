#!/usr/bin/env python3
# Python reimplementation of xbexexmzpe.bms
# Written by jason098   2021-10-23   v1.2

import argparse
from datetime import datetime

def print_time(type):
    timestamp = int.from_bytes(file.read(0x4), "big" if type == "XEX" else "little")
    print(datetime.utcfromtimestamp(timestamp).strftime(f"{type} date: %Y-%m-%d %H:%M:%S"))

parser = argparse.ArgumentParser()
parser.add_argument("file", type=str)
args = parser.parse_args()

file = open(args.file, "rb") 
magic = file.read(4)

if (magic[:2] == b"MZ"):
    file.seek(0x3C)
    file.seek(int.from_bytes(file.read(4), "little") + 0x8)
    print_time("PE")

elif (magic == b"XE\x00\x00"): # alpha
    file.seek(0x1C)
    print_time("XE")
    file.seek(0x74)
    print_time("PE")

elif (magic == b"XBEH"): # final
    file.seek(0x114)
    print_time("XBE")
    file.seek(0x148)
    print_time("PE")
    file.seek(0x188)
    print_time("Cert")

elif (magic == b"XEX?" or magic == b"XEX0"): # alpha
    file.seek(0x103C)
    file.seek(int.from_bytes(file.read(0x4), "little") + 0x1008)
    print_time("PE")

elif (magic == b"XEX-" or magic == b"XEX1" or magic == b"XEX2"): # beta, final
    file.seek(0x14)
    sections = int.from_bytes(file.read(4), "big")
    for _ in range(sections):
        type = int.from_bytes(file.read(4), "big")
        offset = int.from_bytes(file.read(4), "big")
        if (type == 0x18002):
            file.seek(offset + 0x4)
            print_time("XEX")
            break

else:
    print("Couldn't determine file type!")
