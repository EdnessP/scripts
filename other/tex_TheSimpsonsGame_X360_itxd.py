# Written by Edness    v1.1
# 2022-05-22  -  2022-05-27

# Also check out the PS3 version of this script at
# https://forum.xentax.com/viewtopic.php?f=18&t=19360

from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("The Simpsons Game [X360]", ".itxd")
    noesis.setHandlerTypeCheck(handle, tsgCheckType)
    noesis.setHandlerLoadRGBA(handle, tsgLoadTexture)

    #noesis.logPopup()
    return True

def tsgCheckType(data):
    chk = NoeBitStream(data)
    if chk.readBytes(4) == b"uz\x00\x03":
        return True
    return False

def tsgLoadTexture(data, texList):
    tex = NoeBitStream(data, NOE_BIGENDIAN)
    rapi.processCommands("-texnorepfn")

    tex.seek(0x18)
    texInfo = tex.readUInt()
    texInfoEnd = tex.readUInt()  # Offset of the last entry

    while texInfo <= texInfoEnd:
        # 0x0, 0x4 = next, prev tex offset
        tex.seek(texInfo + 0x8)
        texName = tex.readString()
        tex.seek(texInfo + 0x7C)
        texWidth = tex.readUInt()
        texHeight = tex.readUInt()
        tex.seek(texInfo + 0xB4)
        texSize = tex.readUInt()
        texOffset = tex.readUInt()
        tex.seek(texInfo + 0xBF)
        texFmt = tex.readUByte()

        print("\nTexture name: {}".format(texName)
            + "\nTexture dimensions: {} x {}".format(texWidth, texHeight)
            + "\nTexture offset: 0x{:X}".format(texOffset)
            + "\nTexture size: 0x{:X}".format(texSize)
            + "\nTexture format: 0x{:X}".format(texFmt))

        tex.seek(texOffset)
        texData = tex.readBytes(texSize)

        if texFmt == 0x02:
            texFmt = noesis.NOESISTEX_RGBA32
            texData = rapi.imageDecodeRaw(rapi.imageUntile360Raw(texData, texWidth, texHeight, 1), texWidth, texHeight, "A8")
        elif texFmt == 0x52:
            texFmt = noesis.NOESISTEX_DXT1
            texData = rapi.imageUntile360DXT(rapi.swapEndianArray(texData, 2), texWidth, texHeight, 8)
        elif texFmt == 0x53:
            texFmt = noesis.NOESISTEX_DXT3
            texData = rapi.imageUntile360DXT(rapi.swapEndianArray(texData, 2), texWidth, texHeight, 16)
        elif texFmt == 0x54:
            texFmt = noesis.NOESISTEX_DXT5
            texData = rapi.imageUntile360DXT(rapi.swapEndianArray(texData, 2), texWidth, texHeight, 16)
        elif texFmt == 0x86:
            texFmt = noesis.NOESISTEX_RGBA32
            texData = rapi.imageDecodeRaw(rapi.imageUntile360Raw(texData, texWidth, texHeight, 4), texWidth, texHeight, "A8R8G8B8")
        else:
            noesis.doException("Unhandled format 0x{:02X}!".format(texFmt))

        texList.append(NoeTexture(texName, texWidth, texHeight, texData, texFmt))
        texInfo += 0x100
    return True
