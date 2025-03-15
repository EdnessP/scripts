#!/usr/bin/env python3
# Fix Saints Row 2 exported text files with internal patch charlist

# Usage:
#   Decode to readable:
#       script.py  dec  "X:\path\to\static.xml"  "Y:\path\to\charlist.txt"
#   Encode to internal:
#       script.py  enc  "X:\path\to\static.xml"  "Y:\path\to\charlist.txt"

# Written by Edness   v1.0.1   2025-03-15

def convert_text(path, charlist, decode):
    #encode = lambda x: x.to_bytes(0x2).decode("UTF-16BE")
    #decode = lambda x: int.from_bytes(x.encode("UTF-16BE"))

    print("Parsing file...")

    with open(charlist, "r") as file:
        char = file.read().splitlines()

    # lazy text file filtering, could be improved(?)
    char = [x for x in char if not x.startswith("//")]
    assert char[0].startswith("count=")
    num_chars = int(char.pop(0)[6:])
    assert len(char) == num_chars
    char = [int(x) for x in char]

    with open(path, "r", encoding="UTF-8") as file:
        text = list(file.read())

    # can't just do full replaces because that'll override already converted chars
    # might be solveable if i go through the list backwards?  w/e, some other time
    #for i, c in enumerate(char, 32):
    #    i, c = encode(i), encode(c)
    #    text = text.replace(i, c) if decode else text.replace(c, i)

    # but this is so much slower than the solution above...
    for i, c in enumerate(text):
        if not i: continue  # lol (horrible BOM skip)
        c = int.from_bytes(c.encode("UTF-16BE"))
        if c >= 0x20:  # not an ascii control char
            c = char[c - 0x20] if decode else char.index(c) + 0x20
            text[i] = int.to_bytes(c, 0x2).decode("UTF-16BE")

    with open(path, "w", encoding="UTF-8") as file:
        file.write("".join(text))

    print("Done! Text file converted.")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Converts Saints Row 2 exported text files with internal character list")
    subparsers = parser.add_subparsers(description="To view additional help for each subparser, add -h | --help after it")

    decode_parser = subparsers.add_parser("dec", help="convert to readable format")
    decode_parser.add_argument("path", type=str, help="path to the output file")
    decode_parser.add_argument("char", type=str, help="path to the charlist file")
    decode_parser.set_defaults(decode=True)

    encode_parser = subparsers.add_parser("enc", help="convert to internal format")
    encode_parser.add_argument("path", type=str, help="path to the output file")
    encode_parser.add_argument("char", type=str, help="path to the charlist file")
    encode_parser.set_defaults(decode=False)

    args = parser.parse_args()
    try:
        func_args = [args.path, args.char, args.decode]
    except AttributeError:
        print("Error! Bad arguments given. Use -h or --help to show valid arguments.")
    else:
        convert_text(*func_args)
