#!/usr/bin/env python3
# Call of Duty: Finest Hour filename hashing function reimplementation
# from the function at  001429B8  in the PS2 PAL  SPS.BIN  executable.
# There is a secondary loop break condition, if the character is a ;

# Written by Edness   v1.0   2022-10-10

def spark_hash(str):
    hash = 0x84222325CBF29CE4
    str = str.upper().replace("/", "\\").split(";")[0]
    for chr in str:
        hash = ord(chr) ^ (hash << 40) + hash * 0x1B3 & 0xFFFFFFFFFFFFFFFF
    return hash

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Hashes filenames into their hashed values used by Call of Duty: Finest Hour.")
    parser.add_argument("str", type=str)
    args = parser.parse_args()

    hash = spark_hash(args.str)
    print(f"Hashed string: 0x{hash:016X} ({hash})")
