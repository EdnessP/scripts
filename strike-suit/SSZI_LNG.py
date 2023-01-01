#!/usr/bin/env python3
# Strike Suit Zero / Infinity .LNG importer and exporter

# Usage examples:
#   SSZI_LNG.py dec X:\path\to\file.lng
#   SSZI_LNG.py enc X:\path\to\file.txt

# Linebreaks must be written as \n (optionally \r\n)
# Tabs must be written as \t (if those are even used)

# If a line starts with ", it must start with \" to 
# avoid Excel eating up the quotation marks.

# Written by Edness   v1.0   2023-01-01

import argparse, os

def parse_lng(path):
    def read_int():
        return int.from_bytes(file.read(0x4), "little")

    def read_str():
        return b"".join(iter(lambda: file.read(0x1), b"\x00")).decode("UTF-8")

    with open(path, "rb") as file:
        strings = read_int()
        if file.read(0x4) != b"XII2":
            print("Error! Not recognised as a valid .LNG file.")
            return
        hashes = [read_int() for x in range(strings)]
        strings = [read_str() for x in range(strings)]

    path = os.path.splitext(path)[0] + ".txt"
    with open(path, "w", encoding="UTF-8") as file:
        output = ["String ID\tString"]
        for hash, str in zip(hashes, strings):
            if str.startswith('"'): str = f"\\{str}"
            str = str.replace("\n", r"\n").replace("\r", r"\r").replace("\t", r"\t")
            output.append(f"{hash:08X}\t{str}")
        file.write("\n".join(output))
        print("Output written to", path)

def parse_txt(path):
    def write_int(int):
        return int.to_bytes(0x4, "little")

    def write_str(str):
        if str.startswith(r'\"'): str = str[1:]
        return str.replace(r"\n", "\n").replace(r"\r", "\r").replace(r"\t", "\t").encode()

    with open(path, "r", encoding="UTF-8") as file:
        input = file.read().splitlines()

    if input.pop(0) != "String ID\tString":
        print("Error! Not recognised as an exported .LNG from this script.")
        return

    hashes = list()
    strings = list()
    for ln in sorted(input):
        ln = ln.split("\t")
        hashes.append(write_int(int(ln[0], 16)))
        strings.extend((write_str(ln[1]), b"\x00"))

    path = os.path.splitext(path)[0] + ".lng"
    with open(path, "wb") as file:
        file.write(b"".join((
            write_int(len(input)),
            b"XII2",
            b"".join(hashes),
            b"".join(strings),
        )))
        print("Output written to", path)

parser = argparse.ArgumentParser(description="Converts to and from the .LNG files used in Strike Suit Zero / Infinity.")
subparsers = parser.add_subparsers()

decode_parser = subparsers.add_parser("dec", help="decode from a .LNG file")
decode_parser.add_argument("path", type=str)
decode_parser.set_defaults(func=parse_lng)

encode_parser = subparsers.add_parser("enc", help="encode to a .LNG file")
encode_parser.add_argument("path", type=str)
encode_parser.set_defaults(func=parse_txt)

args = parser.parse_args()
try: args.func(args.path)
except AttributeError: print("Error! No arguments given. Use -h or --help to show valid arguments.")
