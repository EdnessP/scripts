#!/usr/bin/env python3
# Parses Blu-ray Permanent Information & Control (PIC) data
# Written by Edness   v1.0   2022-08-01

def parse_pic(path):
    def read_int(bytes):
        return int.from_bytes(file.read(bytes), "big")

    total_size = 0
    with open(path, "rb") as file:
        file.seek(0x4)
        while file.read(0x2) == b"DI":
            file.seek(0x2, 1)
            layer = read_int(0x2)
            file.seek(0x2, 1)  # "b" if identifier == "BDR" else " " (???)
            identifier = file.read(0x4).replace(b"\x01", b"").decode()  # BDO, BDU2, XG4, etc.
            file.seek(0x8, 1)  # 1st byte >> 4 == amount of layers?
            if layer == 0:
                total_sectors = read_int(0x4) - 1
            elif read_int(0x4) - 1 != total_sectors:
                # This shouldn't ever happen under normal circumstances
                print("Warning! Total size mismatch! The calculated sizes might be incorrect!")
            layer_sector_start = read_int(0x4) - 2
            layer_sector_end = read_int(0x4)
            file.seek(0x20, 1)  # 0x50 if identifier == "BDR"

            layer_size = layer_sector_end - layer_sector_start
            total_size += layer_size
            print(f"{identifier} - Layer {layer} - Start sector: 0x{layer_sector_start + 2:08X} - End sector: 0x{layer_sector_end:08X} - Layer size: 0x{layer_size:08X} ({(layer_size) * 2048} bytes)")

    actual_size = (total_size - layer_size) + (total_sectors - layer_sector_start)
    print(f"Disc total size (Used): 0x{actual_size:08X} ({actual_size * 2048} bytes) - Disc end sector: 0x{total_sectors + 1:08X}")
    print(f"Disc total size (Full): 0x{total_size:08X} ({total_size * 2048} bytes)")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=str)
    args = parser.parse_args()

    parse_pic(args.path)
