#!/usr/bin/env python3
# Written by Edness   2021-08-20 - 2022-05-06   v1.1

_char = " -/0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_"

_c_char = list(bytes(256))
for _idx in range(len(_char)):
    _c_char[ord(_char[_idx])] = _idx

def decomp_gtid(c_str, id_len=12):
    str = ""
    for i in range(id_len):
        str += _char[c_str % len(_char)]
        c_str //= len(_char)
    return str[::-1].strip()

def comp_gtid(d_str, id_len=12):
    res = 0
    d_str = d_str.ljust(id_len)[::-1]
    for i in range(id_len):
        res += _c_char[ord(str(d_str[i].upper()))] * (len(_char) ** i)
    return res

if __name__ == "__main__":
    import argparse

    def c_int(gtid):
        if gtid.startswith("0x"):
            return int(gtid[2:], 16)
        return int(gtid, 10)

    parser = argparse.ArgumentParser(description="Converts to and from the EA compressed string format present in Burnout games.")
    subparsers = parser.add_subparsers()
    decode_parser = subparsers.add_parser("dec", help="Decompress string.")
    decode_parser.add_argument("gtid", type=c_int)
    decode_parser.set_defaults(func=decomp_gtid)
    encode_parser = subparsers.add_parser("enc", help="Compress string.")
    encode_parser.add_argument("gtid", type=str)
    encode_parser.set_defaults(func=comp_gtid)
    parser.add_argument("-l", "--len", type=int, default=12, help="How long the string should be (Default = 12)")
    args = parser.parse_args()

    gtid = args.func(args.gtid, args.len)
    print(f"Decompressed string: {gtid}" if type(gtid) is str else f"Compressed string: 0x{gtid:X} ({gtid})")
