#!/usr/bin/env python3
# Extract and build Angel Studios / Rockstar San Diego DAVE/Dave archives

# Usage:
#   Extract:  X  (Python 3.8 or newer)
#       dave.py  X  "/path/to/dave.dat"
#     Optional:
#       -o | --output <str> Path to the output directory;  default is input folder
#         dave.py  X  "X:\path\to\dave.zip"  -o "Y:\path\to\folder"
#
#
#   Rebuild:  B  (Python 3.11 or newer)
#       dave.py  B  "Y:\path\to\folder"  "X:\path\to\new_dave.dat"
#     Optional:
#       -cf | --compfiles       Compress all files (with exceptions, see below)
#       -cn | --compnames       Compress filenames (build Dave instead of DAVE)
#       -d  | --dirs            Include directory entries
#       -a  | --align     <int> 16 byte file alignment;  default is 128 (2048 bytes)
#       -ca | --compalign       Compact align (pack multiple files into a single chunk)
#         dave.py  B  "/path/to/folder"  "/path/to/new_dave.zip"  -cn  -a 0
#
#     Optional (with -cf | --compfiles):
#       -fc | --forcecomp <int> Force compress all files (Bypass blocklist, see comment)
#                               default is 0 (1=assumed safe files, 2=all files, unsafe)
#       -cl | --complevel <int> Compression level;  default is 9 (1=fastest, 9=smallest)
#         dave.py  B  "/path/to/folder"  "/path/to/new_dave.dat"  -cf  -fc 1

# Written by Edness   2022-01-09 - 2023-11-07   v1.5.3

import glob, os, zlib

# The games only store all the chars until ~, but I've seen a few
# files that use the (normally) invalid index 0x30 which I assume
# was a fallback to DEL in their own packer for unsupported chars
CHARS = "\x00 #$()-./?0123456789_abcdefghijklmnopqrstuvwxyz~\x7F"
DAVES = (DAVE := b"DAVE", Dave := b"Dave")
POSIX_SEP = os.sep == "/"
# Midnight Club 3, Midnight Club: L.A. Remix, and Red Dead Revolver
# seem to expect PCKs and PPFs to always be decompressed; it never
# checks if it's compressed, just reads the data as-is, and points
# to it thinking it's completely fine, which causes it to hang...
#
# There are some nuances to it too, such as the PCKs in MC3 that are
# outside of  flash/  and  resources/vehicle/  can be compressed, so
# the  -fc | --forcecomp  argument can take either  1  to compress
# the files that are assumed to be safe, or to  2  for everything.
COMP_EXT_BLOCKLIST = (
    ".pck", ".psppck", ".xbck",
    ".ppf", ".pspppf", ".xbpf",
)
COMP_DIR_BLOCKLIST = (
    "flash/",
    "resources/vehicle/",
)

def exists_prompt(output, prompt):
    if os.path.exists(output):
        response = input(f"Warning! {prompt} (Y/N): ")[:1].upper()
        if response != "Y":
            if response != "N":
                print("Error! Invalid response.", end=" ")
            print("Exiting...")
            return False
    return True

def build_dave(inpath, output, compfiles=False, forcecomp=0, complevel=9, compnames=False, dirs=False, align=128, compalign=False):
    def calc_align(size, align):
        return (size // align + 1) * align

    def seek_align(align):
        return file.seek(calc_align(file.tell(), align))

    def get_int(int, bytes):
        return int.to_bytes(bytes, "little")

    def write_int(int):
        return file.write(get_int(int, 0x4))

    def comp_allow():
        if forcecomp == 2:
            return True
        # doesn't break AFAIK but just to be safe (mini Daves)
        if forcecomp == 0 and data.startswith(DAVES):
            return False
        # maybe restrict PPF compression to --forcecomp 2
        if name.lower().endswith(COMP_EXT_BLOCKLIST):
            # root folder PCKs are blocked from compressing for Red Dead Revolver
            if forcecomp == 1 and "/" in name and not name.lower().startswith(COMP_DIR_BLOCKLIST):
                return True
            return False
        return True

    def size_assert_help():
        help = list()
        if not compfiles:
            help.append("compressing files")
        if not compnames:
            if help[-1] == "compressing files":
                help[-1] += " or filenames"
            else:
                help.append("compressing filenames")
        if compfiles and complevel < 9:
            help.append("increasing the compression level")
        if align:
            help.append("reducing the alignment size")
            if not compalign:
                help[-1] += " or enabling compact alignment"
        if dirs:
            help.append("not including directory entries")
        help = ", or ".join(help)
        return str() if not help else f"\nTry {help}."

    output = os.path.abspath(output)  # normalizes path separators and stuff
    inpath = os.path.join(os.path.abspath(inpath), "")  # force final path separator

    if not exists_prompt(output, "Output file already exists. Overwrite?"):
        return

    if compfiles:
        assert 1 <= complevel <= 9, ERR_COMPLVL
        assert 0 <= forcecomp <= 2, ERR_COMPFRC
    assert align >= 0, ERR_ALIGN
    align *= 16

    print("Preparing files...")
    file_sets = list()  # dict(zip())
    for file_path in glob.iglob(os.path.join(glob.escape(inpath), "**", "*"), recursive=True, include_hidden=True):
        if not dirs and os.path.isdir(file_path):
            continue
        file_name = file_path.removeprefix(inpath)
        if not POSIX_SEP:
            file_name = file_name.replace("\\", "/")
        if os.path.isdir(file_path) and not file_name.endswith("/"):
            file_name += "/"
        assert len(file_name) < 256, ERR_NAMELEN.format(file_name)
        #if compnames:  # earlier games using DAVE have other chars
        for c in set(file_name.lower()):  # fallback to \x7F DEL for Dave/compnames?
            assert c in CHARS if compnames else c.isascii(), ERR_NAMECHAR.format(c, file_name)
        file_sets.append((file_name, file_path))
    # none of the games seemed to use "?" in names so it's probably safe to just use str.lower alone for sorting...
    file_sets.sort(key=lambda entry: [CHARS.index(c) for c in entry[0].lower()] if compnames else entry[0].lower())

    # prepare the filename block
    if not compnames:
        # not sure if identical names are also handled by this variant
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

            # identical files at diff offsets copy the name instead of full-dedup
            # while not really handled by the script, this is original behaviour
            # but technically can be reproduced on case sensitive file systems
            if prev_name == file_name:
                # in the name builder it'd rewrite the previous offset
                file_names.append(b"")
                continue  # doesn't increment dedup_idx

            name = file_name
            if dedup_idx:
                for idx, (prev_char, file_char) in enumerate(zip(prev_name, file_name), 1):
                    if prev_char != file_char:
                        idx -= 1
                        break
                if idx:
                    dedup_info = divmod(idx, 8)
                    name = file_name[idx:]
                else:  # reset counter at new name
                    dedup_idx = 0

            name_size = len(name) + 1
            for c in name[::-1]:
                comp_name <<= 6
                comp_name |= CHARS.index(c)
            if dedup_info is not None:
                comp_name <<= 12
                comp_name |= dedup_info[0] + 0x20 << 6 | dedup_info[1] + 0x38
                name_size += 2
            name_size = (name_size * 0.75).__ceil__()  # * 6 / 8
            file_names.append(get_int(comp_name, name_size))

            # limit is 32 dedupes, probably because the games parse them recursively...
            dedup_idx = dedup_idx + 1 & 0x1F

    entries = len(file_names)
    # entry and name blocks are always 0x800 aligned
    entry_size = calc_align(len(file_sets) * 0x10, 0x800)
    names_size = calc_align(len(b"".join(file_names)), 0x800)

    entry_info = list()
    os.makedirs(os.path.split(output)[0], exist_ok=True)
    with open(__file__) as file: dave = file.read(0x800)
    dave = dave[dave.index(" ".join([chr(x) for x in (35, 87)])) + 0x2:]
    dave = dave.splitlines()[0].split(); dave = " ".join(dave[:3]), dave[-1]
    dave = " - ".join((os.path.split(__file__)[1], *dave[::-1])).encode("UTF-8")
    with open(output, "wb") as file:
        file.seek(0x800 - len(dave))
        file.write(dave)
        file_offs = file.seek(0x800 + entry_size + names_size)
        for name, path in file_sets:
            print("Writing", name)  # path
            if name.endswith("/"):
                entry_info.append((file_offs, 0x0, 0x0))
                continue  # dirs don't increase file_offs
            assert file_offs <= 0xFFFFFFFF, ERR_ARCSIZE + size_assert_help()
            with open(path, "rb") as tmp:
                data = tmp.read()
            if compfiles and comp_allow():
                zlib_obj = zlib.compressobj(complevel, zlib.DEFLATED, -15)
                comp_data = zlib_obj.compress(data) + zlib_obj.flush()
                if len(comp_data) < len(data):
                    data = comp_data
            # pack multiple tiny files into a single sector, if possible
            # if dirs are included, it will create a new alignment zone.
            if compalign and align > 0x20 and entry_info:
                prev_offs = entry_info[-1][0]
                prev_align = prev_offs & (align - 1)
                prev_size = calc_align(entry_info[-1][2], 0x20)
                if 0 < entry_info[-1][2] < align and prev_align + prev_size + len(data) < align:
                    file_offs = file.seek(prev_offs + prev_size)
            entry_info.append((file_offs, os.path.getsize(path), len(data)))
            file.write(data)
            file_offs = seek_align(align) if align else file.tell()
        if align:  # pad last file
            file.seek(-1, 1)
            file.write(b"\x00")

        print("Writing archive header...")
        name_offs = [0x0]  # compressed names are stored backwards
        for idx in range(entries - 1, -1, -1) if compnames else range(entries):
            name_offs.append(name_offs[-1] + len(file_names[idx]))
        name_offs.pop()
        if compnames:
            name_offs.reverse()
            file_names.reverse()

        file.seek(0x0)
        file.write(Dave if compnames else DAVE)
        write_int(entries)
        write_int(entry_size)
        write_int(names_size)

        file.seek(0x800)
        for name_offs, (file_offs, size_full, size_comp) in zip(name_offs, entry_info):
            write_int(name_offs)
            write_int(file_offs)
            write_int(size_full)
            write_int(size_comp)

        file.seek(0x800 + entry_size)
        file.write(b"".join(file_names))

    print("\nSuccess! Archive built at", output)
    print("From the source folder at", inpath)

def read_dave(path, output=str()):
    def read_int(bytes):
        return int.from_bytes(file.read(bytes), "little")

    def read_str():
        return "".join(iter(lambda: file.read(0x1).decode("ASCII"), "\x00"))

    def read_bits():
        comp_data = read_int(0x3)
        return [comp_data >> mul * 6 & 0x3F for mul in range(4)]

    if not output:
        output = os.path.splitext(path)[0]
    output = os.path.abspath(output)

    if not exists_prompt(output, "Output directory already exists. Overwrite files?"):
        return

    with open(path, "rb") as file:
        dave = file.read(0x4)
        assert dave in DAVES, ERR_DAVE

        entries = read_int(0x4)
        info_size = read_int(0x4)
        name_size = read_int(0x4)

        file_name = str()
        for i in range(entries):
            file.seek(0x800 + i * 0x10)
            name_offs = read_int(0x4) + info_size + 0x800
            file_offs = read_int(0x4)
            file_size_full = read_int(0x4)
            file_size_comp = read_int(0x4)

            file.seek(name_offs)
            if dave == DAVE:
                file_name = read_str()
            else:  # = Dave:
                name_bits = read_bits()
                prev_name = file_name
                file_name = str()
                if name_bits[0] >= 0x38:  # deduplicate
                    dedup_size = (name_bits.pop(1) - 0x20) * 8 + name_bits.pop(0) - 0x38
                    file_name = prev_name[:dedup_size]
                while name_bits[0]:  # decompress
                    file_name += CHARS[name_bits.pop(0)]
                    if not name_bits:
                        name_bits = read_bits()

            outpath = os.path.join(output, file_name)
            if not POSIX_SEP:
                outpath = outpath.replace("/", "\\")

            if not file_name.endswith("/"):
                file.seek(file_offs)
                data = file.read(file_size_comp)
                if file_size_full != file_size_comp:
                    data = zlib.decompress(data, -15)
                assert len(data) == file_size_full, ERR_DECOMP.format(file_name)

                print("Writing", outpath)
                os.makedirs(os.path.split(outpath)[0], exist_ok=True)
                with open(outpath, "wb") as out:
                    out.write(data)
            else:  # looks very jarring if the length isn't the same, so it isn't "Creating" or "Making"
                print("Opening", outpath)
                os.makedirs(outpath, exist_ok=True)

    print("\nSuccess! Done extracting.")

# Assertion messages, so they're not visible twice
ERR_ALIGN    = "Error! Invalid alignment size."
ERR_ARCSIZE  = "Error! Archive too large."
ERR_COMPLVL  = "Error! Invalid compression level."
ERR_COMPFRC  = "Error! Invalid compression force level."
ERR_DAVE     = "Error! Not a DAVE/Dave archive."
ERR_DECOMP   = "Error! Data decompression size mismatch. ({})"
ERR_NAMECHAR = "Error! Filename contains illegal characters. (\"{}\" in {})"
ERR_NAMELEN  = "Error! Filename too long. ({})"

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Extracts and builds Angel Studios / Rockstar San Diego DAVE/Dave archives")
    subparsers = parser.add_subparsers(description="To view additional help for each subparser, add -h | --help after it")

    extract_parser = subparsers.add_parser("X", help="extracts a DAVE/Dave archive (Python 3.8 or newer)")
    extract_parser.add_argument("path", type=str, help="path to the DAVE/Dave archive")
    extract_parser.add_argument("-o", "--output", type=str, default=str(), help="path to the output folder")
    extract_parser.set_defaults(read=True, func=read_dave)

    build_parser = subparsers.add_parser("B", help="builds a new DAVE archive (Python 3.11 or newer)")
    build_parser.add_argument("path", type=str, help="path to the input directory")
    build_parser.add_argument("output", type=str, help="path to the output DAVE/Dave archive")
    build_parser.add_argument("-cf", "--compfiles", action="store_true", help="compress all files (with exceptions, see -fc | --forcecomp)")
    build_parser.add_argument("-fc", "--forcecomp", type=int, default=int(), help="{1,2} force compress all files (1=assumed safe files, 2=all files, unsafe)")
    build_parser.add_argument("-cl", "--complevel", type=int, default=9, help="set the file compression level (default=9; (1=fastest, 9=smallest))")
    build_parser.add_argument("-cn", "--compnames", action="store_true", help="compress filenames (build Dave instead of DAVE)")
    build_parser.add_argument("-d", "--dirs", action="store_true", help="include directory entries")
    build_parser.add_argument("-a", "--align", type=int, default=128, help="set a multiple of 16 byte alignment (default=128 (2048 bytes))")
    build_parser.add_argument("-ca", "--compalign", action="store_true", help="compact align (pack multiple files into a single chunk)")
    build_parser.set_defaults(read=False, func=build_dave)

    args = parser.parse_args()
    try:
        func_args = (args.path, args.output) if args.read else (args.path, args.output, args.compfiles, args.forcecomp, args.complevel, args.compnames, args.dirs, args.align, args.compalign)
        args.func(*func_args)
    except AttributeError:
        print("Error! Bad arguments given. Use -h or --help to show valid arguments.")
