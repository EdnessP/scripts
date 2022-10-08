#!/usr/bin/env python3
# Midnight Club STMA/RSTM and string lookup hashing functions
# Written by Edness   v1.1   2022-06-22 - 2022-10-07

def audio_hash(str):
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

def string_hash(str):
    # Reimplemented from function at  003587E8  from the
    # PS2 PAL version of Midnight Club 2

    # Midnight Club 3's string hashing function is nearly
    # identical to Bully's, just without the conversion to
    # lowercase and backslashes to forward slashes, which
    # can be found at  scripts/bully/BullyHash.py
    hash = 0x00000000
    for chr in str:
        hash = (hash << 4) + ord(chr)
        if mask := hash & 0xF0000000:
            hash ^= mask >> 24 ^ mask
    return hash

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Hashes strings for audio and string lookups used by Midnight Club 2 and 3.")
    subparsers = parser.add_subparsers()
    rsm_parser = subparsers.add_parser("aud", help="Hashes strings into their STMA/RSTM hashed names in Midnight Club 2 and 3.")
    rsm_parser.add_argument("string", type=str)
    rsm_parser.set_defaults(func=audio_hash)
    str_parser = subparsers.add_parser("str", help="Hashes the string labels used for string lookups in Midnight Club 2.")
    str_parser.add_argument("string", type=str)
    str_parser.set_defaults(func=string_hash)
    args = parser.parse_args()

    try: hash = args.func(args.string)
    except AttributeError: print("No arguments given. Use -h or --help to show valid arguments.")
    else: print(f"Hashed string: 0x{hash:08X} ({hash})")
