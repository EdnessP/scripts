#!/usr/bin/env python3
# Export and import Bully (Canis Canem Edit) text containers

# Usage:
#   Extract:  X
#       string_bin.py  X  "/path/to/strings.bin"
#     Optional:
#       -o  | --output    <str> Path to the output file;  default is in the input folder
#         string_bin.py  X  "X:\path\to\strings.bin"  -o "Y:\path\to\strings.json"
#
#   Rebuild:  B
#       string_bin.py  B  "Y:\path\to\strings.json"
#     Optional:
#       -o  | --output    <str> Path to the output file;  default is in the input folder
#       -be | --bigendian       Build in big endian (Wii, Xbox 360)
#         string_bin.py  B  "/path/to/strings.json"  -o "/path/to/new.bin"  -be

# Written by Edness   2024-06-20   v1.0.1

import json, os

def parse_bin(path, outpath=str()):
    def read_int():
        return int.from_bytes(file.read(0x4), endian)

    def read_str():
        return b"".join(iter(lambda: file.read(0x1), b"\x00")).decode("UTF-8")

    path = os.path.abspath(path)
    if not outpath:
        outpath = os.path.splitext(path)[0] + ".json"
    outpath = os.path.abspath(outpath)

    output = dict()
    with open(path, "rb") as file:
        header = file.read(0x4)
        check = b"\xAB\xCD\x12\x34"
        assert header in {check, check[::-1]}, ERR_HEADER
        endian = "big" if header == check else "little"
        assert read_int() == 0x1, ERR_HEADER  # version?
        assert read_int() == 0x0, ERR_HEADER  # padding?

        text_size = read_int()
        meta_size = read_int()
        entries = read_int()

        assert meta_size == entries * 0x8, ERR_HEADER
        assert read_int() == 0x2, ERR_HEADER  # version?
        assert read_int() == 0x0, ERR_HEADER  # padding?
        assert file.read(0x8) == b"BD" + bytes(0x6), ERR_HEADER

        text_offs = 0x28
        meta_offs = text_offs + text_size

        for i in range(entries):
            file.seek(meta_offs + i * 0x8)
            str_hash = read_int()
            str_offs = read_int() - 1
            file.seek(text_offs + str_offs)
            assert file.read(0x2) == b"\xFF\xFF", ERR_HEADER
            string = read_str()
            key = f"0x{str_hash:08X}"
            if key in output and output[key] != string:  # rare, but seen
                print(WARN_COLL.format(str_hash, output[key], string))
            else:
                output[key] = string
            # TODO: unhashed map from AE's XMLs?

    with open(outpath, "w", encoding="UTF-8") as file:
        json.dump(output, file, indent=0, sort_keys=True, ensure_ascii=False)

    print("Done! Output written to", outpath)

def build_bin(path, outpath=str(), big_endian=False):
    def write_int(int):
        return file.write(int.to_bytes(0x4, endian))

    def write_str(str):
        return file.write(b"\xFF\xFF" + str.encode("UTF-8") + b"\x00")

    path = os.path.abspath(path)
    if not outpath:
        outpath = os.path.splitext(path)[0] + ".bin"
    outpath = os.path.abspath(outpath)

    with open(path, "r", encoding="UTF-8") as file:
        input = json.load(file)
    input = dict(sorted((int(hash, 16), input[hash]) for hash in input))
    #input = dict(sorted(input.items()))

    str_offs = [1]
    text_offs = 0x28
    endian = "big" if big_endian else "little"
    with open(outpath, "wb") as file:
        file.seek(text_offs)
        for hash in input:
            offs = write_str(input[hash])
            if offs & 0x3:
                offs += 0x4 - offs & 0x3
            str_offs.append(str_offs[-1] + offs)
            file.seek(text_offs + str_offs[-1] - 1)

        for hash, offs in zip(input, str_offs):
            write_int(hash)
            write_int(offs)

        file.seek(0x0)
        # write header last
        write_int(0xABCD1234)
        write_int(0x1)
        write_int(0x0)
        write_int(str_offs[-1] - 1)
        write_int(len(input) * 0x8)
        write_int(len(input))
        write_int(0x2)
        write_int(0x0)
        file.write(b"BD")

    print("Done! Output written to", outpath)

ERR_HEADER = "Error! Invalid string container!"
WARN_COLL = "Warning! A hash collision has occurred! The hash 0x{:08X} corresponds to the following strings\n- {}\n- {}\nThe latter will be discarded!"

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Exports and imports Bully (Canis Canem Edit) text containers")
    subparsers = parser.add_subparsers(description="To view additional help for each subparser, add -h | --help after it")

    extract_parser = subparsers.add_parser("X", help="extracts a text container")
    extract_parser.add_argument("path", type=str, help="path to the text container")
    extract_parser.add_argument("-o", "--output", type=str, default=str(), help="path to the output file")
    extract_parser.set_defaults(read=True, func=parse_bin)

    build_parser = subparsers.add_parser("B", help="builds a new text container")
    build_parser.add_argument("path", type=str, help="path to the json file")
    build_parser.add_argument("-o", "--output", type=str, default=str(), help="path to the output file")
    build_parser.add_argument("-be", "--bigendian", action="store_true", help="build in big endian (Wii, Xbox 360)")
    build_parser.set_defaults(read=False, func=build_bin)

    args = parser.parse_args()
    try:
        func_args = [args.path, args.output]
        if not args.read:
            func_args.append(args.bigendian)
        args_func = args.func
    except AttributeError:
        print("Error! Bad arguments given. Use -h or --help to show valid arguments.")
    args_func(*func_args)
