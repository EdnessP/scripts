#!/usr/bin/env python3
# Parse Burnout CRASH! CSV files to crop exported PNGs with FFmpeg
# Expects the textures to be exported in the same directory as the CSV
# Set the path to the FFmpeg executable at  _ffmpeg_path  before running

# Written by Edness   v1.0   2022-07-13

_ffmpeg_path = r"X:\path\to\ffmpeg\executable"

import os

def parse_csv(csv_path, ff_path=_ffmpeg_path):
    if not os.path.exists(ff_path):
        if __name__ == "__main__":
            print("Please specify the correct location of the FFmpeg executable for _ffmpeg_path in the script!")
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
        os.system(f"{ff_path} -i \"{base_path}\\{tex}.png\" {vf_cmd.strip()} -hide_banner -loglevel error")

    out_dict = {}
    for line in csv_data:
        name, file, x, y, h, w, _h, _w = line.split(",")
        if h != _h or w != _w:
            print(f"Warning! {name} ({file}) has mismatching dimensions!")

        out_path = f"{base_path}\\{file}\\{name}.png"
        os.makedirs(os.path.split(out_path)[0], exist_ok=True)
        if file not in out_dict.keys():
            out_dict[file] = ""

        out_cmd = f"-vf crop={h}:{w}:{x}:{y} \"{out_path}\" "
        if len(out_dict[file]) + len(out_cmd) > 8000:  # limit is 8191
            print("Dumping currently queued images...")
            ffmpeg_cmd(file, out_dict[file])
            out_dict[file] = ""

        out_dict[file] += out_cmd
        print(f"Prepared a path for {out_path}")

    print("Dumping remaining images...")
    for file in out_dict:
        if out_dict[file]:
            ffmpeg_cmd(file, out_dict[file])

    print("Done!")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("csv_path", type=str)
    args = parser.parse_args()

    parse_csv(args.csv_path)
