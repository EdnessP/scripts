#!/usr/bin/env python3
# Parses and prints Blu-ray Permanent Information & Control (PIC) data
# Alternatively, add -d | --dump to print a hexdump of the PIC
# Written by Edness   v1.3   2022-08-01 - 2022-09-26

def parse_pic(path, dump=False):
    def read_int(bytes):
        return int.from_bytes(file.read(bytes), "big")

    def read_const_info():
        total_layers = read_int(0x1) >> 4
        file.seek(0x7, 1)
        total_sectors = read_int(0x4) - 1
        return total_layers, total_sectors

    total_size = 0
    layerbreak = [0]
    with open(path, "rb") as file:
        file.seek(0x4 if file.read(0x2) != b"DI" else 0x0)  # Usually b"\x10\x02", sometimes NULL?
        while file.read(0x2) == b"DI":
            file.seek(0x3, 1)  # 3rd byte is 0x1 if identifier == "BDW" else 0x0?
            layer = read_int(0x1)  # entry would be more appropriate for the BDR/W identifier
            type = file.read(0x1)  # "b" if identifier == "BDR", "c" if "BDW", otherwise " "?
            file.seek(0x1, 1)
            identifier = file.read(0x4).decode()  # BDO, BDU2, XG4, etc.
            #file.seek(0x8, 1)  # 1st byte >> 4 == total layers?
            if layer == 0:
                total_layers, total_sectors = read_const_info()
            elif read_const_info() != (total_layers, total_sectors):
                # This shouldn't ever happen under normal circumstances, I think
                print("Warning - constant data mismatch! The calculated sizes might be incorrect!")
            layer_sector_start = read_int(0x4) - 2
            layer_sector_end = read_int(0x4)
            if type != b" ":
                file.seek(0x44, 1)
                brand = file.read(0x9).replace(b"\x00", b" ").decode()
                identifier += f" - {brand}"
                file.seek(0x3, 1)
            else:
                file.seek(0x20, 1)

            if not dump:
                layer_size = layer_sector_end - layer_sector_start
                total_size += layer_size
                layerbreak.append(layerbreak[-1] + layer_size)
                # Most of this information is completely useless garbage for BDR/BDW, but oh well
                print(f"{repr(identifier)[1:-1]} - Layer {layer} - Start: 0x{layer_sector_start + 2:08X} - End: 0x{layer_sector_end:08X} - Size: 0x{layer_size:08X} ({layer_size} sectors, {layer_size * 2048} bytes)")

        if dump:
            pic_end = file.tell()
            if pic_end % 16 == 0:
                # Redump submission padded PIC hexdump
                if identifier.startswith(("BDO", "XG4")) and pic_end < 0x84:
                    pic_end = 0x84
                elif identifier.startswith("BDU") and pic_end < 0xC4:
                    pic_end = 0xC4
            if pic_end % 4 != 0:
                pic_end = pic_end // 4 * 4
            file.seek(0x0)
            while file.tell() + 0x10 < pic_end:
                print(f"{read_int(0x10):032X}")
            remainder = pic_end % 0x10
            if remainder:
                # This should always just be (4, 8) but I'm future-proofing
                print(f"{read_int(remainder):0{remainder * 2}X}")
        else:
            layerbreak = [str(lbk) for lbk in layerbreak[1:-1]]
            actual_size = (total_size - layer_size) + (total_sectors - layer_sector_start)
            if layerbreak:
                print("Layerbreak{}: {}\n".format("s" if len(layerbreak) > 1 else "", ", ".join(layerbreak)))
            print(f"Total size (Used): 0x{actual_size:08X} ({actual_size} sectors, {actual_size * 2048} bytes) - Disc end: 0x{total_sectors + 1:08X}\n"
                + f"Total size (Full): 0x{total_size:08X} ({total_size} sectors, {total_size * 2048} bytes)\n"
                + f"Total layers: {total_layers}")
            if type != b" ":
                actual_size = -1
                print("\nThis information may be wrong due to it being a burnt disc.")
            return actual_size  # For PIC size validator

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=str)
    parser.add_argument("-d", "--dump", action="store_true")
    args = parser.parse_args()

    parse_pic(args.path, args.dump)
