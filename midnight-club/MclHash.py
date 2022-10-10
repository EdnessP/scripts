#!/usr/bin/env python3
# Midnight Club STMA/RSTM and string lookup hashing functions
# Written by Edness   v1.2   2022-06-22 - 2022-10-10

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

def string_hash2(str):
    # Reimplemented from the function at  003587E8  in the
    # PS2 PAL version of Midnight Club 2

    hash = 0x00000000
    for chr in str:
        hash = (hash << 4) + ord(chr)
        if mask := hash & 0xF0000000:
            hash ^= mask >> 24 ^ mask
    return hash

def string_hash3(str):
    # Reimplemented from the function at  002BE788  in the
    # PS2 PAL version of Midnight Club 3: DUB Edition Remix

    # Almost identical to the audio hashing function in Bully
    # which can be found at  scripts/bully/BullyHash.py
    hash = 0x00000000
    for chr in str:
        hash = (hash + ord(chr)) * 0x401 & 0xFFFFFFFF
        hash ^= hash >> 6
    hash = hash * 9 & 0xFFFFFFFF
    return (hash ^ hash >> 11) * 0x8001 & 0xFFFFFFFF

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Hashes strings for audio and string lookups used by Midnight Club 2 and 3.")
    subparsers = parser.add_subparsers()
    rsm_parser = subparsers.add_parser("aud", help="Hashes strings into their STMA/RSTM hashed names in Midnight Club 2 and 3.")
    rsm_parser.add_argument("string", type=str)
    rsm_parser.set_defaults(func=audio_hash)
    str_parser = subparsers.add_parser("str2", help="Hashes the string labels used for string lookups in Midnight Club 2.")
    str_parser.add_argument("string", type=str)
    str_parser.set_defaults(func=string_hash2)
    str_parser = subparsers.add_parser("str3", help="Hashes the string labels used for string lookups in Midnight Club 3: DUB Edition.")
    str_parser.add_argument("string", type=str)
    str_parser.set_defaults(func=string_hash3)
    args = parser.parse_args()

    try: hash = args.func(args.string)
    except AttributeError: print("No arguments given. Use -h or --help to show valid arguments.")
    else: print(f"Hashed string: 0x{hash:08X} ({hash})")
