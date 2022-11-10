#!/usr/bin/env python3
# Python reimplementation of  xbexexmzpe.bms  with extra features
# Written by jason098 & Edness   2021-10-23 - 2022-11-10   v1.5.4
# Original base script written on 2021-03-17

import argparse, os
from datetime import datetime

parser = argparse.ArgumentParser()
parser.add_argument("file", type=str)
args = parser.parse_args()

file = open(args.file, "rb")
magic = file.read(0x208)
endian = "little"
time_t = True

def magic_int(bytes):
    return int.from_bytes(magic[:bytes], endian)

def read_int(bytes):
    return int.from_bytes(file.read(bytes), endian)

def read_str(bytes):
    return str(file.read(bytes), "UTF-8")

def print_time(type):
    time = (read_int(0x4), 0) if (time_t) else divmod(read_int(0x8) - 0x19DB1DED53E8000, 10000000)
    time = datetime.utcfromtimestamp(time[0]).replace(microsecond=time[1] // 10)
    print(f"{type} date:".ljust(10), time.strftime(f"%Y-%m-%d %H:%M:%S{'' if (time_t) else '.%f'}"))

def parse_pdb(word, *c_dates):
    # Normally it's supposed to always be Stream 2, but a few edge cases have arisen
    # where this isn't the case and instead it's stored in seemingly random streams.
    # And there's still other known issues with few PDBs pointing to a faked stream
    # timestamp with the real stream being elsewhere and never directly pointed to.
    if (streams < pages and streams != 0 and stream_dir < pages * page_size and
        stream_dir != 0 and os.path.getsize(args.file) == pages * page_size):
        global stream_ptr
        while True:
            file.seek(stream_ptr)
            stream = read_int(word)
            if (stream == 0 or stream > pages):
                break
            file.seek(stream * page_size)
            if (read_int(0x4) in c_dates):
                print_time("PDB")
                return
            stream_ptr += word
    print("Info: Something went wrong! Attempting fallback scan...")
    for page in range(pages):
        file.seek(page * page_size)
        if (read_int(0x4) in c_dates):
            print_time("PDB")
            break

if (magic[:0x2] == b"MZ"):
    file.seek(0x3C)
    file.seek(read_int(0x4))
    magic = read_str(0x2)
    if (magic == "PE"):
        file.seek(0x6, 1)
        print_time(magic)
    else:  # NE, LE, LX have no timestamp.
        print(f"Unsupported {magic} file.")

elif (magic[:0x4] == b"XE\x00\x00"):  # Xbox (Alpha)
    file.seek(0x1C)
    print_time("XE")
    file.seek(0x24)
    file.seek(read_int(0x4) + 0x3C)
    print_time("PE")

elif (magic[:0x4] == b"XBEH"):  # Xbox (Final)
    file.seek(0x114)
    print_time("XBE")
    file.seek(read_int(0x2) + 0x4)
    print_time("Cert")
    file.seek(0x148)
    print_time("PE")

elif (magic[:0x4] in {b"XEX?", b"XEX0"}):  # Xbox 360 (Alpha)
    file.seek(0x103C)
    file.seek(read_int(0x4) + 0x1008)
    print_time("PE")

elif (magic[:0x4] in {b"XEX-", b"XEX%", b"XEX1", b"XEX2"}):  # Xbox 360 (Beta, Final)
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

elif (magic[0x200:0x208] == b"msft-xvd"):  # Xbox One
    time_t = False
    file.seek(0x210)
    print_time("XVD")

elif (magic_int(0x8) == 1 or magic_int(0x10) == 2):  # Xbox, Xbox 360 DMI
    time_t = False
    file.seek(0x10)
    print_time("DMI")

elif (magic[:0x4] in {b"\xD1\x0F\x31\x10", b"\xE1\x0F\x31\x10"}):  # Xbox, Xbox 360 SS
    time_t = False
    file.seek(0x49F)
    print_time("Authoring")
    file.seek(0x5DF)
    print_time("Mastering")
    if magic[:0x4] == b"\xD1\x0F\x31\x10":  # Xbox only
        file.seek(0x41F)
        print_time("Creation(?)")
        time_t = True
        file.seek(0x4A7)
        print_time("Certificate")

elif (magic[:0x2] == b"DI"):  # DBG - PDB predecessor?
    file.seek(0x8)
    print_time("DI")

elif (magic[:0x2C] == b"Microsoft C/C++ program database 2.00\r\n\x1AJG\x00\x00"):
    file.seek(0x2C)
    page_size = read_int(0x4)
    file.seek(0x32)
    pages = read_int(0x2)
    file.seek(0x3C)
    stream_dir = read_int(0x2) * page_size
    file.seek(stream_dir)
    streams = read_int(0x2)
    stream_ptr = streams * 8 + 4 + stream_dir
    parse_pdb(0x2, 19950814, 19960307, 19970604)

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
    stream_ptr = streams * 4 + 4 + stream_dir
    parse_pdb(0x4, 20000404)

elif (magic[:0x20] == b"Microsoft Linker Database\n\n\x07\x1A\x00\x00\x00"):
    # There are both FILETIME and TIME_T timestamps, as well as PDB dates?
    time_t = False
    file.seek(0x26)
    file.seek(read_int(0x2) - 0x12, 1)
    print_time("ILK")

else:
    print("Couldn't determine file type!")

file.close()
