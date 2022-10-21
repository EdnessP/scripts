#!/usr/bin/env python3
# Exports and imports Midnight Club .STRTBL files
# Also works with other earlier Angel Studios / Rockstar: San Diego games

# Usage examples:
#   mclub_strtbl.py  -a 2  dec X:\path\to\file.strtbl
#   mclub_strtbl.py  -a 3  enc X:\path\to\file.txt
# 
# The output file is the same as the input, but with the
# appropriate extension appended at the end of the name.
# 
# Linebreaks must be written as \n (optionally \r\n)
# Tabs must be written as \t (if those are even used)
# 
# If a line starts with ", it must start with \" to 
# avoid Excel eating up the quotation marks.
# 
# The  -a | --algo  argument refers to the string hashing algorithm used;
# 2 = Midnight Club 2 (or other older games),  3 = Midnight Club 3

# Written by Edness   v1.2   2022-10-09 - 2022-10-21

import argparse, os, struct

def set_hash(algo):
    func = {
        2: hash2,
        3: hash3,
    }
    assert(algo in func)
    return func.get(algo)

def hash2(str):
    # Reimplemented from function at  003587E8  in
    #          Midnight Club 2 (PS2 PAL)          

    hash = 0x00000000
    for chr in str.encode():
        hash = (hash << 4) + chr
        if mask := hash & 0xF0000000:
            hash = hash ^ mask >> 24 ^ mask
    return hash

def hash3(str):
    # Reimplemented from function at  002BE788  in
    # Midnight Club 3: DUB Edition Remix (PS2 PAL)

    hash = 0x00000000
    for chr in str.encode():
        hash = (hash + chr) * 0x401 & 0xFFFFFFFF
        hash ^= hash >> 6
    hash = hash * 9 & 0xFFFFFFFF
    return (hash ^ hash >> 11) * 0x8001 & 0xFFFFFFFF

def parse_strtbl(path, algo):
    hash = set_hash(algo)

    def read_float():
        return struct.unpack("<f", file.read(0x4))[0]

    def read_int(bytes):
        return int.from_bytes(file.read(bytes), "little")

    def read_str(char_size, encoding):
        str_len = read_int(0x4)  # str_len doesn't include NULL terminator for labels
        return "".join(iter(lambda: file.read(char_size).decode(encoding), "\x00"))

    def read_font():
        return file.read(read_int(0x4)).decode()  # unlike read_str, this has no NULL terminator

    def fixup_str(str):
        str = str.replace("\n", r"\n").replace("\r", r"\r").replace("\t", r"\t")
        if str.startswith('"'): str = f"\\{str}"
        return str

    with open(path, "rb") as file:
        file_size = os.path.getsize(path)  #file.seek(0, 2)

        lang_ptrs = list()
        for i in range(read_int(0x4)):  # is it always 10 total?
            ptr = read_int(0x4)
            if ptr not in lang_ptrs and ptr != file_size:
                lang_ptrs.append(ptr)

        unknown = read_int(0x4)  # 512?
        labels = [read_str(0x1, "UTF-8") for x in range(read_int(0x4))]
        hashes = [hash(lab) for lab in labels]
        hash_dict = dict(zip(hashes, labels))

        str_dict = dict()
        for lab in labels: str_dict[lab] = list()

        for i in lang_ptrs:
            for j in range(read_int(0x4)):
                str_dict[hash_dict[read_int(0x4)]].append((
                    read_int(0x2),              # [0] param_text[0]
                    read_font(),                # [1] font_text
                    read_str(0x2, "UTF-16LE"),  # [2] lang_text
                    read_float(),               # [3] param_text[1]
                    read_float(),               # [4] param_text[2]
                    read_int(0x2)  # NULL?      # [5] param_text[3]
                ))

    output = list()
    output.append("\t".join((
        "String Label",
        "\t".join([f"Language {x}" for x in range(len(lang_ptrs))]),
        "\t".join([f"Font (Lang{x})" for x in range(len(lang_ptrs))]),
        "\t".join([f"Params (Lang{x})" for x in range(len(lang_ptrs))]),
    )))

    for label in str_dict:
        lang_text = list()
        font_text = list()
        param_text = list()
        for entry in str_dict.get(label):
            #lang_text.append(repr(fixup_str(entry[2]))[1:-1])
            lang_text.append(fixup_str(entry[2]))
            font_text.append(entry[1])
            param_text.append(",".join((
                str(entry[0]),
                str(entry[3]),
                str(entry[4]),
                str(entry[5]),
            )))

        output.append("\t".join((
            label,
            "\t".join(lang_text),
            "\t".join(font_text),
            "\t".join(param_text),
        )))

    with open(f"{path}.txt", "w", encoding="UTF-8") as file:
        file.write("\n".join(output))

    print(f"Output written to {os.path.abspath(path)}.txt")

def parse_txt(path, algo):
    hash = set_hash(algo)

    def write_float(float):
        return struct.pack("<f", float)

    def write_int(int, bytes):
        return int.to_bytes(bytes, "little")

    def fixup_str(str):
        str = str.replace(r"\n", "\n").replace(r"\r", "\r").replace(r"\t", "\t")
        if str.startswith(r'\"'): str = str[1:]
        return str  # .encode("raw-unicode-escape").decode("unicode-escape")

    with open(path, "r", encoding="UTF-8") as file:
        input = file.read().splitlines()

    header = input.pop(0).split("\t")

    if header[0].lower() != ("string label") or header[1].lower() != "language 0":
        print("Error! Not recognised as an exported .STRTBL from this script.")
        return

    if len(header[1:]) % 3 != 0:
        print("Error! Unequal amount of columns.")
        return
    lang_count = len(header[1:]) // 3

    # Every section starts with the amount of strings
    label_data = list(write_int(len(input), 0x4))
    lang_data = [list(write_int(len(input), 0x4)) for x in range(lang_count)]
    lang_data.extend([list() for x in range(9 - lang_count)])

    hash_dict = dict()
    for ln in sorted(input, key=str.lower):
        ln = ln.split("\t")
        label = ln.pop(0)
        label_hash = hash(label)
        if label_hash in hash_dict:
            print(f"Error! Hash collision detected! {hash_dict.get(label_hash)} = {label} = 0x{label_hash:08X}")
            return
        hash_dict[label_hash] = label

        label_data.extend(write_int(len(label), 0x4))
        label_data.extend(label.encode() + b"\x00")

        for col in range(lang_count):
            lang = ln[col::lang_count]
            lang[0] = fixup_str(lang[0])
            lang[2] = lang[2].split(",")

            lang_data[col].extend(write_int(hash(label), 0x4))
            lang_data[col].extend(write_int(int(lang[2][0]), 0x2))
            lang_data[col].extend(write_int(len(lang[1]), 0x4))
            lang_data[col].extend(lang[1].encode())
            lang_data[col].extend(write_int(len(lang[0]) + 1, 0x4))
            lang_data[col].extend(lang[0].encode("UTF-16LE"))
            lang_data[col].extend(bytes(2))  # NULL terminator
            lang_data[col].extend(write_float(float(lang[2][1])))  # Always 1.0?
            lang_data[col].extend(write_float(float(lang[2][2])))
            lang_data[col].extend(write_int(int(lang[2][3]), 0x2))  # NULL?

    pointers = [0x30 + len(label_data)]
    for lang in lang_data:
        pointers.append(pointers[-1] + len(lang))

    with open(f"{path}.strtbl", "wb") as file:
        file.write(b"".join((
            write_int(10, 0x4),
            b"".join([write_int(ptr, 0x4) for ptr in pointers]),
            write_int(512, 0x4),
            bytes(label_data),
            bytes(sum(lang_data, list())),
        )))

    print(f"Output written to {os.path.abspath(path)}.strtbl")

this = os.path.basename(__file__)

parser = argparse.ArgumentParser(description="Converts to and from the .STRTBL string tables used in Midnight Club.")
subparsers = parser.add_subparsers()

decode_parser = subparsers.add_parser("dec", help="decode from a .STRTBL file")
decode_parser.add_argument("path", type=str)
decode_parser.set_defaults(func=parse_strtbl)

encode_parser = subparsers.add_parser("enc", help="encode to a .STRTBL file")
encode_parser.add_argument("path", type=str)
encode_parser.set_defaults(func=parse_txt)

parser.add_argument("-a", "--algo", type=int, help="{2,3} hashing algorithm; Midnight Club 2 (or other older titles), or Midnight Club 3")

args = parser.parse_args()
try: args.func(args.path, args.algo)
except AttributeError: print("Error! No arguments given. Use -h or --help to show valid arguments.")
except AssertionError: print("Error! No hashing algorithm provided. Use -h or --help for additional information.")
except KeyError: print("Error! Hashed string did not match expected result. Try a different hashing algorithm.")
