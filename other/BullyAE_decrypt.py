#!/usr/bin/env python3
# Decrypts Bully: Anniversary Edition .EFF, .MTL, .WDB, .XML files.  Batch processing can be done
# on Windows with Command Prompt using:
#   FOR /F "tokens=*" %G IN ('dir /s /b X:\path\to\files\*.xml') DO BullyAE_decrypt.py decf %G
# and on Linux, macOS, and BSD with Terminal using:
#   find /path/to/files -name "*.xml" -print -exec ./BullyAE_decrypt.py decf {} \;

# Python reimplementation of  https://forum.xentax.com/viewtopic.php?t=15777
# and  https://github.com/bartlomiejduda/Tools/blob/master/NEW%20Tools/Bully%20Anniversary%20Edition/Bully_XML_Tool.cpp

# Written by Edness
# 2021-11-29   v1.0

import argparse, os

encrypt_key = b"6Ev2GlK1sWoCa5MfQ0pj43DH8Rzi9UnX"
encrypt_hash = 0x0CEB538D

def decrypt(string):
    buffer = [0 for i in range(256)]
    for idx in range(len(encrypt_key)):
        buffer[encrypt_key[idx]] = idx

    idx = 0
    switch = 0
    data_len = len(string)
    dec_size = (5 * data_len >> 3)
    dec_data = [0 for i in range(dec_size + 1)]
    for i in range(data_len):
        detect = buffer[string[i]]

        value = {
            4: detect << 7,
            5: detect << 6,
            6: detect << 5,
            7: detect << 4
        }.get(switch, 0)

        detect = {
            0: detect << 3,
            1: detect << 2,
            2: detect << 1,
            3: detect,
            4: detect >> 1,
            5: detect >> 2,
            6: detect >> 3,
            7: detect >> 4
        }.get(switch, 0)

        dec_data[idx] |= detect
        dec_data[idx + 1] |= value

        if switch + 5 <= 7:
            switch += 5
        else:
            idx += 1
            switch -= 3

    xor = 0x12
    hash = encrypt_hash
    for i in range(dec_size):
        hash = 0xAB * (hash % 0xB1) - 2 * (hash // 0xB1)
        if hash < 0: hash += 2 ** 32
        dec_data[i] = ((dec_data[i] ^ xor) + hash) & 0xFF
        xor += 6

    dec_data = bytes(dec_data[:-1])
    return dec_data

def dec_str(args):
    string = args.dec_string
    assert(string.startswith("Wx"))
    data = decrypt(bytes(string[2:], "ASCII"))
    print(str(data, "UTF-8"))

def dec_file(args):
    with open(args.dec_path, "rb") as file:
        string = file.read()
        assert(string.startswith(b"Wx"))
        data = decrypt(string[2:])
    input = os.path.splitext(args.dec_path)
    output = input[0] + ".dec" + input[1]
    with open(output, "wb") as file:
        file.write(data)
        print("Decrypted file written to", output)

cur_file = os.path.basename(__file__)
parser = argparse.ArgumentParser(description="Converts the encrypted text files in Bully: Anniversary Edition.")
subparsers = parser.add_subparsers()
decrypt_file_parser = subparsers.add_parser("decf", help="Decrypt file.\xa0\xa0\xa0 Example: "+cur_file+" decf X:\\path\\to\\encrypted.xml")
decrypt_file_parser.add_argument("dec_path", type=str)
decrypt_file_parser.set_defaults(func=dec_file)
decrypt_string_parser = subparsers.add_parser("decs", help="Decrypt string.\xa0 Example: "+cur_file+" decs WxEHUf2GfEnC...")
decrypt_string_parser.add_argument("dec_string", type=str)
decrypt_string_parser.set_defaults(func=dec_str)
args = parser.parse_args()
try: args.func(args)
except AttributeError: print("No arguments given. Use -h or --help to show valid arguments.")
except AssertionError: print("Invalid string detected!")
except IndexError: print("Decryption failed!")
except UnicodeDecodeError: print("Decoding failed!")
