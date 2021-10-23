# Python reimplementation of xbexexmzpe.bms
# Written by jason098   2021-10-23   v1.0

import argparse
from datetime import datetime

parser = argparse.ArgumentParser()
parser.add_argument("file", type=str)
args = parser.parse_args()

file = open(args.file, "rb") 
magic = file.read(4)
if (magic[:2] == b'MZ'):
    file.seek(0x3C, 0)
    file.seek(int.from_bytes(file.read(4), "little") + 0x8, 0)
    timestamp = int.from_bytes(file.read(4), "little")
    print(datetime.utcfromtimestamp(timestamp).strftime('PE date: %Y-%m-%d %H:%M:%S'))
elif (magic == b'XE\x00\x00'):
    file.seek(0x1C, 0)
    timestamp = int.from_bytes(file.read(4), "little")
    file.seek(0x74, 0)
    timestamp2 = int.from_bytes(file.read(4), "little")
    print(datetime.utcfromtimestamp(timestamp).strftime('XE date: %Y-%m-%d %H:%M:%S'))
    print(datetime.utcfromtimestamp(timestamp2).strftime('PE date: %Y-%m-%d %H:%M:%S'))
elif (magic == b'XBEH'):
    file.seek(0x114, 0)
    timestamp = int.from_bytes(file.read(4), "little")
    file.seek(0x148, 0)
    timestamp2 = int.from_bytes(file.read(4), "little")
    file.seek(0x188, 0)
    timestamp3 = int.from_bytes(file.read(4), "little")
    print(datetime.utcfromtimestamp(timestamp).strftime('XBE date: %Y-%m-%d %H:%M:%S'))
    print(datetime.utcfromtimestamp(timestamp2).strftime('PE date: %Y-%m-%d %H:%M:%S'))
    print(datetime.utcfromtimestamp(timestamp3).strftime('Cert date: %Y-%m-%d %H:%M:%S'))
elif (magic == b'XEX?' or magic == b'XEX0'):
    file.seek(0x103C, 0)
    file.seek(int.from_bytes(file.read(4)) + 0x1008, 0)
    timestamp = int.from_bytes(file.read(4), "little")
    print(datetime.utcfromtimestamp(timestamp).strftime('PE date: %Y-%m-%d %H:%M:%S'))
elif (magic == b'XEX-' or magic == b'XEX1' or magic == b'XEX2'):
    file.seek(0x14, 0)
    sections = int.from_bytes(file.read(4), "big")
    for _ in range(sections):
        type = int.from_bytes(file.read(4), "big")
        offset = int.from_bytes(file.read(4), "big")
        if type == 0x18002:
            file.seek(offset + 0x4)
            timestamp = int.from_bytes(file.read(4), "big")
            print(datetime.utcfromtimestamp(timestamp).strftime('XEX/PE date: %Y-%m-%d %H:%M:%S'))
            break
