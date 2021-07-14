# This is a very stripped down recreation of the function at 00402630 in SIA Tilde's Lingo (EXE CRC32: EEE06AD9),
# that handles decompressing and loading a random string from the array in the WORDS resource 110 inside the EXE.

# Some creative liberty™ was taken to simplify things further, such as the converted letter switch case normally
# returning lower-case 1257 encoded letters and right after that subtracting by 32 to get its upper-case variant.
# Here it will just return them already in upper-case (and not 1257 encoded either, I hope.)

# My initial inspiration for this was remembering how when I was a kid, there was an insanely rare chance (1/1000)
# I'd get the broken answer GVAAA.  The cause of this, as I've now learned is from the 1st 32 bit value in the res
# which is the number 999 (signifying it has 999 total words) yet that also gets picked up as a compressed string
# and its decompressed result is, as you might've expected - GVAAA.

# A bonus addition not a part of the original game I added was the ability to compress your own string.  It can be
# either replaced in the EXE, or what I did - using a debugger and replacing the loaded value in the ESI register
# when hitting a breakpoint anywhere between instructions at 0040278D and 004027D9.
# ... Or just replace the unpacked string at 0040ACF0 in RAM, but that's no fun and won't change the 1st character.

# Written by Edness
# 2021-07-13   v1.1

import argparse,struct,os

def c_int(s):
    if s.startswith("0x"): return int(s[2:],16)
    if s.startswith("0b"): return int(s[2:],2)
    if s.startswith("0o"): return int(s[2:],8)
    return int(s,10)

def char2utf(c_char):
    char = {
        0: "A", 1: "Ā", 2: "B", 3: "C", 4: "Č", 5: "D", 6: "E", 7: "Ē",
        8: "F", 9: "G", 10: "Ģ", 11: "H", 12: "I", 13: "Ī", 14: "J", 15: "K",
        16: "Ķ", 17: "L", 18: "Ļ", 19: "M", 20: "N", 21: "Ņ", 22: "O", 23: "P",
        24: "R", 25: "S", 26: "Š", 27: "T", 28: "U", 29: "Ū", 30: "V", 31: "Z"
    }
    print(char.get(c_char,"Ž"),end="")

def utf2char(char):
    c_char = {
        "Ā": "1", "B": "2", "C": "3", "Č": "4", "D": "5", "E": "6", "Ē": "7", "F": "8",
        "G": "9", "Ģ": "a", "H": "b", "I": "c", "Ī": "d", "J": "e", "K": "f", "Ķ": "g",
        "L": "h", "Ļ": "i", "M": "j", "N": "k", "Ņ": "l", "O": "m", "P": "n", "R": "o",
        "S": "p", "Š": "q", "T": "r", "U": "s", "Ū": "t", "V": "u", "Z": "v", "Ž": "w"
    }
    return c_char.get(char,"0")

def dec_str(c_str):
    print("Decompressed string: ",end="")
    for i in range(len):
        char2utf(c_str % 33)
        c_str //= 33
    print()

def read_num(args):
    dec_str(args.num)

def read_str(args):
    res = int("".join(map(lambda x: utf2char(x),args.str[::-1].upper())),33)
    print(f"Compressed string: 0x{res:X} ({res})")

def read_res(args):
    data = open(args.path,"rb")
    size = os.path.getsize(args.path)
    for i in range(size//4):
        dec_str(struct.unpack("I",data.read(4))[0])

parser = argparse.ArgumentParser(description="Converts to and from the compressed string format present in SIA Tilde's Lingo game.")
subparsers = parser.add_subparsers()
decode_parser = subparsers.add_parser("dec",help="Decompress string.")
decode_parser.add_argument("num",type=c_int)
decode_parser.set_defaults(func=read_num)
encode_parser = subparsers.add_parser("enc",help="Compress string.")
encode_parser.add_argument("str",type=str)
encode_parser.set_defaults(func=read_str)
resource_parser = subparsers.add_parser("res",help="Export a file of compressed strings. (e.g. lingo.exe\\.rsrc\\WORDS\\110)")
resource_parser.add_argument("path")
resource_parser.set_defaults(func=read_res)
parser.add_argument("-l","--len",type=int,default=5,help="How long the decompressed string should be, if followed by dec or res (Default = 5)")
args = parser.parse_args()
len = args.len
args.func(args)
