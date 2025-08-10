# GameCube Action Replay disc cheat code dumper
# Reimplemented from the function at 800041C8 in
# Action Replay Ultimate Codes for TLOZ:TP (USA)
# Written by Edness   v1.0.1   2025-08-10

import json, os

UINT32 = lambda num: num & 0xFFFFFFFF
ROR = lambda num, bits: UINT32(num >> bits | num << 32 - bits)
ROL = lambda num, bits: UINT32(num << bits | num >> 32 - bits)
BYTESWAP = lambda num: num >> 24 | num >> 8 & 0xFF00 | (num & 0xFF00) << 8 | (num & 0xFF) << 24

KEY_TABLE = (  # SEED = (0x341C849E, 0xFDA4B67B)
    (0x151E213D, 0x34053F12, 0x0316383E, 0x271E343A),
    (0x03293A24, 0x3E1C2F35, 0x3F210237, 0x21112729),
    (0x0D1E1716, 0x213A3D2D, 0x2B0A161B, 0x1E1A291F),
    (0x3A21393F, 0x3837180D, 0x19143107, 0x29233A36),
    (0x393E3F2F, 0x25242012, 0x21192D3C, 0x16362627),
    (0x24212A0E, 0x0B3D2F23, 0x1E2E2E13, 0x0124370D),
    (0x2C1A171A, 0x340E0E1D, 0x2703363B, 0x1A2F1C06),
    (0x16262F1D, 0x39311834, 0x1F35372C, 0x2029111B),
)

XOR_TABLE = (
    (
        0x01010400, 0x00000000, 0x00010000, 0x01010404, 0x01010004, 0x00010404, 0x00000004, 0x00010000,
        0x00000400, 0x01010400, 0x01010404, 0x00000400, 0x01000404, 0x01010004, 0x01000000, 0x00000004,
        0x00000404, 0x01000400, 0x01000400, 0x00010400, 0x00010400, 0x01010000, 0x01010000, 0x01000404,
        0x00010004, 0x01000004, 0x01000004, 0x00010004, 0x00000000, 0x00000404, 0x00010404, 0x01000000,
        0x00010000, 0x01010404, 0x00000004, 0x01010000, 0x01010400, 0x01000000, 0x01000000, 0x00000400,
        0x01010004, 0x00010000, 0x00010400, 0x01000004, 0x00000400, 0x00000004, 0x01000404, 0x00010404,
        0x01010404, 0x00010004, 0x01010000, 0x01000404, 0x01000004, 0x00000404, 0x00010404, 0x01010400,
        0x00000404, 0x01000400, 0x01000400, 0x00000000, 0x00010004, 0x00010400, 0x00000000, 0x01010004,
    ),
    (
        0x80108020, 0x80008000, 0x00008000, 0x00108020, 0x00100000, 0x00000020, 0x80100020, 0x80008020,
        0x80000020, 0x80108020, 0x80108000, 0x80000000, 0x80008000, 0x00100000, 0x00000020, 0x80100020,
        0x00108000, 0x00100020, 0x80008020, 0x00000000, 0x80000000, 0x00008000, 0x00108020, 0x80100000,
        0x00100020, 0x80000020, 0x00000000, 0x00108000, 0x00008020, 0x80108000, 0x80100000, 0x00008020,
        0x00000000, 0x00108020, 0x80100020, 0x00100000, 0x80008020, 0x80100000, 0x80108000, 0x00008000,
        0x80100000, 0x80008000, 0x00000020, 0x80108020, 0x00108020, 0x00000020, 0x00008000, 0x80000000,
        0x00008020, 0x80108000, 0x00100000, 0x80000020, 0x00100020, 0x80008020, 0x80000020, 0x00100020,
        0x00108000, 0x00000000, 0x80008000, 0x00008020, 0x80000000, 0x80100020, 0x80108020, 0x00108000,
    ),
    (
        0x00000208, 0x08020200, 0x00000000, 0x08020008, 0x08000200, 0x00000000, 0x00020208, 0x08000200,
        0x00020008, 0x08000008, 0x08000008, 0x00020000, 0x08020208, 0x00020008, 0x08020000, 0x00000208,
        0x08000000, 0x00000008, 0x08020200, 0x00000200, 0x00020200, 0x08020000, 0x08020008, 0x00020208,
        0x08000208, 0x00020200, 0x00020000, 0x08000208, 0x00000008, 0x08020208, 0x00000200, 0x08000000,
        0x08020200, 0x08000000, 0x00020008, 0x00000208, 0x00020000, 0x08020200, 0x08000200, 0x00000000,
        0x00000200, 0x00020008, 0x08020208, 0x08000200, 0x08000008, 0x00000200, 0x00000000, 0x08020008,
        0x08000208, 0x00020000, 0x08000000, 0x08020208, 0x00000008, 0x00020208, 0x00020200, 0x08000008,
        0x08020000, 0x08000208, 0x00000208, 0x08020000, 0x00020208, 0x00000008, 0x08020008, 0x00020200,
    ),
    (
        0x00802001, 0x00002081, 0x00002081, 0x00000080, 0x00802080, 0x00800081, 0x00800001, 0x00002001,
        0x00000000, 0x00802000, 0x00802000, 0x00802081, 0x00000081, 0x00000000, 0x00800080, 0x00800001,
        0x00000001, 0x00002000, 0x00800000, 0x00802001, 0x00000080, 0x00800000, 0x00002001, 0x00002080,
        0x00800081, 0x00000001, 0x00002080, 0x00800080, 0x00002000, 0x00802080, 0x00802081, 0x00000081,
        0x00800080, 0x00800001, 0x00802000, 0x00802081, 0x00000081, 0x00000000, 0x00000000, 0x00802000,
        0x00002080, 0x00800080, 0x00800081, 0x00000001, 0x00802001, 0x00002081, 0x00002081, 0x00000080,
        0x00802081, 0x00000081, 0x00000001, 0x00002000, 0x00800001, 0x00002001, 0x00802080, 0x00800081,
        0x00002001, 0x00002080, 0x00800000, 0x00802001, 0x00000080, 0x00800000, 0x00002000, 0x00802080,
    ),
    (
        0x00000100, 0x02080100, 0x02080000, 0x42000100, 0x00080000, 0x00000100, 0x40000000, 0x02080000,
        0x40080100, 0x00080000, 0x02000100, 0x40080100, 0x42000100, 0x42080000, 0x00080100, 0x40000000,
        0x02000000, 0x40080000, 0x40080000, 0x00000000, 0x40000100, 0x42080100, 0x42080100, 0x02000100,
        0x42080000, 0x40000100, 0x00000000, 0x42000000, 0x02080100, 0x02000000, 0x42000000, 0x00080100,
        0x00080000, 0x42000100, 0x00000100, 0x02000000, 0x40000000, 0x02080000, 0x42000100, 0x40080100,
        0x02000100, 0x40000000, 0x42080000, 0x02080100, 0x40080100, 0x00000100, 0x02000000, 0x42080000,
        0x42080100, 0x00080100, 0x42000000, 0x42080100, 0x02080000, 0x00000000, 0x40080000, 0x42000000,
        0x00080100, 0x02000100, 0x40000100, 0x00080000, 0x00000000, 0x40080000, 0x02080100, 0x40000100,
    ),
    (
        0x20000010, 0x20400000, 0x00004000, 0x20404010, 0x20400000, 0x00000010, 0x20404010, 0x00400000,
        0x20004000, 0x00404010, 0x00400000, 0x20000010, 0x00400010, 0x20004000, 0x20000000, 0x00004010,
        0x00000000, 0x00400010, 0x20004010, 0x00004000, 0x00404000, 0x20004010, 0x00000010, 0x20400010,
        0x20400010, 0x00000000, 0x00404010, 0x20404000, 0x00004010, 0x00404000, 0x20404000, 0x20000000,
        0x20004000, 0x00000010, 0x20400010, 0x00404000, 0x20404010, 0x00400000, 0x00004010, 0x20000010,
        0x00400000, 0x20004000, 0x20000000, 0x00004010, 0x20000010, 0x20404010, 0x00404000, 0x20400000,
        0x00404010, 0x20404000, 0x00000000, 0x20400010, 0x00000010, 0x00004000, 0x20400000, 0x00404010,
        0x00004000, 0x00400010, 0x20004010, 0x00000000, 0x20404000, 0x20000000, 0x00400010, 0x20004010,
    ),
    (
        0x00200000, 0x04200002, 0x04000802, 0x00000000, 0x00000800, 0x04000802, 0x00200802, 0x04200800,
        0x04200802, 0x00200000, 0x00000000, 0x04000002, 0x00000002, 0x04000000, 0x04200002, 0x00000802,
        0x04000800, 0x00200802, 0x00200002, 0x04000800, 0x04000002, 0x04200000, 0x04200800, 0x00200002,
        0x04200000, 0x00000800, 0x00000802, 0x04200802, 0x00200800, 0x00000002, 0x04000000, 0x00200800,
        0x04000000, 0x00200800, 0x00200000, 0x04000802, 0x04000802, 0x04200002, 0x04200002, 0x00000002,
        0x00200002, 0x04000000, 0x04000800, 0x00200000, 0x04200800, 0x00000802, 0x00200802, 0x04200800,
        0x00000802, 0x04000002, 0x04200802, 0x04200000, 0x00200800, 0x00000000, 0x00000002, 0x04200802,
        0x00000000, 0x00200802, 0x04200000, 0x00000800, 0x04000002, 0x04000800, 0x00000800, 0x00200002,
    ),
    (
        0x10001040, 0x00001000, 0x00040000, 0x10041040, 0x10000000, 0x10001040, 0x00000040, 0x10000000,
        0x00040040, 0x10040000, 0x10041040, 0x00041000, 0x10041000, 0x00041040, 0x00001000, 0x00000040,
        0x10040000, 0x10000040, 0x10001000, 0x00001040, 0x00041000, 0x00040040, 0x10040040, 0x10041000,
        0x00001040, 0x00000000, 0x00000000, 0x10040040, 0x10000040, 0x10001000, 0x00041040, 0x00040000,
        0x00041040, 0x00040000, 0x10041000, 0x00001000, 0x00000040, 0x10040040, 0x00001000, 0x00041040,
        0x10001000, 0x00000040, 0x10000040, 0x10040000, 0x10040040, 0x10000000, 0x00040000, 0x10001040,
        0x00000000, 0x10041040, 0x00040040, 0x10000040, 0x10040000, 0x10001000, 0x10001040, 0x00000000,
        0x10041040, 0x00041000, 0x00041000, 0x00001040, 0x00001040, 0x00040040, 0x10000000, 0x10041000,
    )
)

def decrypt_code(code, addr):
    addr, code = BYTESWAP(addr), BYTESWAP(code)
    addr = ROL(addr, 4)
    temp = (code ^ addr) & 0xF0F0F0F0
    code ^= temp
    addr = ROR(addr ^ temp, 20)
    temp = (code ^ addr) & 0xFFFF0000
    code ^= temp
    addr = ROR(addr ^ temp, 18)
    temp = (code ^ addr) & 0x33333333
    code ^= temp
    addr = ROR(addr ^ temp,  6)
    temp = (code ^ addr) & 0x00FF00FF
    code ^= temp
    addr = ROL(addr ^ temp,  9)
    temp = (code ^ addr) & 0xAAAAAAAA
    addr ^= temp
    code = ROL(code ^ temp,  1)
    for tbl in KEY_TABLE:
        tmp1 = tbl[0] ^ ROR(addr, 4)
        tmp2 = tbl[1] ^ addr
        code ^= XOR_TABLE[6][tmp1 >>  0 & 0x3F] ^ \
                XOR_TABLE[4][tmp1 >>  8 & 0x3F] ^ \
                XOR_TABLE[2][tmp1 >> 16 & 0x3F] ^ \
                XOR_TABLE[0][tmp1 >> 24 & 0x3F] ^ \
                XOR_TABLE[7][tmp2 >>  0 & 0x3F] ^ \
                XOR_TABLE[5][tmp2 >>  8 & 0x3F] ^ \
                XOR_TABLE[3][tmp2 >> 16 & 0x3F] ^ \
                XOR_TABLE[1][tmp2 >> 24 & 0x3F]
        tmp1 = tbl[2] ^ ROR(code, 4)
        tmp2 = tbl[3] ^ code
        addr ^= XOR_TABLE[6][tmp1 >>  0 & 0x3F] ^ \
                XOR_TABLE[4][tmp1 >>  8 & 0x3F] ^ \
                XOR_TABLE[2][tmp1 >> 16 & 0x3F] ^ \
                XOR_TABLE[0][tmp1 >> 24 & 0x3F] ^ \
                XOR_TABLE[7][tmp2 >>  0 & 0x3F] ^ \
                XOR_TABLE[5][tmp2 >>  8 & 0x3F] ^ \
                XOR_TABLE[3][tmp2 >> 16 & 0x3F] ^ \
                XOR_TABLE[1][tmp2 >> 24 & 0x3F]
    addr = ROR(addr, 1)
    temp = (code ^ addr) & 0xAAAAAAAA
    addr ^= temp
    code = ROR(code ^ temp,  9)
    temp = (code ^ addr) & 0x00FF00FF
    addr ^= temp
    code = ROL(code ^ temp,  6)
    temp = (code ^ addr) & 0x33333333
    addr ^= temp
    code = ROL(code ^ temp, 18)
    temp = (code ^ addr) & 0xFFFF0000
    addr ^= temp
    code = ROL(code ^ temp, 20)
    temp = (code ^ addr) & 0xF0F0F0F0
    addr ^= temp
    code = ROR(code ^ temp,  4)
    return BYTESWAP(addr), BYTESWAP(code)

def parse_gccodelist(file, offs, output):
    read_int = lambda bytes: int.from_bytes(file.read(bytes), "little")
    read_str = lambda: "".join(iter(lambda: file.read(0x2).decode("UTF-16LE"), "\x00"))

    file.seek(offs)
    assert file.read(0x10) == b"GAMECUBECODELIST"
    games = read_int(0x4)
    total_codes = read_int(0x4)  # unused

    for i in range(games):
        entry = dict()
        game_name = read_str()
        game_comment = read_str()  # rarely used
        #assert game_name not in output, game_name
        entry[KEY_NAME] = game_name
        if game_comment: entry[KEY_COMM] = game_comment
        entry[KEY_CHTS] = list()
        cheats = read_int(0x4)
        for j in range(cheats):
            cheat = dict()
            cheat_name = read_str()
            cheat_comment = read_str()
            # 18 out of the 28 GC AR discs on Redump failed this or the above check lol
            #assert cheat_name not in output[game_name], ERR_DUPE
            #output[game_name][cheat_name] = dict()
            cheat[KEY_NAME] = cheat_name
            enabled = read_int(0x1)
            assert enabled <= 1, ERR_CODE  # bool, usually used for mastercodes
            # it actually ORs another value with 0x1 if this is any non-zero val
            if cheat_comment: cheat[KEY_COMM] = cheat_comment
            if enabled: cheat[KEY_FLAG] = bool(enabled)
            codes = read_int(0x4)
            assert codes & 0x1 == 0, ERR_CODE  # should always be addr/code pairs
            code_list = ["{:08X} {:08X}".format(*decrypt_code(read_int(0x4), read_int(0x4))) for x in range(codes >> 1)]
            # empty if used as a section header, meta only if used as a directory entry
            if code_list: cheat[KEY_META] = code_list.pop(0)
            if code_list: cheat[KEY_CODE] = code_list
            entry[KEY_CHTS].append(cheat)
        output.append(entry)

def scan_gc_ar_disc(path):
    assert os.path.getsize(path) == 1459978240, ERR_DISC
    offs = int()
    output = list()
    with open(path, "rb") as file:
        serial = file.read(0x6)
        assert serial in {b"GNHE5d", b"DTLX01"}, ERR_DISC
        # at the beginning of disc for the later DTLX01 discs
        base = 0x50000000 if serial == b"GNHE5d" else 0x0
        file.seek(base)
        dol = file.read(0x400000)  # max, also 0x200000 or 0x300000
        assert b"\x34\x1C\x84\x9E\xFD\xA4\xB6\x7B" in dol, ERR_DISC
        # can have multiple GAMECUBECODELIST chunks in code pack discs
        while (offs := dol.find(b"GAMECUBECODELIST", offs)) != -1:
            parse_gccodelist(file, base + offs, output)
            offs += 0x10
    outpath = os.path.splitext(path)[0] + ".json"
    with open(outpath, "w", encoding="UTF-8") as file:
        json.dump(output, file, indent=4, ensure_ascii=False)
    print("Done! Output written to", outpath)

KEY_NAME = "name"
KEY_CODE = "codes"
KEY_CHTS = "cheats"
KEY_FLAG = "enabled"
KEY_COMM = "comment"
KEY_META = "metadata"

ERR_DISC = "Error! Not a valid GameCube Action Replay disc."
ERR_CODE = "Error! Bad cheat code configuration."
ERR_DUPE = "Error! Duplicate entry name found."

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=str, help="path to a disc image to read")
    args = parser.parse_args()
    scan_gc_ar_disc(args.path)
