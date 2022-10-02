#!/usr/bin/env python3
# The Simpsons Game NewGen .LH2 parser

# Usage:
#   script.py dec "string_file.LH2"
#   script.py enc "string_file.LH2.txt"

# All the strings must be compatible with Windows Codepage 1252!

# Written by Edness   v1.0
# 2022-05-30

import argparse, os

def parse_lh(path):
    def read_int():
        return int.from_bytes(file.read(0x4), "big")

    def read_str():
        return "".join(iter(lambda: file.read(0x1).decode("1252"), "\x00"))

    with open(path, "rb") as file:
        if file.read(0x4) != b"2HCL":
            print("Not a valid .LH2 file!")
            return
        if read_int() != os.path.getsize(path):
            print("File size check failed!")
            return

        file.seek(0x10)
        entries = read_int()
        tables = read_int()
        # Next two values are pointers to the hashed string ID list
        # and the table pointer lists, but only when loaded in RAM.
        # Otherwise these two fields are blank.

        file.seek(0x20)
        ids = [read_int() for x in range(entries)]
        ptr = [list() for x in range(tables)]
        for lst in ptr:
            lst.extend([read_int() for x in range(entries)])

        txt = [list() for x in range(tables)]
        for i, lst in enumerate(ptr):
            for ofs in lst:
                file.seek(ofs)
                txt[i].append(read_str())

    with open(f"{path}.txt", "w", encoding="UTF-8") as file:
        columns = tables - 1 if tables > 1 else tables
        file.write("String ID\t"
                + ("String Label\t" if tables > 1 else "") 
                +  "\t".join([f"Language {x}" for x in range(columns)]))

        for i, id in enumerate(ids):
            file.write(f"\n{id:08X}\t"
                    + (f"{txt[-1][i]}\t" if tables > 1 else "")
                    +  "\t".join([txt[x][i] for x in range(columns)]))

    print(f"Output written to {path}.txt")

def parse_txt(path):
    def write_int(int):
        return int.to_bytes(0x4, "big")

    with open(path, "r", encoding="UTF-8") as file:
        txt = file.read().splitlines()

    # Todo: validate string hash IDs with the hashing algorithm
    # https://github.com/EdnessP/scripts/blob/main/tsg/tsg_hash.py

    hdr = txt[0].split("\t")
    if hdr[0] != "String ID" or hdr[1] not in {"String Label", "Language 0"}:
        print("Not recognised as an .LH2 file exported by this script.")
        return

    txt.pop(0)
    tables = len(hdr) - 1
    entries = len(txt)

    ids = list()
    data = [list() for x in range(tables)]
    txt_ofs = 32 + (entries + tables * entries) * 4

    label = True if hdr[1] == "String Label" else False
    for ln in txt:
        ln = ln.split("\t")
        ids.extend(write_int(int(ln[0], 16)))

        ln.pop(0)
        if label: ln.append(ln.pop(0))
        for i, s in enumerate(ln):
            data[i].append(s.encode("1252") + b"\x00")

    ptr = [txt_ofs]
    for lst in data:
        for ln in lst:
            ptr.append(ptr[-1] + len(ln))
    file_size = ptr.pop()

    with open(f"{path}.LH2", "wb") as file:
        file.write(b"2HCL"
                 + write_int(file_size)
                 + write_int(0x1)
                 + bytes(0x4)
                 + write_int(entries)
                 + write_int(tables)
                 + bytes(0x8)
                 + bytes(ids)
                 + b"".join([write_int(x) for x in ptr])
                 + b"".join(sum(data, [])))

    print(f"Output written to {path}.LH2")

parser = argparse.ArgumentParser(description="Converts to and from the 2HCL string table used in The Simpsons Game (PS3, X360).")
subparsers = parser.add_subparsers()

decode_parser = subparsers.add_parser("dec", help="Decode from a file.")
decode_parser.add_argument("path", type=str)
decode_parser.set_defaults(func=parse_lh)

encode_parser = subparsers.add_parser("enc", help="Encode to a file.")
encode_parser.add_argument("path", type=str)
encode_parser.set_defaults(func=parse_txt)

args = parser.parse_args()
args.func(args.path)
