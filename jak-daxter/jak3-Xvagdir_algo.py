#!/usr/bin/env python3
# Reimplemented from the function at  000A09B8  on the IOP
# of the  OVERLRD2.IRX  module in the PAL version of Jak 3

# Written by Edness   v1.0   2023-05-10

import argparse

CHARS = " ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-"

def c_int(entry):
    if entry.startswith("0x"):
        return int(entry[2:], 16)
    return int(entry, 10)

def enc_vagdir(name, int, stereo, parameter, offset):
    out_tmp = 0
    output = 0x0000000000000000
    name = name[:8].upper().ljust(8)
    for idx, char in enumerate(name):
        if idx == 4:
            output |= out_tmp << 21
            out_tmp = 0
        out_tmp *= len(CHARS)
        out_tmp += CHARS.index(char) if char in CHARS else CHARS[-1]

        # Below is more like how it's done in-game,
        # which has been significantly shortened here
        #tmp = 0x25
        #byte = char.to_bytes()
        #if byte.isalpha():
        #    #tmp = int.from_bytes(byte.upper()) - 0x40
        #elif byte.isdigit():
        #    tmp = char - 0x15
        #elif not char or byte == b" ":
        #    tmp = 0x0
        #elif char != b"-"
        # returns 0 at the end?
        #    tmp = 
        #out_tmp = 0x26 * out_tmp + tmp

    output |= out_tmp

    if offset & 0x7FFF:
        offset = (offset // 0x8000 + 1) * 0x8000
        print(f"Warning! Input offset has been aligned to 0x{offset:X}")
    offset >>= 15
    if parameter > 15: parameter = 15
    elif parameter < 0: parameter = 0

    output |= stereo << 42
    output |= int << 43
    output |= parameter << 44
    output |= offset << 48

    print(f"Compressed entry: 0x{output:016X}")

def dec_vagdir(int):
    #name = int & ((1 << 42) - 1)
    name_int = int & 0x3FFFFFFFFFF
    stereo = int >> 42 & 0x1
    int_wad = int >> 43 & 0x1
    parameter = int >> 44 & 0xF
    offset = (int >> 48) * 0x8000

    name = ""
    name_tmp = name_int & 0x1FFFFF
    for idx in range(8):
        if idx == 4:
            name_tmp = name_int >> 21
        name += CHARS[name_tmp % len(CHARS)]
        name_tmp //= len(CHARS)

    print(f"Filename: {name[::-1]}\nOffset: 0x{offset:X}\nSample rate(?): 0x{parameter:X}\nIs VAGWAD.INT: {bool(int_wad)}\nIs stereo: {bool(stereo)}")

parser = argparse.ArgumentParser(description="Converts to and from the Jak 3 and Jak X compressed VAGWAD entries")
subparsers = parser.add_subparsers()

decode_parser = subparsers.add_parser("dec", help="decompress entry")
decode_parser.add_argument("entry", type=c_int)
decode_parser.set_defaults(func=dec_vagdir)

encode_parser = subparsers.add_parser("enc", help="compress entry")
encode_parser.add_argument("name", type=str)
encode_parser.add_argument("-i", "--int", action="store_true", help="intended for VAGWAD.INT")
encode_parser.add_argument("-s", "--stereo", action="store_true", help="sound file is stereo")
encode_parser.add_argument("-p", "--parameter", type=c_int, default=0, help="additional parameter (0-15), likely audio sample rate")
encode_parser.add_argument("-o", "--offset", type=c_int, default=0, help="must be 0x8000 aligned")
encode_parser.set_defaults(func=enc_vagdir)

args = parser.parse_args()
try: args.func(args.entry) if "dec" in args.func.__name__ else args.func(args.name, args.int, args.stereo, args.parameter, args.offset)
except AttributeError: print("Error! No arguments given. Use -h or --help to show valid arguments.")
