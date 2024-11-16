#!/usr/bin/env python3
# Scan WORLD.IMG and update the .LIP files to match SPEECH.BIN metadata

# Usage:
#   lipfile_update.py  "X:\Stream\World.dir"  "X:\Audio\PlayList\Speech.bin"

# Written by Edness   2023-11-08 - 2024-11-16   v1.2

import glob, os

endian = str()

def read_int(file, bytes=0x4):
    return int.from_bytes(file.read(bytes), endian)

def read_str(file):
    return "".join(iter(lambda: file.read(0x1).decode("ASCII"), "\x00"))

def write_int(file, int, bytes=0x4):
    return file.write(int.to_bytes(bytes, endian))

def update_lip(world_dir, speech_path):
    world_dir = os.path.abspath(world_dir)
    speech_path = os.path.abspath(speech_path)

    # locate WORLD.IMG from the given WORLD.DIR path
    stream_split = os.path.split(world_dir)
    world_img = os.path.splitext(stream_split[1].lower())[0] + ".img"
    for path in glob.iglob(os.path.join(glob.escape(stream_split[0]), "*")):
        if path.lower().endswith(world_img):
            world_img = path
            break
    else:
        raise RuntimeError(ERR_WRLD.format(world_img.capitalize()))

    global endian
    print("Loading Speech.bin...")
    with open(speech_path, "rb") as bin:
        header = bin.read(0x4)
        assert header in {b"Hash", b"hsaH"}, ERR_HASH
        endian = "little" if header == b"Hash" else "big"
        bin_entries = read_int(bin)

        # Bully SE Wii fix (unlikely for full support)
        bin.seek(0x14)
        is_wii_fsb = not read_int(bin) | read_int(bin)
        bin.seek(0x8)

        hash_list = list()
        offs_list = list()
        size_list = list()
        for i in range(bin_entries):
            hash_list.append(read_int(bin))
            offs_list.append(read_int(bin))
            size_list.append(read_int(bin))
            if is_wii_fsb:
                bin.seek(0x8, 1)

    print("Loading World.img...")
    dir_entries = os.path.getsize(world_dir) // 0x20
    with open(world_dir, "rb") as dir, open(world_img, "r+b") as img:
        assert read_int(img) != 0x0FF512ED, ERR_XMEM
        for idx in range(dir_entries):
            dir.seek(idx * 0x20)
            offs = read_int(dir) * 0x800
            size = read_int(dir) * 0x800
            name = read_str(dir)
            if name.lower().endswith(".lip"):
                print(f"Checking {name}...")
                img.seek(offs)
                lip_entries = read_int(img, 0x2)
                #lipsync_size = read_int(img, 0x2)
                for idx in range(lip_entries):
                    lip_offs = offs + 0x4 + idx * 0x18
                    img.seek(lip_offs + 0x0)
                    bin_idx = read_int(img, 0x2)
                    img.seek(lip_offs + 0xC)
                    bin_offs = read_int(img)
                    bin_size = read_int(img)
                    bin_hash = read_int(img)
                    assert bin_hash in hash_list, ERR_ENTR.format(bin_hash)
                    idx = hash_list.index(bin_hash)
                    if idx != bin_idx:
                        img.seek(lip_offs + 0x0)
                        write_int(img, idx, 0x2)
                    if (bin_offs, bin_size) != (offs_list[idx], size_list[idx]):
                        img.seek(lip_offs + 0xC)
                        write_int(img, offs_list[idx])
                        write_int(img, size_list[idx])

    print("\nDone! If there are more World.img copies, please replace them with a copy of:\n" + world_img)

ERR_ENTR = "Error! Couldn't find the hash 0x{:08X}"
ERR_HASH = "Error! Invalid Speech.bin Hash archive."
ERR_WRLD = "Error! Couldn't find {} in the given folder."
ERR_XMEM = "Error! World.img has to be decompressed first."

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Updates Bully's .LIP files in WORLD.IMG to match SPEECH.BIN")
    parser.add_argument("world_path", type=str, help="path to WORLD.DIR (not .IMG)")
    parser.add_argument("speech_path", type=str, help="path to SPEECH.BIN")

    args = parser.parse_args()
    update_lip(args.world_path, args.speech_path)
