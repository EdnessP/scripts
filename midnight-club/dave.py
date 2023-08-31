#!/usr/bin/env python3
# Extract and build Angel Studios / Rockstar San Diego DAVE/Dave archives.

# Usage:
#   Extract:  X
#       script.py  X  "/path/to/dave.dat"
#     Optional:
#       -o | --output {str} Path to the output directory;  default is input folder
#         script.py  X  "X:\path\to\dave.zip"  -o "Y:\path\to\folder"
#
#   Rebuild:  B
#       script.py  B  "Y:\path\to\folder"  "X:\path\to\new_dave.dat"
#     Optional:
#       -cf | --compfiles   Compress all files
#       -cn | --compnames   Compress filenames (build Dave instead of DAVE)
#       -d  | --dirs        Include directory entries
#       -a  | --align {int} 16 byte file alignment;  default is 128 (0x800 bytes)

# Written by Edness   2022-01-09  -  2023-08-31   v1.4

import glob, os, zlib

CHARS = "\x00 #$()-./?0123456789_abcdefghijklmnopqrstuvwxyz~"
POSIX_SEP = os.sep == "/"

def build_dave(path, output, compfiles=False, compnames=False, dirs=False, align=128):
    def calc_align(size, align):
        return (size // align + 1) * align

    def seek_align(align):
        return file.seek(calc_align(file.tell(), align))

    def write_int(int):
        return file.write(int.to_bytes(0x4, "little"))

    print("Preparing files...")

    dave = b"DAVE" if not compnames else b"Dave"
    align *= 16

    path = os.path.join(os.path.abspath(path), "")  # force final path separator
    file_paths = glob.glob(os.path.join(glob.escape(path), "**", "*"), recursive=True)

    #file_names = [path + "/" for path in file_paths if os.path.isdir(path)]
    #file_names = [name.removeprefix(path).replace("\\", "/") for name in file_paths]
    #file_names = zip(file_paths, file_names)
    #file_names.sort(key=lambda name: [CHARS.index(c) for c in name.lower()])

    file_sets = list()  # dict(zip())
    for file_path in file_paths:
        if not dirs and os.path.isdir(file_path):
            continue
        file_name = file_path.removeprefix(path)
        if not POSIX_SEP:
            file_name = file_name.replace("\\", "/")
        if os.path.isdir(file_path) and not file_name.endswith("/"):
            file_name += "/"
        #if compnames:
        #    file_name = file_name.lower()
        file_sets.append((file_name, file_path))
    file_sets.sort(key=lambda entry: [CHARS.index(c) for c in entry[0].lower()])

    if not compnames:
        file_names = [entry[0].encode("ASCII") + b"\x00" for entry in file_sets]
    else:  # compress and deduplicate names
        dedup_idx = 0
        file_name = str()
        file_names = list()
        for entry in file_sets:
            comp_name = int()
            dedup_info = None
            prev_name = file_name
            file_name = entry[0].lower()

            # identical files at different offsets copy instead of full-dedup
            # while not really handled by the script, this is original behaviour
            #if prev_name == file_name:
            #    # in the name builder it'd rewrite the previous offset
            #    file_names.append(-1)
            #    continue  # doesn't increment dedup_idx

            name = file_name
            if dedup_idx:
                for idx, (prev_char, file_char) in enumerate(zip(prev_name, file_name), 1):
                    if prev_char != file_char:
                        idx -= 1
                        break
                if idx:
                    assert idx < 256, "Error! Filename too long."
                    dedup_info = divmod(idx, 8)
                    name = file_name[idx:]
                else:  # reset counter at new name
                    dedup_idx = 0

            byte_len = len(name) + 1
            for c in name[::-1]:
                comp_name <<= 6
                comp_name |= CHARS.index(c)
            if dedup_info is not None:
                comp_name <<= 12
                comp_name |= dedup_info[0] + 0x20 << 6 | dedup_info[1] + 0x38
                byte_len += 2
            byte_len = (byte_len * 6 / 8).__ceil__()
            file_names.append(int.to_bytes(comp_name, byte_len, "little"))

            dedup_idx = dedup_idx + 1 & 0x1F  # limit to 32

    entries = len(file_names)
    # entry and name blocks are always 0x800 aligned
    entry_size = calc_align(len(file_sets) * 0x10, 0x800)
    names_size = calc_align(len(b"".join(file_names)), 0x800)

    entry_info = list()
    with open(output, "wb") as file:
        file.write(dave)
        write_int(entries)
        write_int(entry_size)
        write_int(names_size)

        file_offs = 0x800 + entry_size + names_size
        file.seek(file_offs)
        for idx, (name, path) in enumerate(file_sets):
            print("Writing", name)  # path
            if name.endswith("/"):
                entry_info.append((file_offs, 0x0, 0x0))
                continue
            with open(path, "rb") as tmp:
                data = tmp.read()
            #file_size_full = len(data)
            if compfiles:
                zlib_obj = zlib.compressobj(9, zlib.DEFLATED, -15)
                comp_data = zlib_obj.compress(data) + zlib_obj.flush()
                if len(comp_data) < len(data):
                    data = comp_data
            entry_info.append((file_offs, os.path.getsize(path), len(data)))
            file.write(data)
            file_offs = seek_align(align)

        print("Writing entry data...")
        file.seek(0x800)
        for offset, size_full, size_comp in entry_info:
            file.seek(0x4, 1)
            write_int(offset)
            write_int(size_full)
            write_int(size_comp)

        print("Writing name data...")
        name_offs = 0x0
        entry_range = range(entries - 1, -1, -1) if compnames else range(entries)
        for idx in entry_range:
            file.seek(0x800 + idx * 0x10)
            write_int(name_offs)
            name_offs += len(file_names[idx])
        if compnames:
            file_names.reverse()

        file.seek(0x800 + entry_size)
        file.write(b"".join(file_names))

    print(f"\nSuccess! Done building.")

def read_dave(path, outpath=str()):
    def read_int(bytes):
        return int.from_bytes(file.read(bytes), "little")

    def read_str():
        return "".join(iter(lambda: file.read(0x1).decode("ASCII"), "\x00"))

    def read_bits():
        comp_data = read_int(0x3)
        return [comp_data >> mul * 6 & 0x3F for mul in range(4)]

    if not outpath:
        outpath = os.path.splitext(path)[0]
    outpath = os.path.abspath(outpath)
    #os.makedirs(os.path.split(outpath)[0], exist_ok=True)

    file_name = str()
    with open(path, "rb") as file:
        dave = file.read(0x4)
        assert dave in {b"DAVE", b"Dave"}, "Error! Not a DAVE/Dave archive."

        entries = read_int(0x4)
        info_size = read_int(0x4)
        name_size = read_int(0x4)

        file.seek(0x800)
        for i in range(entries):
            file.seek(0x800 + i * 0x10)
            name_offs = read_int(0x4) + info_size + 0x800
            file_offs = read_int(0x4)
            file_size_full = read_int(0x4)
            file_size_comp = read_int(0x4)

            file.seek(name_offs)
            if dave == b"DAVE":
                file_name = read_str()
            else:  # == "Dave":
                name_bits = read_bits()
                prev_name = file_name
                file_name = str()
                if name_bits[0] >= 0x30:  # deduplicate
                    dedup_len = (name_bits.pop(1) - 0x20) * 8 + name_bits.pop(0) - 0x38
                    file_name = prev_name[:dedup_len]
                while name_bits[0]:  # decompress
                    file_name += CHARS[name_bits.pop(0)]
                    if not name_bits:
                        name_bits = read_bits()

            out_path = os.path.join(outpath, file_name)
            if not POSIX_SEP:
                out_path = out_path.replace("/", "\\")

            if not file_name.endswith("/"):
                file.seek(file_offs)
                data = file.read(file_size_comp)
                if file_size_full != file_size_comp:
                    data = zlib.decompress(data, -15)
                    assert len(data) == file_size_full, "Error! Data decompression size mismatch."

                print("Writing", out_path)
                os.makedirs(os.path.split(out_path)[0], exist_ok=True)
                with open(out_path, "wb") as out:
                    out.write(data)
            else:
                print("Creaing", out_path)
                os.makedirs(out_path, exist_ok=True)

    print(f"\nSuccess! Done extracting.")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Extracts and builds Angel Studios / Rockstar San Diego DAVE/Dave archives")
    subparsers = parser.add_subparsers(description="to view additional help for each subparser, add -h | --help after it")

    extract_parser = subparsers.add_parser("X", help="extracts a DAVE/Dave archive")
    extract_parser.add_argument("path", type=str, help="path to the DAVE/Dave archive")
    extract_parser.add_argument("-o", "--output", type=str, default="", help="path to the output folder")
    extract_parser.set_defaults(read=True)

    build_parser = subparsers.add_parser("B", help="builds a new DAVE archive")
    build_parser.add_argument("path", type=str, help="path to the input directory")
    build_parser.add_argument("output", type=str, help="path to the output DAVE/Dave archive")
    build_parser.add_argument("-cf", "--compfiles", action="store_true", help="compress all files")
    build_parser.add_argument("-cn", "--compnames", action="store_true", help="compress filenames (use Dave instead of DAVE)")
    build_parser.add_argument("-d", "--dirs", action="store_true", help="include directory entries")
    build_parser.add_argument("-a", "--align", type=int, default=128, help="set a multiple of 16 byte alignment (default=128 (0x800))")
    build_parser.set_defaults(read=False)

    args = parser.parse_args()
    try: read_dave(args.path, args.output) if args.read else build_dave(args.path, args.output, args.compfiles, args.compnames, args.dirs, args.align)
    except AttributeError: print("Error! Bad arguments given. Use -h or --help to show valid arguments.")
