#!/usr/bin/env python3
# Converts to and from Bully: Anniversary Edition encrypted .EFF, .MTL, .WDB, .XML files.

# Batch processing can be done on Windows with Command Prompt using:
#   FOR /F "tokens=*" %G IN ('dir /s /b "X:\path\to\files\*.xml"') DO BullyAE_encryption.py decf "%G"
# and on Linux, macOS, and BSD with Terminal using:
#   find /path/to/files -name "*.xml" -print -exec ./BullyAE_encryption.py decf {} \;
# where  decf  can be replaced with  encf  to batch re-encrypt files.

# Written by Edness    v1.2
# 2021-11-29  -  2022-06-13

import os

_encrypt_key = b"6Ev2GlK1sWoCa5MfQ0pj43DH8Rzi9UnX"
_encrypt_hash = 0x0CEB538D

def encrypt(string):
    dec_size = len(string)
    enc_size = 8 * dec_size // 5 + 1
    dec_data = list(string + b"\x00")
    enc_data = list(bytes(enc_size))

    xor = 18
    hash = _encrypt_hash
    for i in range(dec_size):
        hash = 0xAB * (hash % 0xB1) - 2 * (hash // 0xB1) & 0xFFFFFFFF
        dec_data[i] = ((dec_data[i] - hash) ^ xor) & 0xFF
        xor += 6

    idx = 0
    switch = 0
    rm_char = False
    for i in range(enc_size):
        char = dec_data[idx]
        if idx + 1 < len(dec_data):
            next = dec_data[idx + 1]
        else:
            rm_char = True
            next = 0

        char = {
            0: char >> 3,
            1: char >> 2 & 0x1F,
            2: char >> 1 & 0x1F,
            3: char & 0x1F,
            4: (char & 0xF) << 1 | next >> 7,
            5: (char & 0x7) << 2 | next >> 6,
            6: (char & 0x3) << 3 | next >> 5,
            7: (char & 0x1) << 4 | next >> 4
        }.get(switch, 0)

        enc_data[i] |= _encrypt_key[char]

        if (switch + 5) % 8 < switch: idx += 1
        switch = (switch + 5) % 8

    enc_data = b"Wx" + bytes(enc_data[:-1] if rm_char else enc_data)
    return enc_data

def decrypt(string):
# The decryption routine is a Python reimplementation of  https://forum.xentax.com/viewtopic.php?t=15777  and
# https://github.com/bartlomiejduda/Tools/blob/master/NEW%20Tools/Bully%20Anniversary%20Edition/Bully_XML_Tool.cpp

    buffer = list(bytes(256))
    for idx in range(len(_encrypt_key)):
        buffer[_encrypt_key[idx]] = idx

    enc_size = len(string)
    dec_size = 5 * enc_size // 8
    dec_data = list(bytes(dec_size + 1))

    idx = 0
    switch = 0
    for i in range(enc_size):
        char = buffer[string[i]]

        next = {
            4: char << 7,
            5: char << 6,
            6: char << 5,
            7: char << 4
        }.get(switch, 0)

        char = {
            0: char << 3,
            1: char << 2,
            2: char << 1,
            3: char,
            4: char >> 1,
            5: char >> 2,
            6: char >> 3,
            7: char >> 4
        }.get(switch, 0)

        dec_data[idx] |= char
        dec_data[idx + 1] |= next

        if (switch + 5) % 8 < switch: idx += 1
        switch = (switch + 5) % 8

    xor = 18
    hash = _encrypt_hash
    for i in range(dec_size):
        hash = 0xAB * (hash % 0xB1) - 2 * (hash // 0xB1) & 0xFFFFFFFF
        dec_data[i] = ((dec_data[i] ^ xor) + hash) & 0xFF
        xor += 6

    dec_data = bytes(dec_data[:-1])
    return dec_data

def enc_str(args):
    string = bytes(args.enc_string, "UTF-8")
    data = encrypt(string)
    print(str(data, "ASCII"))

def dec_str(args):
    string = bytes(args.dec_string, "ASCII")
    assert(string.startswith(b"Wx"))
    data = decrypt(string[2:])
    print(str(data, "UTF-8"))

def enc_file(args):
    with open(args.enc_path, "rb") as file:
        string = file.read()
    data = encrypt(string)
    input = os.path.splitext(args.enc_path)
    output = input[0] + ".enc" + input[1]
    with open(output, "wb") as file:
        file.write(data)
    print("Encrypted file written to ", output)

def dec_file(args):
    with open(args.dec_path, "rb") as file:
        assert(file.read(2) == (b"Wx"))
        string = file.read()
    data = decrypt(string)
    input = os.path.splitext(args.dec_path)
    output = input[0] + ".dec" + input[1]
    with open(output, "wb") as file:
        file.write(data)
    print("Decrypted file written to ", output)

def main():
    import argparse

    this = os.path.basename(__file__)
    path = "X:\\path\\to\\" if os.name == "nt" else "/path/to/"

    parser = argparse.ArgumentParser(description="Converts the encrypted text files in Bully: Anniversary Edition.")
    subparsers = parser.add_subparsers()
    decrypt_file_parser = subparsers.add_parser("decf", help="Decrypt file. \xA0 \xA0 Example: " + this + " decf " + path + "encrypted.xml")
    decrypt_file_parser.add_argument("dec_path", type=str)
    decrypt_file_parser.set_defaults(func=dec_file)
    decrypt_string_parser = subparsers.add_parser("decs", help="Decrypt string. \xA0 Example: " + this + " decs WxEHUf2GfEnC...")
    decrypt_string_parser.add_argument("dec_string", type=str)
    decrypt_string_parser.set_defaults(func=dec_str)
    encrypt_file_parser = subparsers.add_parser("encf", help="Encrypt file. \xA0 \xA0 Example: " + this + " encf " + path + "decrypted.xml")
    encrypt_file_parser.add_argument("enc_path", type=str)
    encrypt_file_parser.set_defaults(func=enc_file)
    encrypt_string_parser = subparsers.add_parser("encs", help="Encrypt string. \xA0 Example: " + this + " encs <Entry name=...")
    encrypt_string_parser.add_argument("enc_string", type=str)
    encrypt_string_parser.set_defaults(func=enc_str)
    args = parser.parse_args()

    try: args.func(args)
    except AttributeError: print("No arguments given. Use -h or --help to show valid arguments.")
    except (AssertionError, UnicodeEncodeError): print("Invalid string detected!")
    except IndexError: print(("De" if str(args.func)[10:].startswith("dec") else "En") + "cryption failed!")
    except UnicodeDecodeError: print("Decoding failed!")

if __name__ == "__main__":
    main()
