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

def parse_pdb(page_size, pages, date):
    for page in range(pages):
        file.seek(page * page_size)
        c_date = int.from_bytes(file.read(0x4), "little")
        if (c_date == date):
            print_time("PDB")
            break

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
    file.seek(0x74)
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
    stream2_ptr = streams * 4 + 8
    file.seek(stream_dir + stream2_ptr)
    file.seek(int.from_bytes(file.read(0x4), "little") * page_size)
    c_date = int.from_bytes(file.read(0x4), "little")
    if (c_date == 20000404):
        print_time("PDB")
    else: # Fallback
        parse_pdb(page_size, pages, 20000404)

elif (magic == b"Microsoft C/C++ program database 2.00\r\n\x1AJG\x00\x00"):
    page_size = int.from_bytes(file.read(0x4), "little")
    file.seek(0x2, 1)
    pages = int.from_bytes(file.read(0x2), "little")
    parse_pdb(page_size, pages, 19970604)

else:
    print("Couldn't determine file type!")
