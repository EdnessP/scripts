#!/usr/bin/env python3
# Bully name hashing function reimplementations from the PS2 version
# Written by Edness   v1.0   2022-06-20

def rstm_hash(str):
    # Reimplemented from the  zipHashFile::Hash  function at  0040CDF0  in PS2 PAL
    # Used for looking up RSTM audio files by their hashed names

    # The game normally checks if it starts with a quotation mark and strips it,
    # and also terminates the hash loop if/when a quotation mark is encountered.
    hash = 0x00000000
    str = str.lower().replace("\\", "/")
    for chr in str:
        hash = (hash + ord(chr)) * 0x401 & 0xFFFFFFFF
        hash ^= hash >> 6
    hash = hash * 9 & 0xFFFFFFFF
    return (hash ^ hash >> 11) * 0x8001 & 0xFFFFFFFF

def label_hash(str):
    # Reimplemented from the  HashUCstring & HashStringJS  functions
    # Used for looking up strings by their hashed labels

    hash = 0x00000000
    str = str.upper()
    for chr in str:
        hash = ord(chr) + hash * 0x83 & 0x7FFFFFFF
    return hash

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Hashes strings used by Bully.")
    subparsers = parser.add_subparsers()
    rsm_parser = subparsers.add_parser("rsm", help="Hashes strings into their RSTM hashed names used by Bully.")
    rsm_parser.add_argument("string", type=str)
    rsm_parser.set_defaults(func=rstm_hash)
    str_parser = subparsers.add_parser("str", help="Hashes the string labels used for string lookups in Bully.")
    str_parser.add_argument("string", type=str)
    str_parser.set_defaults(func=label_hash)
    args = parser.parse_args()

    try: hash = args.func(args.string)
    except AttributeError: print("No arguments given. Use -h or --help to show valid arguments.")
    else: print(f"Hashed string: 0x{hash:08X} ({hash})")
