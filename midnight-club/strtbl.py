#!/usr/bin/env python3
# Exports and imports Angel Studios / Rockstar San Diego .STRTBL files

# Usage: (requires Python 3.9 or newer)
#   strtbl.py  dec  "X:\path\to\file.strtbl"
#   strtbl.py  enc  "X:\path\to\edited.json"

# This script has been tested with the following games:
#
#  Version 1 (Hash v0, Table v0)
#   - Midnight Club: Street Racing
#   - Smuggler's Run (Crazy Bump's: Kattobi Car Battle)
#
#  Version 2 (Hash v0, Table v1)
#   - Midnight Club: Street Racing (Japan)
#   - TransWorld Surf (Next Wave)
#
#  Version 3 (Hash v0, Table v2)
#   - Midnight Club II
#   - Oni 2: Death & Taxes
#   - Red Dead Revolver
#   - Rockstar Games Presents Table Tennis
#   - Smuggler's Run 2: Hostile Territory (Warzones)
#   - SpyHunter 2
#   - Test Drive: Off-Road: Wide Open
#   - TransWorld Surf (Next Wave)
#
#  Version 4 (Hash v1, Table v2)
#   - Midnight Club 3: DUB Edition
#   - Midnight Club 3: DUB Edition Remix
#   - Midnight Club: L.A. Remix
#
#  Version 5 (Hash v2, Table v2)
#   - Midnight Club: Los Angeles
#   - Red Dead Redemption
#   - Red Dead Redemption: Undead Nightmare
#   - Red Dead Redemption (Remaster)

# Written by Edness   v1.3.4   2022-10-09 - 2024-04-01

import json, os, struct

SINT8 = lambda x: x - ((x & 0x80) << 1)
UINT32 = lambda x: x & 0xFFFFFFFF

def hash_v0(str):
    # Reimplemented from function at  003587E8  in
    #          Midnight Club 2 (PS2 PAL)          
    hash = int()
    # Japanese Red Dead Revolver has keys with tabs at the end that are stripped
    # but Test Drive: Off Road has keys with a space at the end not stripped out
    for chr in str.strip("\t\n\r").encode(ENC_LABEL):
    # Test Drive also has keys with ANSI range chars which are treated as signed
        hash = UINT32((hash << 4) + SINT8(chr))
        if mask := hash & 0xF0000000:
            hash ^= mask >> 24 ^ mask
    return hash

def hash_v1(str):
    # Reimplemented from function at  002BE788  in
    # Midnight Club 3: DUB Edition Remix (PS2 PAL)
    hash = int()
    for chr in str.encode(ENC_LABEL):
        hash = UINT32(hash + SINT8(chr))
        hash = UINT32((hash << 10) + hash)
        hash ^= hash >> 6
    hash = UINT32((hash << 3) + hash)
    hash ^= hash >> 11
    return UINT32((hash << 15) + hash)

def hash_v2(str):
    # Reimplemented from function at  0040CDF0  in
    #      Bully / Canis Canem Edit (PS2 PAL)     
    # While Bully doesn't use .STRTBL, it is where
    # I originally reimplemented this hash variant
    # Cross-checked with the function at  821CA9A8
    # in Midnight Club: Los Angeles (Xbox 360 EUR)
    hash = int()
    #return hash_v1(str.lower())
    # v1 but unsigned chars and case and path separator insensitive
    # I wanted to have this function just call hash_v1 but the last
    # minute discovery of v1 also using signed chars threw that off
    for chr in str.replace("\\", "/").encode(ENC_LABEL).lower():
        hash += chr  # the only change lol
        hash = UINT32((hash << 10) + hash)
        hash ^= hash >> 6
    hash = UINT32((hash << 3) + hash)
    hash ^= hash >> 11
    return UINT32((hash << 15) + hash)

HASH_FUNCS = (hash_v0, hash_v1, hash_v2)

#def determine_v0_hash(hashes, label, hash_func):
#    # strtbl v0 has no labels, but this surprisingly can find many hash matches
#    label = "".join([x for x in label if x.isascii()])
#    labels = [label, label.capitalize(), label.title(), re.sub(r"[^0-9A-Za-z\s]", "", label)]
#
#    label = label.split(" ")
#    for i, lab in enumerate(label):
#        lab = list(lab)
#        lab[0] = lab[0].upper()
#        lab = "".join(lab)
#        label[i] = lab
#    label = " ".join(label)
#    labels.append(label)
#
#    for label in labels:
#        hash = hash_func(label.encode())
#        if hash in hashes:
#            return hash
#    return -1

def determine_hash(hashes, labels):
    def get_hash_map(hash_func):
        hash_map = dict()
        for label in labels:
            #if ver_strtbl == 0:
            #    hash = determine_v0_hash(hashes, label, hash_func)
            hash = hash_func(label)
            if hash not in hashes:
                break
            # RDR 360 has a .STRTBL w/ one dupe label with different cases
            if hash in hash_map:
                print(WARN_COLL.format(hash, hash_map[hash], label))
            #assert hash not in hash_map, ERR_COLL.format(hash, hash_map[hash], label)
            hash_map[hash] = label
        else:
            return hash_map

    for ver, func in enumerate(HASH_FUNCS):
        hash_map = get_hash_map(func)
        if hash_map is not None:
            return hash_map, ver
    raise RuntimeError(ERR_ALGO)

#def json_unindent(json_data, start, end):
#    # there's proper workarounds but i cba, so enjoy this horror
#    json_data = json_data.splitlines()
#    for i, ln in enumerate(json_data):
#        if ln.endswith(start):
#            list_data = list()
#            data = json_data.pop(i + 1).strip()
#            while not data.startswith(end):
#                list_data.append(data)
#                data = json_data.pop(i + 1).strip()
#            json_data[i] += " ".join(list_data) + data
#    return "\n".join(json_data)

#def json_unindent_data(json_data):
#    # this is very slow for massive strtbls but still insanely
#    # faster than custom JSONEncoder subclass encoders...  lol
#    print("\nPreparing output 1 of 2...", end="\r")
#    json_data = json_unindent(json_data, "[", "]")
#    print("\nPreparing output 2 of 2...")
#    return json_unindent(json_data, f"\"{KEY_LNG_FONT}\": {{", "}")

def json_fixup_fonts(json_data):
    # and this is 1000x faster than the "safer" method above
    font = f"\"{KEY_LNG_FONT}\": "
    json_data = json_data.splitlines()
    for i, ln in enumerate(json_data):
        if ln.strip().startswith(font):
            ln = ln.split(font)
            ln[-1] = ln[-1][1:-1].replace(r'\"', '"').replace("\\\\", "\\")
            json_data[i] = font.join(ln)
    return "\n".join(json_data)

def exists_prompt(output, prompt):
    if os.path.exists(output):
        response = input(f"Warning! {prompt.format(os.path.split(output)[1])} (Y/N): ")[:1].upper()
        if response != "Y":
            if response != "N":
                print("Error! Invalid response.", end=" ")
            print("Exiting...")
            return False
    return True

def parse_strtbl(path, outpath=str()):
    def read_float():
        return struct.unpack("<f", file.read(0x4))[0]

    def read_int(bytes):
        return int.from_bytes(file.read(bytes), "little")

    def read_str(encoding, *, null_end=True, null_len=False):
        null_term = "\x00".encode(encoding)
        char_size = len(null_term)
        str_len = read_int(0x4)
        if null_end:  # fonts in table v1 and v2 don't include the NULL terminator
            string = b"".join(iter(lambda: file.read(char_size), null_term)).decode(encoding)
            if null_len:  # str_len includes the NULL terminator for the text data length
                str_len -= 1
        else:
            string = file.read(str_len * char_size).decode(encoding)
            if null_len:
                if str_len: str_len -= 1
                string = string[:-1]
        assert len(string) == str_len, ERR_STRLEN
        return string

    path = os.path.abspath(path)
    if not outpath:
        outpath = os.path.splitext(path)[0] + ".json"

    assert os.path.exists(path), ERR_FILE
    if not exists_prompt(outpath, WARN_OUTPUT):
        return

    output = dict()
    file_size = os.path.getsize(path)
    with open(path, "rb") as file:
        # there's no clear header identifier, so stricter checking is done here
        # it's always little endian regardless of platform (GCN, PS3, 360, Wii)
        languages = read_int(0x4)
        assert not languages >> 16, ERR_LANGS
        lang_ptrs = [read_int(0x4) for x in range(languages)]
        assert sorted(lang_ptrs) == lang_ptrs, ERR_LANGS
        label_offs = 0x4 + languages * 0x4
        assert label_offs <= file_size, ERR_LANGS
        for lang in lang_ptrs: assert label_offs <= lang <= file_size, ERR_LANGS

        unique_langs = sorted(set(lang_ptrs))
        if unique_langs[-1] == file_size:
            unique_langs.pop()

        print("Determining .STRTBL revision...")  #end=" ", flush=True

        hashes = list()
        #labels = list()
        if lang_ptrs[0] == label_offs:  # table v0
            file.seek(lang_ptrs[0])
            entries = read_int(0x4)
            for i in range(entries):
                hashes.append(read_int(0x4))
                file.seek(read_int(0x4), 1)  # font (has null terminator)
                #labels.append(read_str(0x2, "UTF-16LE", null_len=True))
                file.seek(read_int(0x4) * 2, 1)
                file.seek(0x8, 1)  # 2 x floats
            hash_map = dict([(x, KEY_HASHED.format(x)) for x in sorted(hashes)])
            ver_strtbl = 0
            ver_hash = 0

        else:  # table v1, v2
            file.seek(label_offs)
            ver_strtbl = read_int(0x4)
            assert ver_strtbl in {256, 512}, ERR_VER
            ver_strtbl >>= 8
            entries = read_int(0x4)
            labels = [read_str(ENC_LABEL) for x in range(entries)]

            file.seek(lang_ptrs[0])
            entries = read_int(0x4)
            for i in range(entries):
                hashes.append(read_int(0x4))
                if ver_strtbl == 2:
                    file.seek(0x2, 1)
                file.seek(read_int(0x4), 1)  # font (no null terminator)
                file.seek(read_int(0x4) * 2, 1)  # string data
                file.seek(0x8, 1)  # 2 x floats
                if ver_strtbl == 2:
                    file.seek(0x2, 1)

            hash_map, ver_hash = determine_hash(hashes, labels)
            # Every 6th gen title has 10 entries, and it started slowly
            # increasing with Wii Table Tennis at 11.  While RGPTT uses
            # hash v0 for whatever reason, afterward everything uses v2
            # which is just v1 except label hashes are case insensitive
            if languages > 10 and ver_hash == 1:
                ver_hash = 2

        #print(f"Hash v{ver_hash}, Table v{ver_strtbl}")

        output[KEY_CONFIG] = dict()
        output[KEY_CONFIG][KEY_CNF_VERSION] = dict()
        output[KEY_CONFIG][KEY_CNF_VERSION][KEY_VER_HASH] = ver_hash
        output[KEY_CONFIG][KEY_CNF_VERSION][KEY_VER_STRTBL] = ver_strtbl

        output[KEY_CONFIG][KEY_CNF_DUPES] = dict()
        for lang in unique_langs:
            dupes = lang_ptrs.count(lang) - 1
            if dupes:
                lang_idx = KEY_LANG.format(lang_ptrs.index(lang))
                output[KEY_CONFIG][KEY_CNF_DUPES][lang_idx] = dupes

        output[KEY_CONFIG][KEY_CNF_LANGS] = languages
        output[KEY_DATA] = dict([(label, dict()) for label in hash_map.values()])

        #for i, lang in enumerate(lang_ptrs):
        for idx, lang in enumerate(unique_langs):  #, 1):
            print(f"Reading language {idx + 1} of {len(unique_langs)}...", end="\r")
            #if lang == file_size: continue
            file.seek(lang)
            entries = read_int(0x4)
            assert entries == len(hash_map), ERR_COUNT
            lang_idx = KEY_LANG.format(idx)
            for i in range(entries):
                label = hash_map[read_int(0x4)]
                if ver_strtbl == 2:
                    size = read_int(0x2)
                font = read_str(ENC_FONT, null_end=False, null_len=(ver_strtbl == 0))
                string = read_str(ENC_TEXT, null_len=True)
                scale_f = [round(read_float(), 5), round(read_float(), 5)]
                if ver_strtbl == 2:
                    # int(scale_f) if it's over 1.0f?  extremely rarely used
                    # currently only seen it used in red dead redemption 360
                    scale_b = [read_int(0x1), read_int(0x1)]
                    #assert not read_int(0x2), ERR_V2DATA

                # I spent sooo much time trying to work out the cleanest way to
                # store these, and still not sure if this is the right decision
                output[KEY_DATA][label][lang_idx] = dict()
                output[KEY_DATA][label][lang_idx][KEY_LNG_TEXT] = string

                #output[KEY_DATA][label][lang_idx][KEY_LNG_FONT] = dict()
                #output[KEY_DATA][label][lang_idx][KEY_LNG_FONT]["name"] = font
                #output[KEY_DATA][label][lang_idx][KEY_LNG_FONT]["scale"] = scale
                #if ver_strtbl == 2:
                #    output[KEY_DATA][label][lang_idx][KEY_LNG_FONT]["size"] = size

                # This is by miles the fastest method to inline output font keys
                font_data = dict()
                font_data[KEY_FNT_NAME] = font
                font_data[KEY_FNT_SCALE_FLOAT] = scale_f
                if ver_strtbl == 2:
                    font_data[KEY_FNT_SCALE_BYTE] = scale_b
                    font_data[KEY_FNT_SIZE] = size
                output[KEY_DATA][label][lang_idx][KEY_LNG_FONT] = json.dumps(font_data)

    # I tried custom NoIndent json encoders, but that was insanely slow.
    print("\nPreparing output...")
    # Red Dead Redemption remaster has a 13MiB .STRTBL, which decodes to
    # 28MiB if using 4 space indentation. And with TABs it becomes 22MiB
    output = json.dumps(output, indent=4, ensure_ascii=False)  # sort_keys=True
    with open(outpath, "w", encoding=ENC_JSON, newline="\n") as file:
        #json.dump(output, file, indent="\t", ensure_ascii=False, cls=MyEncoder)
        file.write(json_fixup_fonts(output))  # easiest hack workaround lol

    print("Done! Output written to", outpath)

def parse_json(path, outpath=str()):
    def write_float(float):
        return file.write(struct.pack("<f", float))

    def write_int(int, bytes):
        return file.write(int.to_bytes(bytes, "little"))

    def write_str(string, encoding, *, null_end=True, null_len=False):
        str_len = len(string)  # pre-encode
        if null_end:
            string += "\x00"
        if null_len and string:
            str_len += 1
            if not null_end:
                string += "\x00"
        write_int(str_len, 0x4)
        file.write(string.encode(encoding))

    path = os.path.abspath(path)
    if not outpath:
        outpath = os.path.splitext(path)[0] + ".strtbl"

    assert os.path.exists(path), ERR_FILE
    if not exists_prompt(outpath, WARN_OUTPUT):
        return

    print("Loading data...")

    with open(path, "r", encoding=ENC_JSON) as file:
        input = json.load(file)

    dupes = input[KEY_CONFIG][KEY_CNF_DUPES]
    languages = input[KEY_CONFIG][KEY_CNF_LANGS]
    ver_strtbl = input[KEY_CONFIG][KEY_CNF_VERSION][KEY_VER_STRTBL]
    hash_func = HASH_FUNCS[input[KEY_CONFIG][KEY_CNF_VERSION][KEY_VER_HASH]]

    # always stored sorted case insensitive by lower-case
    labels = sorted(input[KEY_DATA].keys(), key=str.lower)

    #if ver_strtbl == 0: hash_map = dict([(int(x, 16), x) for x in labels])
    #else: hash_map = dict([(hash_func(x), x) for x in labels])
    hash_map = dict()
    for label in labels:
        if ver_strtbl == 0 and label.startswith(KEY_HASHED_PRE):
            hash = int(label.removeprefix(KEY_HASHED_PRE), 16)
        else:  # user could've manually unhashed tbl v0 labels
            hash = hash_func(label)
        assert hash not in hash_map, ERR_COLL.format(hash, hash_map[hash], label)
        hash_map[hash] = label

    # normally they're stored seemingly randomly
    # but doesn't hurt to sort by ascending hash
    hash_map = dict(sorted(hash_map.items()))

    with open(outpath, "wb") as file:
        file.seek(0x4 + languages * 0x4)
        if ver_strtbl > 0:
            print("Writing labels...")
            write_int(ver_strtbl << 8, 0x4)
            write_int(len(labels), 0x4)
            for label in labels:
                write_str(label, ENC_LABEL)

        print("Writing language data...")
        lang_ptrs = list()
        unique_langs = languages - sum(dupes.values())
        for lang in range(unique_langs):
            #lang_ptrs.append(file.seek(0x0, 2))
            lang_ptrs.append(file.tell())
            lang_idx = KEY_LANG.format(lang)
            lang_counter = int()
            file.seek(0x4, 1)
            for hash in hash_map:
                label = hash_map[hash]
                if lang_idx in input[KEY_DATA][label]:
                    lang_counter += 1
                    entry = input[KEY_DATA][label][lang_idx]
                    write_int(hash, 0x4)
                    if ver_strtbl == 2:
                        write_int(entry[KEY_LNG_FONT][KEY_FNT_SIZE], 0x2)
                    write_str(entry[KEY_LNG_FONT][KEY_FNT_NAME], ENC_FONT, null_end=False, null_len=(ver_strtbl == 0))
                    write_str(entry[KEY_LNG_TEXT], ENC_TEXT, null_len=True)
                    write_float(entry[KEY_LNG_FONT][KEY_FNT_SCALE_FLOAT][0])
                    write_float(entry[KEY_LNG_FONT][KEY_FNT_SCALE_FLOAT][1])
                    if ver_strtbl == 2:
                        write_int(entry[KEY_LNG_FONT][KEY_FNT_SCALE_BYTE][0], 0x1)
                        write_int(entry[KEY_LNG_FONT][KEY_FNT_SCALE_BYTE][1], 0x1)
            if not lang_counter:
                file.seek(-0x4, 1)
            else:  # or just if lang_counter: write num_langs
                assert lang_counter == len(labels), ERR_COUNT
                file.seek(lang_ptrs[-1])
                write_int(lang_counter, 0x4)
                file.seek(0x0, 2)  # eof
            if lang_idx in dupes:
                for i in range(dupes[lang_idx]):
                    lang_ptrs.append(lang_ptrs[-1])
        #while len(lang_ptrs) < languages:
        #for i in range(languages - len(lang_ptrs)):
        #    lang_ptrs.append(file.tell())

        print("Writing container header...")
        file.seek(0x0)
        write_int(languages, 0x4)
        for lang in lang_ptrs:
            write_int(lang, 0x4)

    print("Done! Output written to", outpath)

ENC_LABEL = "1252"
ENC_TEXT = "UTF-16LE"
ENC_FONT = "ASCII"  # ?
ENC_JSON = "UTF-8"

KEY_CONFIG = "config"
KEY_CNF_LANGS = "languages"
KEY_CNF_DUPES = "dupes"
KEY_CNF_VERSION = "version"
KEY_VER_HASH = "hash"
KEY_VER_STRTBL = "table"

KEY_DATA = "data"
KEY_LANG = "Language {:02}"
KEY_LNG_TEXT = "text"
KEY_LNG_FONT = "font"
KEY_FNT_NAME = "name"
KEY_FNT_SCALE_FLOAT = "scale32"
KEY_FNT_SCALE_BYTE = "scale8"
KEY_FNT_SIZE = "size"

KEY_HASHED_PRE = "__hashed_0x"
KEY_HASHED = KEY_HASHED_PRE + "{:07X}"

MSG_COLL = "A hash collision has occurred. The hash 0x{:08X} resolves to:\n- {}\n- {}"

ERR_ALGO = "Error! Failed to determine the hash algorithm."
ERR_COLL = "Error! " + MSG_COLL
ERR_COUNT = "Error! Language entry amount doesn't match label entries."
ERR_FILE = "Error! The specified file could not be found."
ERR_LANGS = "Error! Not a valid .STRTBL string table container."
ERR_STRLEN = "Error! String does not match its expected size."
ERR_VER = "Error! Unsupported .STRTBL version."

WARN_COLL = "Warning! " + MSG_COLL
WARN_OUTPUT = "Output file {} already exists. Overwrite?"

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Converts to and from the .STRTBL string tables used in Angel Studios / Rockstar San Diego games.")
    subparsers = parser.add_subparsers()

    decode_parser = subparsers.add_parser("dec", help="decode from a .STRTBL file")
    decode_parser.add_argument("path", type=str)
    decode_parser.set_defaults(func=parse_strtbl)

    encode_parser = subparsers.add_parser("enc", help="encode to a .STRTBL file")
    encode_parser.add_argument("path", type=str)
    encode_parser.set_defaults(func=parse_json)

    #parser.add_argument("-o", "--output", type=str, default=str(), help=)

    try:
        args = parser.parse_args()
        arg_func, arg_path = args.func, args.path
    except AttributeError:
        print("Error! No arguments given. Use -h or --help to show valid arguments.")
    else:
        arg_func(arg_path)
