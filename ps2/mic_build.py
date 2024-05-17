#!/usr/bin/env python3
# Generates a .MIC/.MIH+.MIB sound file, used
# in PS2 games with the MultiStreamer library

# The input sound is supposed to be a 16-bit PCM WAV file

MFAUDIO_PATH = r"X:\path\to\MFAudio.exe"

# Usage:
#     mic_build.py  "X:\path\to\sound.wav"
#   Optional:
#     -i  | --interleave <int> How many frames per channel before switching
#     -sr | --samplerate <int> Resample to a different sample rate
#     -s  | --split            Build a split .MIH+.MIB instead of a .MIC file
#       mic_build.py  "X:\path\to\sound.wav"  -i 0x5B80  -sr 44100

# Written by Edness   2024-05-16 - 2024-05-17   v1.0.1

import os, random, string  #, subprocess

def read_int(file, bytes):
    return int.from_bytes(file.read(bytes), "little")

def write_int(file, int, bytes):
    return file.write(int.to_bytes(bytes, "little"))

def build_mic(path, interleave=int(), resample_rate=int(), split=False):
    assert MFAUDIO_PATH.strip() and os.path.isfile(MFAUDIO_PATH), ERR_FILE

    if resample_rate:
        assert resample_rate <= 48000, ERR_FREQ

    path = os.path.abspath(path)
    output = os.path.splitext(path)[0]  # + ".mic"

    wav_size = os.path.getsize(path)
    with open(path, "rb") as file:
        header = file.read(0x4)
        assert header == b"RIFF", ERR_TYPE

        base_path = os.path.split(output)[0]
        #while True:  # i could really use a do-while loop in python right about now
        tmp_name = "tmp_" + "".join(random.choices(string.digits + string.ascii_letters, k=12))
        raw_path = os.path.join(base_path, tmp_name + ".raw")
            #if not os.path.exists(raw_path): break

        assert read_int(file, 0x4) + 0x8 == wav_size, ERR_SIZE
        assert file.read(0x4) == b"WAVE", ERR_TYPE

        chunk_name = file.read(0x4)
        chunk_size = read_int(file, 0x4)
        chunk_offs = file.tell()

        assert chunk_name == b"fmt ", ERR_TYPE

        format = read_int(file, 0x2)
        assert format == 0x0001, ERR_WAVE  # in {0x0001, 0xFFFE}
        channels = read_int(file, 0x2)
        assert 1 <= channels <= 2, ERR_WAVE
        if channels != 1:
            assert interleave and not interleave & 0xF, ERR_INTR
        sample_rate = read_int(file, 0x4)
        assert sample_rate <= 48000, ERR_WAVE
        if resample_rate:
            sample_rate = resample_rate
        file.seek(0x22)
        bit_depth = read_int(file, 0x2)
        assert bit_depth == 16, ERR_WAVE

        while chunk_name != b"data":
            file.seek(chunk_offs + chunk_size)
            assert file.tell() < wav_size, ERR_DATA
            chunk_name = file.read(0x4)
            chunk_size = read_int(file, 0x4)
            chunk_offs = file.tell()
        print(f"Found the data section at 0x{chunk_offs - 0x8:X}.", end="  ")

        # MFAudio is hardcoded to find the data section at 0x24
        if chunk_offs == 0x2C:  # and format == 0x0001
            print("Seems to be in the expected format layout.")
            wav_path = path
            wav_delete = False
        else:
            print("Seems to be stored in a different layout.  Rebuilding file...")
            wav_path = os.path.join(base_path, tmp_name + ".wav")
            wav_delete = True
            file.seek(chunk_offs - 0x8)
            data = file.read(chunk_size + 0x8)
            file.seek(0x16)  # lazy riff parser
            with open(wav_path, "wb") as tmp:
                tmp.write(b"RIFF")
                write_int(tmp, len(data) + 0x24, 0x4)
                tmp.write(b"WAVEfmt ")
                write_int(tmp, 0x10, 0x4)
                write_int(tmp, 0x1, 0x2)
                tmp.write(file.read(0xE))
                tmp.write(data)

    #command = [MFAUDIO_PATH, "/OTRAWC", f"/OF{sample_rate}", f"/OC{channels}", f'"{wav_path}" "{raw_path}"']
    #if channels != 1: command.insert(-2, f"/OI{interleave:X}")  # am aware subprocess handles paths with spaces, but mfaudio
    #subprocess.check_call(command)
    # mfaudio is dumb in how it handles the output path that subprocess simply will not cut it
    cmd = f"\"{MFAUDIO_PATH}\" /OTRAWC /OF{sample_rate} /OC{channels} "
    if channels != 1: cmd += f"/OI{interleave:X} "
    cmd += f"\"{wav_path}\" \"{raw_path}\""
    os.system(f"\"{cmd}\"")

    if wav_delete:
        os.remove(wav_path)

    with open(raw_path, "rb") as file:
        raw_data = bytearray(file.read())
    raw_size = len(raw_data)
    os.remove(raw_path)

    spu_end_frame = b"\x00\x07" + b"\x77" * 0xE

    block_size_full = interleave * channels
    block_size_last = raw_data.rfind(spu_end_frame) % interleave
    blocks = raw_size // block_size_full

    assert block_size_last != -1 and not block_size_last & 0xF, ERR_ENDF
    assert raw_data.count(spu_end_frame) == channels, ERR_ENDF
    # a bunch of other safetychecks would be good here like
    # checking if the end frame matches on all channels but

    # wipe SPU end flag frames and SPU flags
    raw_data = raw_data.replace(spu_end_frame, bytes(0x10))
    raw_data[0x1::0x10] = bytes(len(raw_data) // 0x10)

    with open(output + (".mih" if split else ".mic"), "wb") as file:
        write_int(file, 0x40, 0x4)  # header size, always 64 bytes
        #write_int(file, block_size_last << 8 | 0x20, 0x4)
        write_int(file, 0x20, 0x1)
        write_int(file, block_size_last, 0x3)
        write_int(file, channels, 0x4)
        write_int(file, sample_rate, 0x4)
        write_int(file, interleave, 0x4)
        write_int(file, blocks, 0x4)
        if split:
            file.seek(0x3F)
            file.write(b"\x00")
            print("Header file written to:", file.name)
            with open(output + ".mib", "wb") as tmp:
                tmp.write(raw_data)
                print("Sound file written to:", tmp.name)
        else:
            file.seek(0x40)
            file.write(raw_data)
            print("Sound file written to:", file.name)

    print("Done!")

ERR_ENDF = "Error! Invalid end frame."
ERR_DATA = "Error! Couldn't locate the WAV data section."
ERR_FILE = "Error! Please specify the location of MFAudio in MFAUDIO_PATH in the script."
ERR_FREQ = "Error! Invalid sample rate."
ERR_INTR = "Error! Invalid interleave size - must be a multiple of 16."
ERR_SIZE = "Error! Invalid file size."
ERR_TYPE = "Error! Not a valid WAV input file."
ERR_WAVE = "Error! Unsupported WAV format.\nInput needs to be a signed 16-bit PCM uncompressed WAV up to 2 channels."

if __name__ == "__main__":
    import argparse

    hex = lambda x: int(x, 16) if x.startswith("0x") else int(x)

    parser = argparse.ArgumentParser(description="Builds Sony MultiStreamer .MIC/.MIH+.MIB sound files")
    parser.add_argument("path", type=str, help="path to a WAV sound file")
    #parser.add_argument("-o", "--output", type=str, default=str(), help="path to the output file")
    parser.add_argument("-i", "--interleave", type=hex, default=int(), help="how many frames per channel before switching")
    parser.add_argument("-sr", "--samplerate", type=hex, default=int(), help="resample to a different sample rate")
    parser.add_argument("-s", "--split", action="store_true", help="build a split .MIH+.MIB instead of a .MIC file")

    args = parser.parse_args()
    build_mic(args.path, args.interleave, args.samplerate, args.split)
