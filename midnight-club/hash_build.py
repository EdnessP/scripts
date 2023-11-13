#!/usr/bin/env python3
# Extract and build Angel Studios / Rockstar San Diego Hash sound archives
# Midnight Club 2,  Midnight Club 3: DUB Edition,  Bully (Canis Canem Edit)

# Usage:
#   Extract:  X  (Python 3.8 or newer)
#       hash_build.py  X  "/path/to/streams.dat"
#     Optional:
#       -o  | --output    <str> Path to the output directory;  default is input folder
#       -nl | --namelist  <str> Path to the filename text file
#       -a  | --algo      <str> {Bully,MClub} Filename hashing algorithm
#       -th | --threshold <int> Percentage threshold how many names should match to accept;  default is 70
#         hash_build.py  X  "X:\path\to\streams.dat"  -o "Y:\path\to\folder"
#         hash_build.py  X  "X:\path\to\streams.dat"  -nl "Z:\path\to\streams.lst"  -a mclub  -th 45
#
#   Rebuild:  B  (Python 3.9 or newer)
#       -a  | --algo      <str> {Bully,MClub} Filename hashing algorithm
#         hash_build.py  B  "Y:\path\to\folder"  "X:\path\to\music.bin"  -a bully
#     Optional:
#       -be | --bigendian       Build in big endian (Wii, Xbox 360)
#         hash_build.py  B  "/path/to/folder"  "/path/to/music.bin"  -a bully  -be

# Written by Edness   2022-07-05 - 2023-11-13   v1.3

import glob, os

HASHED = "__hashed"
HASHES = (HASH := b"Hash", HSAH := b"hsaH")
INT_MAX_RANGE = range(1 << 32)
POSIX_SEP = os.sep == "/"

def __bully_hash(str):
    # Reimplemented from the  zipHashFile::Hash  function located
    # at  0040CDF0  in the PS2 PAL version of Canis Canem Edit
    hash = 0x00000000
    hash_str = str.lower().replace("\\", "/").encode("ASCII")
    for chr in hash_str:
        hash = (hash + chr) * 0x401 & 0xFFFFFFFF
        hash ^= hash >> 6
    hash = hash * 9 & 0xFFFFFFFF
    return (hash ^ hash >> 11) * 0x8001 & 0xFFFFFFFF, str

def __mclub_hash(str):
    # Reimplemented from the function at  004F9298  in the
    # PS2 PAL version of Midnight Club 3: DUB Edition Remix
    # Also found at  00386DB0  in PS2 PAL Midnight Club 2
    hash = 0x00000000
    hash_str = str.upper().replace("\\", "/").encode("ASCII")
    for idx, chr in enumerate(hash_str, 1):
        hash = (hash << 1 | hash >> 31) + chr * idx & 0xFFFFFFFF
    return hash, str

def get_hash_func(algo):
    hash_func = {
        "bully": __bully_hash,
        "mclub": __mclub_hash
    }.get(algo.lower())
    assert hash_func is not None, ERR_ALGO
    return hash_func

def exists_prompt(output, prompt):
    if os.path.exists(output):
        response = input(f"Warning! {prompt} (Y/N): ")[:1].upper()
        if response != "Y":
            if response != "N":
                print("Error! Invalid response.", end=" ")
            print("Exiting...")
            return False
    return True

def build_hash(path, output, algo=str(), big_endian=False):
    def seek_align():
        offset = file.tell()
        if not offset & 0x7FF: return offset
        return file.seek((offset // 0x800 + 1) * 0x800)

    def write_int(int):
        return file.write(int.to_bytes(0x4, endian))

    endian = "big" if big_endian else "little"
    calc_hash = get_hash_func(algo)
    output = os.path.abspath(output)  # normalizes path separators and stuff
    path = os.path.join(os.path.abspath(path), "")  # force final path separator

    if not exists_prompt(output, "Output file already exists. Overwrite?"):
        return

    hash_dict = dict()
    print("Preparing files...")
    for file_path in glob.iglob(os.path.join(glob.escape(path), "**", "*"), recursive=True):
        if os.path.isdir(file_path):
            continue
        file_name = file_path.removeprefix(path)
        hash = int(os.path.splitext(os.path.split(file_name)[-1])[0], 16) if \
               file_name.startswith(HASHED) else calc_hash(file_name.strip())[0]
        assert hash in INT_MAX_RANGE, ERR_HASH.format(file_name)  # bad hashed entries
        assert hash not in hash_dict, ERR_COLL.format(hash, hash_dict[hash], file_name)
        hash_dict[hash] = file_name
    assert hash_dict, ERR_DICT

    offs_list = list()
    size_list = list()
    name_list = list()
    entries = len(hash_dict)
    os.makedirs(os.path.split(output)[0], exist_ok=True)
    with open(output, "wb") as file:
        file.seek(0x8 + entries * 0xC)
        for hash in hash_dict:
            print("Writing", hash_dict[hash])
            with open(os.path.join(path, hash_dict[hash]), "rb") as in_file:
                data = in_file.read()
            offs = seek_align()
            assert offs in INT_MAX_RANGE, ERR_SIZE
            size = file.write(data)
            offs_list.append(offs)
            size_list.append(size)
        file.seek(seek_align() - 1)
        file.write(b"\x00")  # pad last file

        print("Writing archive header...")
        file.seek(0x0)
        #file.write(HSAH if big_endian else HASH)
        write_int(0x68736148)  # endian dependant "Hash"
        write_int(entries)
        for hash, offs, size in sorted(zip(hash_dict, offs_list, size_list)):
            if not hash_dict[hash].startswith(HASHED):
                file_name = hash_dict[hash].strip()
                if not POSIX_SEP:
                    file_name = file_name.replace("\\", "/")
                name_list.append(file_name)
            write_int(hash)
            write_int(offs)
            write_int(size)

    print("\nSuccess! Archive built at", output)

    if name_list:
        outname = os.path.splitext(output)[0]
        outname += ".LST" if os.path.split(outname)[-1].isupper() else ".lst"
        with open(outname, "w") as file:
            file.write("\n".join(name_list))
            #file.write("\n".join([str() if hash_dict[hash].startswith(HASHED) else hash_dict[hash] for hash in sorted(hash_dict)]))

        print("File name list written at", outname)

def read_hash(path, output=str(), namepath=str(), algo=str(), threshold=70):
    def read_int():
        return int.from_bytes(file.read(0x4), endian)

    def get_name_dict():
        return dict(sorted([calc_hash(name.strip() + ext) for name in name_list if name.strip()]))

    if not output:
        output = os.path.splitext(path)[0]
    output = os.path.abspath(output)

    if not exists_prompt(output, "Output directory already exists. Overwrite files?"):
        return

    with open(path, "rb") as file:
        hash_id = file.read(0x4)
        assert hash_id in HASHES, ERR_HARC

        endian = "little" if hash_id == HASH else "big"
        file_count = read_int()

        # Bully SE Wii fix (unlikely for full support)
        file.seek(0x14)
        is_wii_fsb = not read_int() | read_int()
        file.seek(0x8)

        hash_list = list()
        offs_list = list()
        size_list = list()
        for i in range(file_count):
            hash_list.append(read_int())
            offs_list.append(read_int())
            size_list.append(read_int())
            if is_wii_fsb:
                file.seek(0x8, 1)

        name_dict = dict()
        if namepath:
            calc_hash = get_hash_func(algo)
            assert 0 <= threshold <= 100, ERR_THLD
            with open(namepath, "r") as name_file:
                name_list = name_file.read().splitlines()

            name_match = dict([(x, int()) for x in ("", ".rsm", ".stm")])
            for ext in name_match:
                name_dict = get_name_dict()
                for hash in hash_list:
                    if hash in name_dict:
                        name_match[ext] += 1
                if name_match[ext] >= file_count:
                    print("Name list validated" + ("!" if ext == "" else f" with the additional extension {ext}!"))
                    break
            else:
                print("The provided name list does not match the Hash archive.")
                for ext in name_match:
                    name_match[ext] = name_match[ext] / file_count * 100
                max_match = max(name_match.values())
                if max_match > threshold:
                    ext = list(name_match.keys())[list(name_match.values()).index(max_match)]
                    name_dict = get_name_dict()
                    print("However, hashes", "without an additional extension" if ext == "" else f"with the additional extension {ext}", f"matched {round(max_match, 2)}% of the name list.")
                else:
                    name_dict = dict()

        for hash, offs, size in zip(hash_list, offs_list, size_list):
            name = name_dict.get(hash, os.path.join(HASHED, f"{hash:08X}")) # + {b"RSTM": ".rsm", b"STMA": ".stm"}.get(file_data[:0x4], "")
            name = name.replace("\\", "/") if POSIX_SEP else name.replace("/", "\\")
            outpath = os.path.join(output, name)
            file.seek(offs)
            print("Writing", outpath)
            os.makedirs(os.path.split(outpath)[0], exist_ok=True)
            with open(outpath, "wb") as out_file:
                out_file.write(file.read(size))

    print("\nSuccess! Done extracting.")

ERR_ALGO = "Error! Invalid hash algorithm. Please provide the hashing algorithm with -a | --algo\nValid algorithms are 'Bully' and 'MClub'"
ERR_COLL = "Error! A hash collision has occurred. The hash 0x{:08X} resolves to:\n- {}\n- {}"
ERR_DICT = "Error! No files were found at the given path."
ERR_HARC = "Error! Not a Hash archive."
ERR_HASH = "Error! Invalid hash detected."
ERR_SIZE = "Error! Archive too large."
ERR_THLD = "Error! Invalid threshold value."

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Extracts and builds Angel Studios / Rockstar San Diego Hash archives")
    subparsers = parser.add_subparsers(description="To view additional help for each subparser, add -h | --help after it")

    extract_parser = subparsers.add_parser("X", help="extracts a Hash archive (Python 3.8 or newer)")
    extract_parser.add_argument("path", type=str, help="path to the Hash archive")
    extract_parser.add_argument("-o", "--output", type=str, default=str(), help="path to the output folder")
    extract_parser.add_argument("-nl", "--namelist", type=str, default=str(), help="path to a text file of names")
    extract_parser.add_argument("-a", "--algo", type=str, default=str(), help="{Bully,MClub} filename hashing algorithm")
    extract_parser.add_argument("-th", "--threshold", type=int, default=70, help="threshold percentage how many names should match to accept; (default=70)")
    extract_parser.set_defaults(read=True, func=read_hash)

    build_parser = subparsers.add_parser("B", help="builds a new Hash archive (Python 3.9 or newer)")
    build_parser.add_argument("path", type=str, help="path to the input directory")
    build_parser.add_argument("output", type=str, help="path to the output Hash archive")
    build_parser.add_argument("-a", "--algo", type=str, default=str(), help="{Bully,MClub} filename hashing algorithm")
    build_parser.add_argument("-be", "--bigendian", action="store_true", help="build in big endian (Wii, Xbox 360)")
    build_parser.set_defaults(read=False, func=build_hash)

    args = parser.parse_args()
    try:
        func_args = (args.path, args.output, args.namelist, args.algo, args.threshold) if args.read else (args.path, args.output, args.algo, args.bigendian)
        args.func(*func_args)
    except AttributeError:
        print("Error! Bad arguments given. Use -h or --help to show valid arguments.")
