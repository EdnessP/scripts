#!/usr/bin/env python3
# print FSB-FEV txtm maps for vgmstream
# Written by Edness   v1.0   2026-01-13

import os

def parse_fev(path):
    read_int = lambda: int.from_bytes(file.read(0x4), "little")
    read_str = lambda: "".join(iter(lambda: file.read(0x1).decode("ASCII"), "\x00"))

    def read_fev_str():
        strlen = read_int()
        string = read_str()
        assert len(string) == strlen - 1
        return string

    path = os.path.abspath(path)
    fev_name = os.path.split(path)[1]
    with open(path, "rb") as file:
        magic = file.read(0x4)
        assert magic in {b"FEV1", b"RIFF"}

        # determine file type
        if magic == b"FEV1":
            fev_version = read_int()
            fev_offset = file.tell()
        elif magic == b"RIFF":
            riff_size = read_int() + 0x8
            assert file.read(0x4) == b"FEV "
            assert file.read(0x4) == b"FMT "
            assert read_int() == 0x4  # fmt_size
            fev_version = read_int()
            assert file.read(0x4) == b"LIST"
            list_size = read_int()
            assert file.read(0x4) == b"PROJ"

            fev_offset = 0
            strr_offset = 0
            while file.tell() < riff_size:
                chunk_id = file.read(0x4)
                chunk_size = read_int()
                chunk_offset = file.tell()
                #print(chunk_id, hex(chunk_size), hex(chunk_offset))

                if chunk_id == b"LGCY":
                    fev_offset = chunk_offset
                elif chunk_id == b"STRR":
                    strr_count = read_int()
                    strr_offset = file.tell()
                    strr_buffer = strr_offset + strr_count * 0x4

                if chunk_size & 0x1: chunk_size += 1
                file.seek(chunk_offset + chunk_size)
            assert fev_offset and strr_offset

        assert not fev_version & 0xFF00FFFF and fev_version >= 0x00070000 and fev_version <= 0x00450000

        # parse fev data (see vgmstream fsb_fev.h for further info)
        # https://github.com/vgmstream/vgmstream/blob/master/src/meta/fsb_fev.h
        file.seek(fev_offset)
        if fev_version >= 0x002E0000: file.seek(0x4, 1)
        if fev_version >= 0x00320000: file.seek(0x4, 1)
        if fev_version >= 0x00400000 and magic == b"FEV1":
            file.seek(read_int() * 0x8, 1)
        if fev_version >= 0x00190000: read_fev_str()
        wave_banks = read_int()
        languages = read_int() if fev_version >= 0x00410000 else 1

        for i in range(wave_banks):
            file.seek(0x4, 1)
            if fev_version >= 0x00140000: file.seek(0x4, 1)
            lang_suffixes = list()
            for j in range(languages):
                if fev_version >= 0x003D0000: file.seek(0x8, 1)
                if fev_version >= 0x00410000:
                    idx = read_int()
                    if idx not in lang_suffixes:
                        lang_suffixes.append(idx)
            wavebank_name = read_fev_str()

            if lang_suffixes:
                fev_offset = file.tell()
                for idx in lang_suffixes:
                    file.seek(strr_offset + idx * 0x4)
                    file.seek(strr_buffer + read_int())
                    lang_suffix = read_str()
                    print(f"{wavebank_name + lang_suffix}.fsb: {fev_name}")
                file.seek(fev_offset)
            else:
                print(f"{wavebank_name}.fsb: {fev_name}")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=str, help="path to a FMOD Event (.FEV) file to read")
    args = parser.parse_args()
    parse_fev(args.path)
