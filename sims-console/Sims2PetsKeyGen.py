#!/usr/bin/env python3
# Rewritten from the functions at  00120558  and  00120338
# for decoding, and the function at  00120160  for encoding
# in the PS2 PAL v1.00 executable of The Sims 2: Pets console

# https://EdnessP.github.io/live/strings#The_Sims_(Console)

# Written by Edness   v1.2   2023-03-19 - 2023-08-16

# Usage:
#   script.py enc <gift_id> [-n | --name <name>]
#   script.py dec <key>

import re, zlib

PETS_ENC_LEN = 19
PETS_DEC_LEN = 13
PETS_CHARS = "12346789ABCDEFGHIJKLMNPQRTUVWXYZO05SabcdefghijklmnopqrstuvwxyzÀÁÄÆÈÉÌÍÑÒÓÖÙÚÜŒàáâäæçèéêëìíîïñòóôöùúûüßœ -.!@#~%^&*()+=:;,\\/?'\"{}"
PETS_GIFTS = {  # head fashion icons for cats reuse the ones for dogs
    14: "Cat Fur Colors - Blue",                   # f_furcolor_blue
    41: "Cat Fur Colors - Green",                  # f_furcolor_green
    38: "Cat Fur Colors - Pink",                   # f_furcolor_pink
    28: "Cat Fur Colors - Purple",                 # f_furcolor_purple
     8: "Cat Fur Colors - Red",                    # f_furcolor_red
    27: "Cat Fur Marking Colors - Blue",           # f_furcolor_blue
    34: "Cat Fur Marking Colors - Green",          # f_furcolor_green
    11: "Cat Fur Marking Colors - Pink",           # f_furcolor_pink
    19: "Cat Fur Marking Colors - Purple",         # f_furcolor_purple
    29: "Cat Fur Marking Colors - Red",            # f_furcolor_red
    46: "Cat Fur Marking Patterns - Bandit Mask",  # f_mark_banditmask
    42: "Cat Fur Marking Patterns - Panda",        # f_mark_panda
    16: "Cat Glasses - Blue Elvis Glasses",        # d_gl_elvis_blue
    24: "Cat Glasses - Green Cat's Eyes",          # d_gl_catseyes
     3: "Cat Glasses - Magenta Aviators",          # d_gl_aviators_magenta
    30: "Cat Hats - Blue Head Bandana",            # d_ht_headbandana_blue
     5: "Cat Hats - Red-White Bucket Hat",         # d_ht_bucket_redwhite
    13: "Cat Neckwear - Green Bandana",            # d_cl_bandana_green
    20: "Cat Neckwear - Green Leather with Bone",  # d_cl_medal_leathergreen
     1: "Cat Neckwear - Pink Bandana",             # d_cl_bandana_pink
    35: "Cat Neckwear - Red Leather with Bone",    # d_cl_medal_leatherred
    36: "Cat Shirts - Green Shirt",                # f_tm_shirt_green
    12: "Cat Shirts - Orange Shirt",               # f_tm_shirt_orange
    32: "Dog Fur Colors - Blue",                   # d_furcolor_blue
    10: "Dog Fur Colors - Green",                  # d_furcolor_green
    21: "Dog Fur Colors - Pink",                   # d_furcolor_pink
    44: "Dog Fur Colors - Purple",                 # d_furcolor_purple
    18: "Dog Fur Colors - Red",                    # d_furcolor_redkisspoint
    40: "Dog Fur Marking Colors - Blue",           # d_furcolor_blue
    31: "Dog Fur Marking Colors - Green",          # d_furcolor_green
     9: "Dog Fur Marking Colors - Pink",           # d_furcolor_pink
    17: "Dog Fur Marking Colors - Purple",         # d_furcolor_purple
    26: "Dog Fur Marking Colors - Red",            # d_furcolor_redkisspoint
    45: "Dog Fur Marking Patterns - Stars",        # d_mark_stars
    43: "Dog Fur Marking Patterns - Zebra",        # d_mark_zebra
    15: "Dog Glasses - Green Cat's Eyes",          # d_gl_catseyes
    23: "Dog Glasses - Magenta Aviators",          # d_gl_aviators_magenta
    33: "Dog Glasses - Purple Elvis Glasses",      # d_gl_elvis_purple
    39: "Dog Hats - Blonde-Violet Golf Hat",       # d_ht_golf_blondeviolet
     4: "Dog Hats - Green Tight Cowboy Hat",       # d_ht_cowboytight_green
    22: "Dog Neckwear - Green Bandana",            # d_cl_bandana_green
    25: "Dog Neckwear - Green Leather with Bone",  # d_cl_medal_leathergreen
     6: "Dog Neckwear - Pink Bandana",             # d_cl_bandana_pink
     7: "Dog Neckwear - Red Leather with Bone",    # d_cl_medal_leatherred
     2: "Dog Shirts - Green Shirt",                # d_tm_shirt_green
    37: "Dog Shirts - Orange Shirt",               # d_tm_shirt_orange
     0: "Unused ID (Dog Hats)",
    47: "Unused ID",
    48: "Unused ID",
    49: "Unused ID",
    50: "Unused ID"
}

def pets_decode_key(key):
    key = re.sub("[^0-9A-Z]", "", key.upper())
    if len(key) != PETS_ENC_LEN:
        print("Error: Invalid key length!")
        return

    key_dec = list(bytes(PETS_DEC_LEN - 3))
    key_enc = [PETS_CHARS.index(c) for c in key]
    for i in range(0, 10, 5):
        for j in range(7):
            for k in range(i, i + 5):
                key_dec[k] = key_dec[k] | 1 << j if key_enc[j + (i // 5) * 7] >> k - i & 1 else key_dec[k] & ~(1 << j)

    key_int = 0
    for i in range(24):
        d_idx = i // 5
        e_idx = i % 5 + 14
        key_int = key_int | 1 << i if key_enc[e_idx] >> d_idx & 1 else key_int & ~(1 << i)
    key_dec.extend(key_int.to_bytes(3, "little"))

    # This algorithm has a significant flaw, where it for whatever reason converts first 9 bytes
    # of the decoded key to UTF-16 (putting NULLs after every byte) however it still hashes the
    # first 9 bytes (name + gift id) of the converted key even though it's now 18 bytes large.
    key_conv = list(bytes(9))
    for i in range(5):
        key_conv[i * 2] = key_dec[i]
    key_hash = zlib.crc32(bytes(key_conv)) & 0x7F7F7F7F
    if key_hash != int.from_bytes(bytes(key_dec[-4:]), "big"):
        print("Error: Invalid checksum!")
        return
    if key_dec[8] > 50:
        print("Error: Invalid gift ID!")
        return

    key_name = "".join([PETS_CHARS[c] for c in key_dec[:8]])
    print(f"Gifter: {key_name}\nGiftID: {key_dec[8]} ({PETS_GIFTS.get(key_dec[8])})")

def pets_encode_key(gift_id, name=""):
    if gift_id not in range(0, 51):
        print("Error! Invalid gift ID!")

    key_enc = list(bytes(PETS_ENC_LEN))
    key_dec = [PETS_CHARS.index(c) for c in name.ljust(8)[:8]]
    key_dec.append(gift_id)

    # broken key hash validation implementation, see comment in pets_decode_key()
    key_conv = list(bytes(9))
    for i in range(5):
        key_conv[i * 2] = key_dec[i]
    key_hash = zlib.crc32(bytes(key_conv)) & 0x7F7F7F7F
    key_dec.extend(key_hash.to_bytes(4, "big"))

    for i in range(0, 10, 5):
        for j in range(7):
            for k in range(i, i + 5):
                idx = j + (i // 5) * 7
                key_enc[idx] = key_enc[idx] | 1 << k - i if key_dec[k] >> j & 1 else key_enc[idx] & ~(1 << k - i)

    key_int = int.from_bytes(key_dec[-3:], "little")
    for i in range(24):
        d_idx = i // 5
        e_idx = i % 5 + 14
        key_enc[e_idx] = key_enc[e_idx] | 1 << d_idx if key_int >> i & 1 else key_enc[e_idx] & ~(1 << d_idx)

    key = "-".join(re.findall(".{1,4}", "".join([PETS_CHARS[c] for c in key_enc])))
    print(f"Unlock Code: {key}\nGift: {PETS_GIFTS.get(gift_id)}")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Encodes and decodes the Unlock Code from The Sims 2: Pets.")
    subparsers = parser.add_subparsers()

    decode_parser = subparsers.add_parser("dec", help="decode a key")
    decode_parser.add_argument("key", type=str)
    decode_parser.set_defaults(func=pets_decode_key)

    encode_parser = subparsers.add_parser("enc", help="encode a key")
    encode_parser.add_argument("gift_id", type=int)
    encode_parser.add_argument("-n", "--name", type=str, default="", help="gifter's name")
    encode_parser.set_defaults(func=pets_encode_key)

    args = parser.parse_args()
    try: args.func(args.key) if "dec" in args.func.__name__ else args.func(args.gift_id, args.name)
    except AttributeError: print("Error! No arguments given. Use -h or --help to show valid arguments.")
