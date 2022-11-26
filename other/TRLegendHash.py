#!/usr/bin/env python3
# Tomb Raider: Legend filename hashing algorithm

# Reimplemented from the function at  0009AF00  in
# the Xbox 2005-12-08 pre-release build executable
# and the function at  001A19C0  in the PS2 PAL elf

# Written by Edness   v1.0   2022-11-26

def tr_legend_hash(str):
    hash = 0xFFFFFFFF
    str = str.lower()
    for chr in str:
        hash ^= ord(chr) << 24
        for i in range(8):
            hash = (hash * 2 ^ 0x04C11DB7 if hash >> 31 else hash << 1) & 0xFFFFFFFF
    return hash ^ 0xFFFFFFFF  # ~hash & 0xFFFFFFFF

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Hashes filenames into their hashed values used by Tomb Raider: Legend.")
    parser.add_argument("str", type=str)
    args = parser.parse_args()

    hash = tr_legend_hash(args.str)
    print(f"Hashed string: 0x{hash:08X} ({hash})")
