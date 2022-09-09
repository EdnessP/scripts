#!/usr/bin/env python3
# Midnight Club STMA/RSTM lookup hashing function
# Written by Edness   v1.0   2022-06-22

def lookup_hash(str):
    # Reimplemented from the function at  004F9298  in the
    # PS2 PAL version of Midnight Club 3: DUB Edition Remix
    # Also found at  00386DB0  in PS2 PAL Midnight Club 2

    # For Midnight Club 2 the sound files are supposed to
    # end with .STM, but for Midnight Club 3 - with .RSM
    hash = 0x00000000
    str = str.upper().replace("\\", "/")
    for idx, chr in enumerate(str, 1):
        hash = (hash << 1 | hash >> 31) + ord(chr) * idx & 0xFFFFFFFF
    return hash

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Hashes strings into their RSTM hashed values used by Midnight Club 3.")
    parser.add_argument("str", type=str)
    args = parser.parse_args()

    hash = lookup_hash(args.str)
    print(f"Hashed string: 0x{hash:08X} ({hash})")
