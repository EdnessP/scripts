#!/usr/bin/env python3
# Python reimplementation of xbexexmzpe.bms
# Written by jason098   2021-10-23   v1.1

import argparse
from datetime import datetime

def print_time(name, time):
    print(datetime.utcfromtimestamp(time).strftime(f"{name} date: %Y-%m-%d %H:%M:%S"))

parser = argparse.ArgumentParser()
parser.add_argument("file", type=str)
args = parser.parse_args()

file = open(args.file, "rb") 
magic = file.read(4)
if (magic[:2] == b"MZ"):
    file.seek(0x3C, 0)
    file.seek(int.from_bytes(file.read(4), "little") + 0x8, 0)
    print_time("PE", int.from_bytes(file.read(4), "little"))

elif (magic == b"XE\x00\x00"):
    file.seek(0x1C, 0)
    print_time("XE", int.from_bytes(file.read(4), "little"))
    file.seek(0x74, 0)
    print_time("PE", int.from_bytes(file.read(4), "little"))

elif (magic == b"XBEH"):
    file.seek(0x114, 0)
    print_time("XBE", int.from_bytes(file.read(4), "little"))
    file.seek(0x148, 0)
    print_time("PE", int.from_bytes(file.read(4), "little"))
    file.seek(0x188, 0)
    print_time("Cert", int.from_bytes(file.read(4), "little"))

elif (magic == b"XEX?" or magic == b"XEX0"):
    file.seek(0x103C, 0)
    file.seek(int.from_bytes(file.read(4)) + 0x1008, 0)
    print_time("PE", int.from_bytes(file.read(4), "little"))

elif (magic == b"XEX-" or magic == b"XEX1" or magic == b"XEX2"):
    file.seek(0x14, 0)
    sections = int.from_bytes(file.read(4), "big")
    for _ in range(sections):
        type = int.from_bytes(file.read(4), "big")
        offset = int.from_bytes(file.read(4), "big")
        if type == 0x18002:
            file.seek(offset + 0x4)
            print_time("XEX/PE", int.from_bytes(file.read(4), "big"))
            break

else:
    print("Couldn't determine file type")
