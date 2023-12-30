#!/usr/bin/env python3
# Disney Epic Mickey Wii string lookup hash algorithm.
# Reimplemented from the function at  80A1D070  in the
# secondary relocatable executable from the US release

# Usage:
#     epic_mickey_hash.py  "string to hash"
#   Optional:
#     -id | --dictid  <int>  Dictionary hash seed ID found at 0x8 in a .DCT file
#       epic_mickey_hash.py  string_to_hash  -id 0x12345678

# Written by Edness   v1.1   2023-12-27 - 2023-12-28

def epic_mickey_hash(string: bytes, dct_id=int()) -> int:
    # dct_id is the unique hash seed present at 0x8
    # in each of the language .DCT dictionary files
    assert type(string) in {bytes, bytearray}, ERR_TYPE
    # Asking for encoding beforehand instead of doing it here,
    # because while stepping through the game in a debugger, I
    # saw some test string passed through that had upper range
    # characters which would be broken here (\xC5 -> \xC3\x85)
    string = string.lower()
    chunks = len(string) // 12
    uint32 = lambda num: num & 0xFFFFFFFF
    hash0 = uint32(dct_id)
    hash1 = 0x9E3779B9
    hash2 = hash1
    # Can't tell if this is PowerPC loop unrolling at play,
    # or if it's just this unnecessarily over-engineered...
    # The different iterations can likely be consolidated
    # further; I do see some very vague rotating patterns
    idx = int()
    for i in range(chunks):
        hash4 = uint32(hash0 + int.from_bytes(string[idx + 8:idx + 12], "little"))
        hash3 = uint32(hash1 + int.from_bytes(string[idx + 4:idx +  8], "little"))
        hash1 = uint32(hash2 + int.from_bytes(string[idx + 0:idx +  4], "little"))
        hash1 = uint32((hash1 - hash3) - hash4 ^ hash4 >> 13)
        hash3 = uint32((hash3 - hash4) - hash1 ^ hash1 <<  8)
        hash2 = uint32((hash4 - hash1) - hash3 ^ hash3 >> 13)
        hash1 = uint32((hash1 - hash3) - hash2 ^ hash2 >> 12)
        hash3 = uint32((hash3 - hash2) - hash1 ^ hash1 << 16)
        hash4 = uint32((hash2 - hash1) - hash3 ^ hash3 >>  5)
        hash2 = uint32((hash1 - hash3) - hash4 ^ hash4 >>  3)
        hash1 = uint32((hash3 - hash4) - hash2 ^ hash2 << 10)
        hash0 = uint32((hash4 - hash2) - hash1 ^ hash1 >> 15)
        idx += 12
    hash0 += len(string)
    hash0 = uint32(hash0 + (int.from_bytes(string[idx + 8:idx + 11], "little") << 8))
    hash1 = uint32(hash1 +  int.from_bytes(string[idx + 4:idx +  8], "little"))
    hash2 = uint32(hash2 +  int.from_bytes(string[idx + 0:idx +  4], "little"))
    hash2 = uint32((hash2 - hash1) - hash0 ^ hash0 >> 13)
    hash4 = uint32((hash1 - hash0) - hash2 ^ hash2 <<  8)
    hash3 = uint32((hash0 - hash2) - hash4 ^ hash4 >> 13)
    hash1 = uint32((hash2 - hash4) - hash3 ^ hash3 >> 12)
    hash4 = uint32((hash4 - hash3) - hash1 ^ hash1 << 16)
    hash2 = uint32((hash3 - hash1) - hash4 ^ hash4 >>  5)
    hash1 = uint32((hash1 - hash4) - hash2 ^ hash2 >>  3)
    hash3 = uint32((hash4 - hash2) - hash1 ^ hash1 << 10)
    hash0 = uint32((hash2 - hash1) - hash3 ^ hash3 >> 15)
    return hash0

ERR_TYPE = "Please encode the input string first."

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Hashes strings into their hashed lookup values used by Epic Mickey")
    parser.add_argument("str", type=str, help="string to hash")
    parser.add_argument("-id", "--dictid", type=lambda num: int(num, 16) if num.startswith("0x") else int(num),
                        default="0", help="unique dictionary hash seed ID value, found at 0x8 in a .DCT file")
    args = parser.parse_args()

    hash = epic_mickey_hash(args.str.encode(), args.dictid)
    print(f"Hashed string: 0x{hash:08X} ({hash})")
