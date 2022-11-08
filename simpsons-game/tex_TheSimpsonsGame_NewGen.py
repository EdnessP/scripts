# Written by Edness    v1.2
# 2022-05-22  -  2022-11-08

TsgDebug = False

from inc_noesis import *

def registerNoesisTypes():
    handlePS3 = noesis.register("The Simpsons Game [PS3]", ".txd")
    noesis.setHandlerTypeCheck(handlePS3, tsgCheckTypePS3)
    noesis.setHandlerLoadRGBA(handlePS3, tsgLoadTexturePS3)

    handleX360 = noesis.register("The Simpsons Game [X360]", ".itxd")
    noesis.setHandlerTypeCheck(handleX360, tsgCheckTypeX360)
    noesis.setHandlerLoadRGBA(handleX360, tsgLoadTextureX360)

    if TsgDebug:
        noesis.logPopup()
    return True

def tsgCheckTypePS3(data):
    chk = NoeBitStream(data)
    if chk.readUInt() == 0x16 and chk.readUInt() + 0xC == chk.getSize() and chk.readUInt() == 0x1C02002D:
        return True  # Common RW Texture Dictionary container, specifically checking RW 3.7.0.2 build 45
    return False

def tsgCheckTypeX360(data):
    chk = NoeBitStream(data)
    if chk.readBytes(4) == b"uz\x00\x03":
        return True
    return False

def tsgLoadTexturePS3(data, texList):
    tex = NoeBitStream(data)
    rapi.processCommands("-texnorepfn")

    tex.seek(0x28)  # Should be 0x2C but the very last chunk is always missing its ID

    while tex.getOffset() < tex.getSize():
        tex.seek(0x4, 1)  # See above
        texChunkSize = tex.readUInt()
        #if tex.readUInt() != RW_VER_ID:
        #    noesis.doException("Unexpected identifier!")
        tex.seek(0x8, 1)
        texOffset = tex.getOffset()

        tex.setEndian(NOE_BIGENDIAN)
        tex.seek(texOffset + 0x4)
        texName = tex.readString()
        tex.seek(texOffset + 0x4B)
        texFmt = tex.readUByte()
        texWidth = tex.readUShort()
        texHeight = tex.readUShort()
        tex.setEndian(NOE_LITTLEENDIAN)
        tex.seek(texOffset + 0x54)
        texSize = tex.readUInt()

        if TsgDebug:
            print("\nPlayStation 3 texture detected!"
                + "\nTexture name: {}".format(texName)
                + "\nTexture dimensions: {} x {}".format(texWidth, texHeight)
                + "\nTexture offset: 0x{:X}".format(texOffset)
                + "\nTexture size: 0x{:X}".format(texSize)
                + "\nTexture format: 0x{:X}".format(texFmt))

        texData = tex.readBytes(texSize)

        if texFmt == 0x02:
            texFmt = noesis.NOESISTEX_RGBA32
            texData = rapi.imageDecodeRaw(rapi.imageFromMortonOrder(texData, texWidth, texHeight, 1), texWidth, texHeight, "A8")
        elif texFmt == 0x52:
            texFmt = noesis.NOESISTEX_DXT1
        elif texFmt == 0x53:
            texFmt = noesis.NOESISTEX_DXT3
        elif texFmt == 0x54:
            texFmt = noesis.NOESISTEX_DXT5
        elif texFmt == 0x86:
            texFmt = noesis.NOESISTEX_RGBA32
            texData = rapi.imageDecodeRaw(rapi.imageFromMortonOrder(texData, texWidth, texHeight, 4), texWidth, texHeight, "B8G8R8A8")
        else:
            noesis.doException("Unhandled format 0x{:02X}!".format(texFmt))

        texList.append(NoeTexture(texName, texWidth, texHeight, texData, texFmt))
        tex.seek(texOffset + texChunkSize + 0x28)
    return True

def tsgLoadTextureX360(data, texList):
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

        if TsgDebug:
            print("\nXbox 360 texture detected!"
                + "\nTexture name: {}".format(texName)
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
