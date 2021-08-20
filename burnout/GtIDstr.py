# Reworked /scripts/other/LingoTildeStr.py due to being relatively similar.

# Written by Edness
# 2021-08-20   v1.0

import argparse

def c_int(s):
    if s.startswith("0x"): return int(s[2:],16)
    if s.startswith("0b"): return int(s[2:],2)
    if s.startswith("0o"): return int(s[2:],8)
    return int(s,10)

def char2utf(c_char):
    char = {
        1: "-", 2: "/", 3: "0", 4: "1", 5: "2", 6: "3", 7: "4", 8: "5", 9: "6", 10: "7",
        11: "8", 12: "9", 13: "A", 14: "B", 15: "C", 16: "D", 17: "E", 18: "F", 19: "G", 20: "H",
        21: "I", 22: "J", 23: "K", 24: "L", 25: "M", 26: "N", 27: "O", 28: "P", 29: "Q", 30: "R",
        31: "S", 32: "T", 33: "U", 34: "V", 35: "W", 36: "X", 37: "Y", 38: "Z", 39: "_"
    }
    return char.get(c_char," ")

def utf2char(char):
    c_char = {
        "-": 1, "/": 2, "0": 3, "1": 4, "2": 5, "3": 6, "4": 7, "5": 8, "6": 9, "7": 10,
        "8": 11, "9": 12, "A": 13, "B": 14, "C": 15, "D": 16, "E": 17, "F": 18, "G": 19, "H": 20,
        "I": 21, "J": 22, "K": 23, "L": 24, "M": 25, "N": 26, "O": 27, "P": 28, "Q": 29, "R": 30,
        "S": 31, "T": 32, "U": 33, "V": 34, "W": 35, "X": 36, "Y": 37, "Z": 38, "_": 39
    }
    return c_char.get(char,0)

def read_num(args):
    str = ""
    c_str = args.num
    for i in range(len):
        str += char2utf(c_str % 40)
        c_str //= 40
    print("Decompressed string:",str[::-1])

def read_str(args):
    res = 0
    d_str = args.str.ljust(len)
    for i in range(len):
        res += (utf2char(str(d_str[i].upper()))*(40**(len-i-1)))
    print(f"Compressed string: 0x{res:X} ({res})")

parser = argparse.ArgumentParser(description="Converts to and from the EA compressed string format present in Burnout games.")
subparsers = parser.add_subparsers()
decode_parser = subparsers.add_parser("dec",help="Decompress string.")
decode_parser.add_argument("num",type=c_int)
decode_parser.set_defaults(func=read_num)
encode_parser = subparsers.add_parser("enc",help="Compress string.")
encode_parser.add_argument("str",type=str)
encode_parser.set_defaults(func=read_str)
parser.add_argument("-l","--len",type=int,default=12,help="How long the string should be (Default = 12)")
args = parser.parse_args()
len = args.len
args.func(args)
