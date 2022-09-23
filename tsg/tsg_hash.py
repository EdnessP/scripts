#!/usr/bin/env python3
# The Simpsons Game (NewGen) string label hash function
# Reimplemented from the function at  827451C0  in the
# Xbox 360 version, or from  00522090 in the PS3 version

# Written by Edness   v1.0   2022-09-22

def tsg_label(str):
    str = str.lower()
    hash = 0x00000000
    for chr in str:
        hash = 0x1003F * hash + ord(chr) & 0xFFFFFFFF
    return hash

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Hashes strings into their hashed values used by The Simpsons Game.")
    parser.add_argument("str", type=str)
    args = parser.parse_args()

    hash = tsg_label(args.str)
    print(f"Hashed string: 0x{hash:08X} ({hash})")
