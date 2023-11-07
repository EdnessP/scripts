#!/usr/bin/env python3
# Generates a RSTM sound file for Midnight Club 3: DUB Edition and Bully
# The input type is usually meant to be ADS/SS2, but WAV is also accepted.
# If the input file is WAV, you must specify a path either for MFAudio or
# PS2STR from the PS2 SDK.  PS2STR is given priority if both files exist.

MFAUDIO_PATH = r"X:\path\to\MFAudio.exe"
PS2STR_PATH = r"X:\path\to\ps2str.exe"

# Usage:
#     rstm_build.py  "X:\path\to\sound.ads"
#   Optional:
#     -o  | --output    <str> Path to the output file;  defaults to the input folder
#     -lf | --loopfull        Loop the entire sound file
#     -ls | --loopstart <int> Set manual loop start position in frames (28 samples each)
#     -le | --loopend   <int> Set manual loop end position in frames (28 samples each)
#       rstm_build.py  "/path/to/sound.wav"  -o "/path/to/sound.rsm"  -lf

# Written by Edness   2022-02-26 - 2023-11-07   v1.4

import os, random, string

def read_int(file, bytes):
    return int.from_bytes(file.read(bytes), "little")

def write_int(file, int, bytes):
    return file.write(int.to_bytes(bytes, "little"))

def build_rstm(path, output=str(), loopfull=False, loop_start=int(), loop_end=int()):
    path = os.path.abspath(path)
    if not output:
        output = os.path.splitext(path)[0] + ".rsm"
    output = os.path.abspath(output)

    #if sample_rate:
    #    assert sample_rate <= 48000, ERR_FREQ

    with open(path, "rb") as file:
        header = file.read(0x4)
        assert header in {b"RIFF", b"SShd"}, ERR_TYPE

        if header == b"SShd":
            ads_path = path
            ads_delete = False
        else:  # convert WAV to ADS/SS2
            ps2str = PS2STR_PATH.strip() and os.path.isfile(PS2STR_PATH)
            mfaudio = MFAUDIO_PATH.strip() and os.path.isfile(MFAUDIO_PATH)
            assert ps2str or mfaudio, ERR_FILE
            ads_delete = True

            base_path = os.path.split(output)[0]
            tmp_name = "tmp_" + "".join(random.choices(string.digits + string.ascii_letters, k=12))
            ads_path = os.path.join(base_path, tmp_name + ".ads")

            assert read_int(file, 0x4) + 0x8 == os.path.getsize(path), ERR_SIZE
            assert file.read(0x4) == b"WAVE", ERR_TYPE

            chunk_name = file.read(0x4)
            chunk_size = read_int(file, 0x4)
            chunk_offs = file.tell()

            assert chunk_name == b"fmt ", ERR_TYPE

            format = read_int(file, 0x2)
            assert format == 0x0001, ERR_WAVE  # in {0x0001, 0xFFFE}
            channels = read_int(file, 0x2)
            assert 1 <= channels <= 2, ERR_WAVE
            sample_rate = read_int(file, 0x4)
            assert sample_rate <= 48000, ERR_WAVE
            #if not sample_rate:
            #    sample_rate = frequency
            file.seek(0x22)
            bit_depth = read_int(file, 0x2)
            assert bit_depth == 16, ERR_WAVE

            while chunk_name != b"data":
                file.seek(chunk_offs + chunk_size)
                assert file.tell() < os.path.getsize(path), ERR_DATA
                chunk_name = file.read(0x4)
                chunk_size = read_int(file, 0x4)
                chunk_offs = file.tell()
            print(f"Found the data section at 0x{chunk_offs - 0x8:X}.", end="  ")

            # This is mainly for MFAudio, which is hardcoded to find the data section at 0x24
            if chunk_offs == 0x2C and format == 0x0001:
                print("Seems to be in the expected format layout.")
                wav_path = path
                wav_delete = False
            else:
                print("Seems to be stored in a different layout.  Rebuilding file...")
                wav_path = os.path.join(base_path, tmp_name + ".wav")
                wav_delete = True
                file.seek(chunk_offs - 0x8)
                data = file.read(chunk_size + 0x8)
                file.seek(0x16)
                with open(wav_path, "wb") as tmp:
                    tmp.write(b"RIFF")
                    write_int(tmp, len(data) + 0x24, 0x4)
                    tmp.write(b"WAVEfmt ")
                    write_int(tmp, 0x10, 0x4)
                    write_int(tmp, 0x1, 0x2)
                    tmp.write(file.read(0xE))
                    tmp.write(data)

            if ps2str:
                # -sr:{sample_rate} doesn't resample it on PS2STR, just pitches it up/down
                os.system(f"{PS2STR_PATH} e -o -v -a -is:16 \"{wav_path}\" \"{ads_path}\"")
            elif mfaudio:
                os.system(f"{MFAUDIO_PATH} /OTSS2C /OF{sample_rate} /OC{channels} /OI10 \"{wav_path}\" \"{ads_path}\"")

            if wav_delete:
                os.remove(wav_path)

    #with open(ads_path, "rb") as ads, open(output, "wb") as rsm:
    with open(ads_path, "rb") as file:
        header = file.read(0x4)
        assert header == b"SShd", ERR_ADS2
        sshd_size = read_int(file, 0x4)
        encoding = read_int(file, 0x4)
        assert encoding == 0x10, ERR_ADS2
        sample_rate = read_int(file, 0x4)
        assert sample_rate <= 48000, ERR_ADS2
        channels = read_int(file, 0x4)
        assert 1 <= channels <= 2, ERR_ADS2
        interleave = read_int(file, 0x4)
        assert interleave == 0x10, ERR_ADS2
        # not using loop flags from here, use -lf/-ls/-le instead
        #loop_start = read_int(file, 0x4)
        #loop_end = read_int(file, 0x4)
        #if loop_start != 0xFFFFFFFF: loop_start *= 0x10
        #if loop_end != 0xFFFFFFFF: loop_end *= 0x10
        file.seek(sshd_size + 0x8)
        header = file.read(0x4)
        assert header == b"SSbd", ERR_ADS2
        ssbd_size = read_int(file, 0x4)
        assert not ssbd_size & 0xF, ERR_SIZE
        rsm_data = bytearray(file.read(ssbd_size))
        frame_size = interleave * channels
        # wipe SPU flags written by MFAudio, Bully is very unhappy with these
        rsm_data[0x1::0x10] = bytes(len(rsm_data) // 0x10)
        # wipe SPU initialization frame written by PS2STR, RSMs don't have these
        if rsm_data.startswith(bytes(frame_size)):
            rsm_data = rsm_data[frame_size:]
        # wipe SPU end flag frame written by both MFAudio and PS2STR, also not needed
        rsm_data = rsm_data[:-frame_size]

    os.makedirs(os.path.split(output)[0], exist_ok=True)
    with open(__file__) as file: rsm_header = file.read(0x800)
    rsm_header = rsm_header[rsm_header.index(" ".join([chr(x) for x in (35, 87)])) + 0x2:]
    rsm_header = rsm_header.splitlines()[0].split(); rsm_header = " ".join(rsm_header[:3]), rsm_header[-1]
    rsm_header = " - ".join((os.path.split(__file__)[1], *rsm_header[::-1])).encode("UTF-8")
    with open(output, "wb") as file:
        file.write(b"RSTM")
        file.seek(0x8)
        write_int(file, sample_rate, 0x4)
        write_int(file, channels, 0x4)
        file.seek(0x18)
        write_int(file, len(rsm_data), 0x4)
        if loopfull:
            write_int(file, 0x0, 0x4)
            write_int(file, len(rsm_data) - frame_size, 0x4)
        elif loop_start or loop_end:
            write_int(file, loop_start * frame_size, 0x4)  # can be 0x0
            if loop_end < 0: loop_end = (len(rsm_data) - frame_size) // frame_size + loop_end
            write_int(file, loop_end * frame_size if loop_end else len(rsm_data) - frame_size, 0x4)
        else:  # no looping
            write_int(file, 0x0, 0x4)
            write_int(file, len(rsm_data), 0x4)
        file.seek(0x800 - len(rsm_header))
        file.write(rsm_header)
        file.write(rsm_data)

    if ads_delete:
        os.remove(ads_path)
    print("Success! RSM written to", output)

ERR_ADS2 = "Error! Unsupported ADS/SS2 format.\nInput needs to be a PS-ADPCM encoded stream up to 2 channels with 16 byte interleaving."
ERR_DATA = "Error! Couldn't locate the WAV data section."
ERR_FILE = "Error! Please specify the location of MFAudio in MFAUDIO_PATH or PS2STR in PS2STR_PATH in the script."
ERR_FREQ = "Error! Invalid sample rate."
ERR_SIZE = "Error! Invalid file size."
ERR_TYPE = "Error! Not a WAV or ADS/SS2 input file."
ERR_WAVE = "Error! Unsupported WAV format.\nInput needs to be a signed 16-bit PCM uncompressed WAV up to 2 channels."

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Builds Rockstar San Diego RSTM sound files")
    parser.add_argument("path", type=str, help="path to a WAV or ADS/SS2 sound file")
    parser.add_argument("-o", "--output", type=str, default=str(), help="path to the output file")
    #parser.add_argument("-sr", "--samplerate", type=int, default=int(), help="override the sample rate (WAV only)")
    parser.add_argument("-lf", "--loopfull", action="store_true", help="loop the whole stream")
    parser.add_argument("-ls", "--loopstart", type=int, default=int(), help="set the loop start frame (28 samples each)")
    parser.add_argument("-le", "--loopend", type=int, default=int(), help="set the loop end frame (28 samples each)")

    args = parser.parse_args()
    build_rstm(args.path, args.output, args.loopfull, args.loopstart, args.loopend)
