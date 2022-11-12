#!/usr/bin/env python3
# Parse Burnout CRASH! CSV files to crop exported PNGs with FFmpeg
# Expects the textures to be exported in the same directory as the CSV
# Set the path to the FFmpeg executable at  FFMPEG_PATH  before running

# Written by Edness   v1.1   2022-07-13 - 2022-11-12

FFMPEG_PATH = r"D:\CTOOLS\ffmpeg\bin\ffmpeg.exe"

import os

def parse_csv(csv_path, ff_path=FFMPEG_PATH):
    if not os.path.exists(ff_path):
        if __name__ == "__main__":
            print("Please specify the correct location of the FFmpeg executable for FFMPEG_PATH in the script!")
        else:
            print("The provided FFmpeg executable was not found!")
        return
    if not os.path.exists(csv_path):
        print("The provided CSV file was not found!")
        return

    # convert to abspath just in case
    ff_path = os.path.abspath(ff_path)
    csv_path = os.path.abspath(csv_path)

    base_path = os.path.split(csv_path)[0]

    with open(csv_path, "r") as file:
        csv_data = file.read().splitlines()

    def ffmpeg_cmd(tex, vf_cmd):
        os.system(f"{ff_path} -i \"{os.path.join(base_path, tex)}.png\" {vf_cmd.strip()} -hide_banner -loglevel error")

    out_dict = {}
    for line in csv_data:
        name, file, x, y, w, h, _w, _h = line.split(",")
        if w != _w or h != _h:
            print(f"Warning! {os.path.join(file, name)} has mismatching dimensions! {w}x{h} vs {_w}x{_h}")

        out_path = f"{os.path.join(base_path, file, name)}.png"
        os.makedirs(os.path.split(out_path)[0], exist_ok=True)
        if file not in out_dict.keys():
            out_dict[file] = ""

        out_cmd = f"-vf crop={w}:{h}:{x}:{y} \"{out_path}\" "
        if len(out_dict[file]) + len(out_cmd) > 8000:  # limit is 8192
            print("Dumping currently queued images...")
            ffmpeg_cmd(file, out_dict[file])
            out_dict[file] = ""

        out_dict[file] += out_cmd
        print(f"Prepared a path for {out_path}")

    print("Dumping remaining images...")
    for file, vf_cmd in out_dict.items():
        if vf_cmd:
            ffmpeg_cmd(file, vf_cmd)

    print("Done!")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("csv_path", type=str)
    args = parser.parse_args()

    parse_csv(args.csv_path)
