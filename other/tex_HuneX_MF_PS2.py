# Written by Edness
# 2021-10-28   v1.0

# Suzunone Seven! Rebirth Knot,  Scarlet: Nichijou no Kyoukaisen,
# Fate/stay night: Réalta Nua,  Ramune: Garasu-bin ni Utsuru Umi,
# Maple Colors,  and possibly many other titles with this format.

from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("HuneX MF Textures [PS2]", ".dat")
    noesis.setHandlerTypeCheck(handle, checkType)
    noesis.setHandlerLoadRGBA(handle, loadTexture)
    return 1

def checkType(data):
    bs = NoeBitStream(data)
    if bs.readBytes(4) == b"MF\x00\x00":
        return 1
    return 0

def loadTexture(data, texList):
    bs = NoeBitStream(data)
    rapi.processCommands("-texnorepfn")
    filename = os.path.splitext(rapi.getInputName())[0]

    bs.seek(0x10)
    strLength = bs.readUInt()
    strOffset = bs.readUInt()
    bs.seek(0x20)
    dataLength = bs.readUInt()
    dataOffset = bs.readUInt()
    # both lengths repeated after a null?

    bs.seek(strOffset)
    info = str(bs.readBytes(strLength), "UTF-8").splitlines()
    size = info[1].split(",")
    # might try merging image parts with the info stored here, if possible

    bs.seek(dataOffset + 4)
    dataCount = bs.readUInt()
    bs.seek(8, 1)

    for i in range(dataCount):
        bs.seek(0xC, 1) # last int always = 8?  not indicative of bpp
        texFmt = bs.readUInt()
        texWidth = bs.readUInt()
        texHeight = bs.readUInt()
        palOffset = bs.readUInt() + dataOffset
        texOffset = bs.readUInt() + dataOffset
        curPos = bs.tell()

        bs.seek(palOffset)
        if texFmt == 0x13 or texFmt == 0x14:
            palData = list()
            for j in range(256 if texFmt == 0x13 else 16):
                palData.extend(bs.readBytes(3))
                alpha = bs.readUByte()
                alpha *= 2
                if alpha == 0x100:
                    alpha -= 1
                palData.append(alpha)
            palData = bytes(palData)

        bs.seek(texOffset)
        if texFmt == 0x13:
            texData = rapi.imageDecodeRawPal(bs.readBytes(texWidth * texHeight), palData, texWidth, texHeight, 8, "R8G8B8A8", noesis.DECODEFLAG_PS2SHIFT)
        elif texFmt == 0x14:
            texData = rapi.imageDecodeRawPal(bs.readBytes((texWidth * texHeight) // 2), palData, texWidth, texHeight, 4, "R8G8B8A8")
        else:
            raise RuntimeError("ERROR! Unknown texture format " + hex(texFmt))

        texList.append(NoeTexture((filename + "_texture" + str(i + 1)), texWidth, texHeight, texData, noesis.NOESISTEX_RGBA32))
        bs.seek(curPos)
    return 1
