#!/usr/bin/env python3
# Jak 3 & Jak X: Combat Racing VAGWAD/VAGDIR extract
# Written by Edness   v1.3   2023-05-10 - 2023-05-14

# Usage:
#   script.py  "X:\PATH\TO\VAGWAD.ENG"
#
# Optional:
#   -o | --output   specify an output folder different from the input path folder
#
#   script.py  "X:\PATH\TO\VAGWAD.INT"  -o "Y:\path\to\output\folder"

import argparse, os

FREQ_MAP = {
    0x2: 16000,
    0x3: 24000,
    0x4: 32000,
    0x6: 48000,
    0x8: 44100,
    0xC: 22050,  # 22000 for ver 3 non-INT?
    0xF: 36000
}

CMP_CHARS = " ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-"

def read_int(file, bytes):
    return int.from_bytes(file.read(bytes), "little")

class DecompressEntry:
    # Reimplemented from the function at  000A09B8  on the IOP
    # of the  OVERLRD2.IRX  module in the PAL version of Jak 3
    def __init__(self, file):
        cmp_int = read_int(file, 0x8)
        cmp_name = cmp_int & 0x3FFFFFFFFFF
        self.stereo = cmp_int >> 42 & 0x1
        self.int_wad = cmp_int >> 43 & 0x1
        self.frequency = cmp_int >> 44 & 0xF  # ???
        self.offset = cmp_int >> 48 << 15  # * 0x8000
        #flags = cmp_int >> 42 & ((1 << 6) - 1)

        name = ""
        tmp_name = cmp_name & 0x1FFFFF
        for idx in range(8):
            if idx == 4:
                tmp_name = cmp_name >> 21
            tmp_name, char_idx = divmod(tmp_name, len(CMP_CHARS))
            name += CMP_CHARS[char_idx]
        self.name = name[::-1].strip() + ".VAG"
        #print(name[::-1], f"{flags:06b}", f"{self.offset:X}")

def extract_vagwad(vagwad, outpath=""):
    if not os.path.exists(vagwad):
        print("Provided VAGWAD file could not be found!")
        return

    split_ext = os.path.splitext(vagwad)
    int_wad = split_ext[1].upper() == ".INT"
    vagdir = os.path.join(os.path.split(vagwad)[0], "VAGDIR.AYB")

    if not os.path.exists(vagdir):
        print("VAGDIR.AYB needs to be in the same directory as the input file!")
        return

    if not outpath:
        outpath = split_ext[0]
    outpath = os.path.abspath(outpath)
    os.makedirs(outpath, exist_ok=True)

    with open(vagwad, "rb") as wad, open(vagdir, "rb") as dir:
        if wad.read(0x4) != b"pGAV":
            print("Input is not a VAGWAD file!")
            return

        if dir.read(0x8) != b"VGWADDIR":
            print("Invalid VAGDIR.AYB file in the same directory as the input file!")
            return

        version = read_int(dir, 0x4)
        entries = read_int(dir, 0x4)
        #dir_size = 0x10 + entries * 0x8

        entries = [DecompressEntry(dir) for entry in range(entries)]
        entries = [entry for entry in entries if entry.int_wad == int_wad]
        entries.sort(key=lambda entry: entry.offset)  # shouldn't be needed but just in case

        if not entries:
            print("No sound file entries for this container!")
            return

        entry_eof = len(entries) - 1
        for idx, entry in enumerate(entries):
            wad.seek(entry.offset)

            if idx == entry_eof:
                vag_data = wad.read()  # until EOF
            else:
                vag_size = entries[idx + 1].offset - entry.offset
                vag_data = wad.read(vag_size)

            if not vag_data.startswith(b"pGAV"):
                print("Failed to decompress entry! (Offset error)")
                return

            # Not even entirely sure if this is even correct but it seems to match most of the time...
            # Only seems to correspond to .ENG/.INT containers, others can have different sample rates
            #wad.seek(entry.offset + 0x10)
            #frequency = read_int(wad, 0x4)
            #if entry.frequency not in FREQ_MAP:
            #    print("New sample rate detected!", frequency)
            #if frequency != FREQ_MAP.get(entry.frequency):
            #    print("Failed to decompress entry! (Sample rate error)", frequency)
            #    return

            #print(entry.name.ljust(12), f"{entry.offset:X}")
            out_vag = os.path.join(outpath, entry.name)
            with open(out_vag, "wb") as vag:
                print("Writing", out_vag)
                vag.write(vag_data)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("vagwad", type=str, help="path to a vagwad container")
    parser.add_argument("-o", "--output", type=str, default="", help="where the output folder should be")
    args = parser.parse_args()

    extract_vagwad(args.vagwad, args.output)
