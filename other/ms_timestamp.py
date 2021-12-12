#!/usr/bin/env python3
# Python reimplementation of xbexexmzpe.bms with extra features
# Written by jason098 & Edness   2021-10-23 - 2021-12-11   v1.3

import argparse
from datetime import datetime

parser = argparse.ArgumentParser()
parser.add_argument("file", type=str)
args = parser.parse_args()

file = open(args.file, "rb") 
magic = file.read(0x2C)

def print_time(type):
    time = int.from_bytes(file.read(0x4), "big" if (type == "XEX") else "little")
    print(f"{type} date:".ljust(10), datetime.utcfromtimestamp(time).strftime("%Y-%m-%d %H:%M:%S"))

def scan_pdb(c_date):
    for page in range(pages):
        file.seek(page * page_size)
        if (int.from_bytes(file.read(0x4), "little") == c_date):
            print_time("PDB")
            break

def parse_pdb(word, c_date):
    global stream_ptr
    # Normally it's supposed to always be Stream 2, but a
    # few edge cases have arisen where this isn't the case
    # and instead it's stored in seemingly random streams.
    for _ in range(streams):
        file.seek(stream_dir + stream_ptr)
        file.seek(int.from_bytes(file.read(word), "little") * page_size)
        if (int.from_bytes(file.read(0x4), "little") == c_date):
            print_time("PDB")
            return
        stream_ptr += word
    print("Attempting fallback scan! This shouldn't ever happen!\nPlease contact jason098#9850 or Edness#2203 with this")
    scan_pdb(c_date)

if (magic[:2] == b"MZ"):
    file.seek(0x3C)
    file.seek(int.from_bytes(file.read(0x4), "little"))
    magic = str(file.read(0x2), "UTF-8")
    if (magic == "PE"):
        file.seek(0x6, 1)
        print_time("PE")
    else: # NE, LE, LX have no timestamp
        print(f"Unsupported MZ/{magic} file.")

elif (magic[:4] == b"XE\x00\x00"): # alpha
    file.seek(0x1C)
    print_time("XE")
    file.seek(0x24)
    file.seek(int.from_bytes(file.read(0x4), "little") + 0x3C)
    print_time("PE")

elif (magic[:4] == b"XBEH"): # final
    file.seek(0x114)
    print_time("XBE")
    cert_offs = int.from_bytes(file.read(0x2), "little")
    file.seek(0x148)
    print_time("PE")
    file.seek(cert_offs + 0x4)
    print_time("Cert")

elif (magic[:4] == b"XEX?" or magic[:4] == b"XEX0"): # alpha
    file.seek(0x103C)
    file.seek(int.from_bytes(file.read(0x4), "little") + 0x1008)
    print_time("PE")

elif (magic[:4] == b"XEX-" or magic[:4] == b"XEX1" or magic[:4] == b"XEX2"): # beta, final
    file.seek(0x14)
    sections = int.from_bytes(file.read(0x4), "big")
    for _ in range(sections):
        type = int.from_bytes(file.read(0x4), "big")
        offset = int.from_bytes(file.read(0x4), "big")
        if (type == 0x18002):
            file.seek(offset + 0x4)
            print_time("XEX")
            break

elif (magic == b"Microsoft C/C++ program database 2.00\r\n\x1AJG\x00\x00"):
    file.seek(0x2C)
    page_size = int.from_bytes(file.read(0x4), "little")
    file.seek(0x32)
    pages = int.from_bytes(file.read(0x2), "little")
    file.seek(0x3C)
    stream_dir = int.from_bytes(file.read(0x2), "little") * page_size
    file.seek(stream_dir)
    streams = int.from_bytes(file.read(0x2), "little")
    stream_ptr = streams * 8 + 4
    parse_pdb(0x2, 19970604)

elif (magic[:32] == b"Microsoft C/C++ MSF 7.00\r\n\x1ADS\x00\x00\x00"):
    file.seek(0x20)
    page_size = int.from_bytes(file.read(0x4), "little")
    file.seek(0x28)
    pages = int.from_bytes(file.read(0x4), "little")
    file.seek(0x34)
    file.seek(int.from_bytes(file.read(0x4), "little") * page_size)
    stream_dir = int.from_bytes(file.read(0x4), "little") * page_size
    file.seek(stream_dir)
    streams = int.from_bytes(file.read(0x4), "little")
    stream_ptr = streams * 4 + 4
    parse_pdb(0x4, 20000404)

else:
    print("Couldn't determine file type!")
