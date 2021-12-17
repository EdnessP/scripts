#!/usr/bin/env python3
# Python reimplementation of xbexexmzpe.bms with extra features
# Written by jason098 & Edness   2021-10-23 - 2021-12-17   v1.4

import argparse, os
from datetime import datetime

parser = argparse.ArgumentParser()
parser.add_argument("file", type=str)
args = parser.parse_args()

file = open(args.file, "rb")
magic = file.read(0x208)
endian = "little"

def read_int(bytes):
    return int.from_bytes(file.read(bytes), endian)

def print_time(type):
    time = divmod(read_int(0x8) - 0x19DB1DED53E8000, 10000000)[0] if (type == "XVD") else read_int(0x4)
    print(f"{type} date:".ljust(10), datetime.utcfromtimestamp(time).strftime("%Y-%m-%d %H:%M:%S"))

def parse_pdb(word, c_date):
    # Normally it's supposed to always be Stream 2, but a few edge cases have arisen
    # where this isn't the case and instead it's stored in seemingly random streams.
    if (streams < pages and streams != 0 and stream_dir < pages * page_size and
        stream_dir != 0 and os.path.getsize(args.file) == pages * page_size):
        global stream_ptr
        for _ in range(streams):
            file.seek(stream_dir + stream_ptr)
            stream = read_int(word)
            if (stream == 0 or stream > pages):
                break
            file.seek(stream * page_size)
            if (read_int(0x4) == c_date):
                print_time("PDB")
                return
            stream_ptr += word
    print("Info: PDB integrity check failed! Attempting fallback scan...")
    for page in range(pages):
        file.seek(page * page_size)
        if (read_int(0x4) == c_date):
            print_time("PDB")
            break

if (magic[:0x2] == b"MZ"):
    file.seek(0x3C)
    file.seek(read_int(0x4))
    magic = str(file.read(0x2), "UTF-8")
    if (magic == "PE"):
        file.seek(0x6, 1)
        print_time(magic)
    else: # NE, LE, LX have no timestamp
        print(f"Unsupported {magic} file.")

elif (magic[:0x4] == b"XE\x00\x00"): # alpha
    file.seek(0x1C)
    print_time("XE")
    file.seek(0x24)
    file.seek(read_int(0x4) + 0x3C)
    print_time("PE")

elif (magic[:0x4] == b"XBEH"): # final
    file.seek(0x114)
    print_time("XBE")
    file.seek(0x148)
    print_time("PE")
    file.seek(0x118)
    file.seek(read_int(0x2) + 0x4)
    print_time("Cert")

elif (magic[:0x4] == b"XEX?" or magic[:0x4] == b"XEX0"): # alpha
    file.seek(0x103C)
    file.seek(read_int(0x4) + 0x1008)
    print_time("PE")

elif (magic[:0x4] == b"XEX-" or magic[:0x4] == b"XEX1" or magic[:0x4] == b"XEX2"): # beta, final
    endian = "big"
    file.seek(0x14)
    sections = read_int(0x4)
    for _ in range(sections):
        type = read_int(0x4)
        offset = read_int(0x4)
        if (type == 0x18002):
            file.seek(offset + 0x4)
            print_time("XEX")
            break

elif (magic[0x200:0x208] == b"msft-xvd"):
    file.seek(0x210)
    print_time("XVD")

elif (magic[:0x2C] == b"Microsoft C/C++ program database 2.00\r\n\x1AJG\x00\x00"):
    file.seek(0x2C)
    page_size = read_int(0x4)
    file.seek(0x32)
    pages = read_int(0x2)
    file.seek(0x3C)
    stream_dir = read_int(0x2) * page_size
    file.seek(stream_dir)
    streams = read_int(0x2)
    stream_ptr = streams * 8 + 4
    parse_pdb(0x2, 19970604)

elif (magic[:0x20] == b"Microsoft C/C++ MSF 7.00\r\n\x1ADS\x00\x00\x00"):
    file.seek(0x20)
    page_size = read_int(0x4)
    file.seek(0x28)
    pages = read_int(0x4)
    file.seek(0x34)
    file.seek(read_int(0x4) * page_size)
    stream_dir = read_int(0x4) * page_size
    file.seek(stream_dir)
    streams = read_int(0x4)
    stream_ptr = streams * 4 + 4
    parse_pdb(0x4, 20000404)

else:
    print("Couldn't determine file type!")
