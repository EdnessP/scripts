# Burnout 2: Point of Impact GameCube, PS2 and Xbox texture plugin
# The  lib_zq_nintendo_tex  library is required to view the GameCube
# textures.  Place it Noesis Python plugins directory to enable it.

# This plugin is brought to you by the Burnout Modding community.
#               burnout.wiki  |  discord.gg/8zxbb4x              

# Written by Edness   2022-06-28 - 2022-11-19   v1.2

PoiDebug = False

from inc_noesis import *

try:
    import lib_zq_nintendo_tex as ntex
    PoiGameCube = True
except ImportError:
    PoiGameCube = False

def registerNoesisTypes():
    handleDic = noesis.register("Burnout 2: Point of Impact - Dictionary", ".dic")
    noesis.setHandlerTypeCheck(handleDic, poiChkDic)
    noesis.setHandlerLoadRGBA(handleDic, poiArcTexDic)

    handleFE = noesis.register("Burnout 2: Point of Impact - Frontend", ".gcn;.ps2" if PoiGameCube else ".ps2")
    noesis.setHandlerTypeCheck(handleFE, poiChkFE)
    noesis.setHandlerLoadRGBA(handleFE, poiArcTexFE)

    if PoiGameCube:
        handleGrd = noesis.register("Burnout 2: Point of Impact - GameCube Textures", ".grd")
        noesis.setHandlerTypeCheck(handleGrd, poiChkGrd)
        noesis.setHandlerLoadRGBA(handleGrd, poiArcTexGrd)

    handleCar = noesis.register("Burnout 2: Point of Impact - Racecars", ".rcf;.rcx")
    noesis.setHandlerTypeCheck(handleCar, poiChkCar)
    noesis.setHandlerLoadRGBA(handleCar, poiArcTexCar)

    handlePss = noesis.register("Burnout 2: Point of Impact - Tracks", ".pss")
    noesis.setHandlerTypeCheck(handlePss, poiChkPss)
    noesis.setHandlerLoadRGBA(handlePss, poiArcTexPss)

    handleTra = noesis.register("Burnout 2: Point of Impact - Traffic", ".tra")
    noesis.setHandlerTypeCheck(handleTra, poiChkTra)
    noesis.setHandlerLoadRGBA(handleTra, poiArcTexTra)

    if PoiDebug:
        noesis.logPopup()
    return True





def poiChkDic(data):
    chk = NoeBitStream(data)
    chk.seek(0x4)
    if chk.readUInt() == 0x16:
        return True
    return False

def poiChkFE(data):
    chk = NoeBitStream(data)
    if chk.readUInt64() == 6:
        return True
    return False

def poiChkGrd(data):
    if data.startswith(bytes(16)):
        return True
    return False

def poiChkCar(data):
    chk, chkEndian = poiGetHdrEndian(data)
    if chk.readUInt() in {
        0xB2CA0009,  # PS2,  Alpha
        0xB2CA000A,  # PS2,  Demo
        0xB2CA000B,  # PS2,  Final
        0xB2CA2001,  # XBOX, Final
        0xB2CA2003,  # GCN,  Final
    } and chk.readUInt() == 0 and chk.readUInt() == chk.getSize():
        return True
    return False

def poiChkPss(data):
    chk, chkEndian = poiGetHdrEndian(data)
    if chk.readUInt() in {
        0xB2300007,  # GCN,  Final
        0xB2300008,  # XBOX, Final
        0xB2300011,  # PS2,  Alpha
        0xB2300012,  # PS2,  Demo
        0xB2300016,  # PS2,  Final
    }:
        return True
    return False

def poiChkTra(data):
    chk, chkEndian = poiGetHdrEndian(data)
    if chk.readUInt() in {
        0xB2DA0007,  # PS2,  Alpha, Demo
        0xB2DA0008,  # PS2,  Final
        0xB2DA2001,  # XBOX, Final
        0xB2DA2004,  # GCN,  Final
    } and chk.readUInt() == 0:
        return True
    return False





def poiGetHdrEndian(data):
    noeEndian = NOE_BIGENDIAN if data.startswith(b"\xB2") else NOE_LITTLEENDIAN
    return NoeBitStream(data, noeEndian), noeEndian

def poiPS2Read4(tex, rSize):
    # Converts 4-bit data to 8-bit
    rData = list()
    for byte in tex.readBytes(rSize):
        # Not using Noesis' readBits() because it is very slow
        rData.extend((byte & 0xF, byte >> 4))
    return bytearray(rData)

def poiPS2Read32(tex, rColors):
    # Fixes alpha channel for 32-bit data
    rData = list()
    for col in range(rColors):
        rData.extend(tex.readBytes(3))
        rAlpha = tex.readUByte() * 2
        if rAlpha == 0x100:
            rAlpha -= 1
        rData.append(rAlpha)
    return bytearray(rData)





def poiTexDicParse(tex, texList, texOffset):
    tex.seek(texOffset + 0xC)

    if tex.readBytes(0x4) == b"PS2\x00":
        texFmt = noesis.NOESISTEX_RGBA32
        tex.seek(texOffset + 0x18)
        nameLen = tex.readUInt()
        tex.seek(texOffset + 0x20)
        texName = noeStrFromBytes(tex.readBytes(nameLen))
        texOffsetNew = tex.getOffset()
        tex.seek(texOffsetNew + 0x28)
        texWidth = tex.readUInt()
        texHeight = tex.readUInt()
        bitDepth = tex.readUInt()
        tex.seek(texOffsetNew + 0x58)
        palOffset = tex.readUInt() + texOffsetNew + 0xC4
        tex.seek(texOffsetNew + 0xC4)
        bmpOffset = tex.getOffset()

        if PoiDebug:
            print("\nPlayStation 2 texture detected!"
                + "\nTexture name: {}".format(texName)
                + "\nTexture offset: 0x{:X}".format(texOffset)
                + "\nTexture data offset: 0x{:X}".format(bmpOffset)
                + "\nTexture dimensions: {} x {}".format(texWidth, texHeight)
                + "\nTexture bit depth: {}".format(bitDepth)
                + "\nPalette data offset: 0x{:X}".format(palOffset))

        if bitDepth == 4:
            texData = poiPS2Read4(tex, texWidth * texHeight // 2)
        elif bitDepth == 8:
            texData = tex.readBytes(texWidth * texHeight)
        else:
            noesis.doException("Unhandled bit-depth: {}".format(bitDepth))

        tex.seek(palOffset)
        if bitDepth == 4:
            palData = poiPS2Read32(tex, 16)
            tex.seek(0x20, 1)
        elif bitDepth == 8:
            palData = poiPS2Read32(tex, 256)
        tex.seek(0x28, 1)

        texData = rapi.imageUntwiddlePS2(texData, texWidth, texHeight, 8)
        texData = rapi.imageDecodeRawPal(texData, palData, texWidth, texHeight, 8, "R8G8B8A8", noesis.DECODEFLAG_PS2SHIFT if bitDepth == 8 else 0)

    else:  # XBOX, 0x5
        tex.seek(texOffset + 0x14)
        texName = tex.readString()
        tex.seek(texOffset + 0x5C)
        texWidth = tex.readUShort()
        texHeight = tex.readUShort()
        tex.seek(texOffset + 0x63)
        texFmt = tex.readUByte()
        texSize = tex.readUInt()

        if PoiDebug:
            print("\nXbox texture detected!"
                + "\nTexture name: {}".format(texName)
                + "\nTexture offset: 0x{:X}".format(texOffset)
                + "\nTexture data offset: 0x{:X}".format(tex.getOffset())
                + "\nTexture size: 0x{:X}".format(texSize)
                + "\nTexture dimensions: {} x {}".format(texWidth, texHeight)
                + "\nTexture format: 0x{:X}".format(texFmt))

        texData = tex.readBytes(texSize)
        if texFmt == 0x0C:
            texFmt = noesis.NOESISTEX_DXT1
        elif texFmt == 0x0E:
            texFmt = noesis.NOESISTEX_DXT3
        elif texFmt == 0x0F:
            texFmt = noesis.NOESISTEX_DXT5
        else:
            noesis.doException("Unhandled format: 0x{:X}".format(texFmt))
        tex.seek(0x18, 1)

    texList.append(NoeTexture(texName, texWidth, texHeight, texData, texFmt))

def poiTexPS2Parse(tex, texList, texOffset, texName, ramAddress):
    tex.seek(texOffset + 0x4)
    bmpOffset = tex.readUInt() - ramAddress
    palOffset = tex.readUInt() - ramAddress
    texWidth = tex.readUInt()
    texHeight = tex.readUInt()
    bitDepth = tex.readUInt()

    if PoiDebug:
        print("\nPlayStation 2 texture detected!"
            + "\nTexture name: {}".format(texName)
            + "\nTexture offset: 0x{:X}".format(texOffset) + (" (0x{:08X} in RAM)".format(texOffset + ramAddress) if ramAddress else "")
            + "\nTexture data offset: 0x{:X}".format(bmpOffset) + (" (0x{:08X} in RAM)".format(bmpOffset + ramAddress) if ramAddress else "")
            + "\nTexture dimensions: {} x {}".format(texWidth, texHeight)
            + "\nTexture bit depth: {}".format(bitDepth)
            + "\nPalette data offset: 0x{:X}".format(palOffset) + (" (0x{:08X} in RAM)".format(palOffset + ramAddress) if ramAddress else ""))

    tex.seek(bmpOffset)
    if bitDepth == 4:
        texData = poiPS2Read4(tex, texWidth * texHeight // 2)
    elif bitDepth == 8:
        texData = tex.readBytes(texWidth * texHeight)
    else:
        noesis.doException("Unhandled bit-depth: {}".format(bitDepth))

    tex.seek(palOffset)
    if bitDepth == 4:
        palData = poiPS2Read32(tex, 16)
    elif bitDepth == 8:
        palData = poiPS2Read32(tex, 256)

    texData = rapi.imageUntwiddlePS2(texData, texWidth, texHeight, 8)
    texData = rapi.imageDecodeRawPal(texData, palData, texWidth, texHeight, 8, "R8G8B8A8", noesis.DECODEFLAG_PS2SHIFT if bitDepth == 8 else 0)
    texList.append(NoeTexture(texName, texWidth, texHeight, texData, noesis.NOESISTEX_RGBA32))

def poiTexGCNParse(tex, texList, texOffset, texName, ramAddress):
    tex.seek(texOffset + 0xC)
    texWidth = tex.readUInt()
    texHeight = tex.readUInt()
    bitDepth = tex.readUInt()
    tex.seek(texOffset + 0x40)
    texFmt = tex.readUInt()
    tex.seek(texOffset + 0x4C)
    palOffset = tex.readUInt() - ramAddress  # i think?
    bmpOffset = tex.readUInt() - ramAddress

    if PoiDebug:
        print("\nGameCube texture detected!"
            + "\nTexture name: {}".format(texName)
            + "\nTexture offset: 0x{:X}".format(texOffset) + (" (0x{:08X} in RAM)".format(texOffset + ramAddress) if ramAddress else "")
            + "\nTexture data offset: 0x{:X}".format(bmpOffset) + (" (0x{:08X} in RAM)".format(bmpOffset + ramAddress) if ramAddress else "")
            + "\nTexture dimensions: {} x {}".format(texWidth, texHeight)
            + "\nTexture bit depth: {}".format(bitDepth)
            + "\nTexture format: 0x{:X}".format(texFmt))

    if 0x8 <= texFmt <= 0xA:
        noesis.doException("Unhandled GCN paletted texture.")

    tex.seek(bmpOffset)
    texData = ntex.readTexture(tex, texWidth, texHeight, texFmt, palOffset)
    texData.name = texName
    texList.append(texData)

def poiTexXboxParse(tex, texList, texOffset, texName, ramAddress):
    tex.seek(texOffset + 0xC)
    texWidth = tex.readUInt()
    texHeight = tex.readUInt()
    bitDepth = tex.readUInt()
    tex.seek(texOffset + 0x34)
    texDataOffset = tex.readUInt() - ramAddress
    tex.seek(texOffset + 0x45)
    texFmt = tex.readUByte()

    tex.seek(texDataOffset + 0x4)
    bmpOffset = tex.readUInt() - ramAddress

    if PoiDebug:
        print("\nXbox texture detected!"
            + "\nTexture name: {}".format(texName)
            + "\nTexture offset: 0x{:X}".format(texOffset) + (" (0x{:08X} in RAM)".format(texOffset + ramAddress) if ramAddress else "")
            + "\nTexture info offset: 0x{:X}".format(texDataOffset) + (" (0x{:08X} in RAM)".format(texDataOffset + ramAddress) if ramAddress else "")
            + "\nTexture data offset: 0x{:X}".format(bmpOffset) + (" (0x{:08X} in RAM)".format(bmpOffset + ramAddress) if ramAddress else "")
            + "\nTexture dimensions: {} x {}".format(texWidth, texHeight)
            + "\nTexture bit depth: {}".format(bitDepth)
            + "\nTexture format: 0x{:X}".format(texFmt))

    tex.seek(bmpOffset)
    if texFmt == 0x0C:
        texFmt = noesis.NOESISTEX_DXT1
        texData = tex.readBytes(texWidth * texHeight // 2)
    elif texFmt == 0x0E:
        texFmt = noesis.NOESISTEX_DXT3
        texData = tex.readBytes(texWidth * texHeight)
    elif texFmt == 0x0F:
        texFmt = noesis.NOESISTEX_DXT5
        texData = tex.readBytes(texWidth * texHeight)
    else:
        noesis.doException("Unhandled format: 0x{:X}".format(texFmt))

    texList.append(NoeTexture(texName, texWidth, texHeight, texData, texFmt))

def poiTexParse(tex, texEndian, texList, nextTex, ramAddress=0x0, nextTexMin=0x0):
    while nextTex > nextTexMin:
        if PoiDebug:
            hdrOffset = nextTex
        tex.seek(nextTex)
        texOffset = tex.readUInt() - ramAddress
        tex.seek(0x4, 1)
        nextTex = tex.readUInt() - ramAddress - 0x8
        prevTex = tex.readUInt() - ramAddress - 0x8
        texName = tex.readString()

        tex.seek(texOffset)
        if tex.readUInt() - ramAddress != texOffset:
            noesis.doException("Pointer mismatch!")

        if tex.readUInt() != 0:
            poiTexPS2Parse(tex, texList, texOffset, texName, ramAddress)
        elif texEndian == NOE_LITTLEENDIAN:
            poiTexXboxParse(tex, texList, texOffset, texName, ramAddress)
        elif PoiGameCube:
            poiTexGCNParse(tex, texList, texOffset, texName, ramAddress)

        if PoiDebug:
            print("Texture header offset: 0x{:X}".format(hdrOffset) + (" (0x{:08X} in RAM)".format(hdrOffset + ramAddress) if ramAddress else ""))
            if nextTex >= 0:
                print("Next texture header: 0x{:X}".format(nextTex) + (" (0x{:08X} in RAM)".format(nextTex + ramAddress) if ramAddress else ""))
            if prevTex >= 0:
                print("Previous texture header: 0x{:X}".format(prevTex) + (" (0x{:08X} in RAM)".format(prevTex + ramAddress) if ramAddress else ""))





def poiArcTexDic(data, texList):
    rapi.processCommands("-texnorepfn")
    arc = NoeBitStream(data)

    texCount = arc.readUInt()

    arc.seek(0x2C)
    for tex in range(texCount):
        texOffset = arc.getOffset()
        poiTexDicParse(arc, texList, texOffset)

        if PoiDebug:
            print("Texture {} of {}".format(tex + 1, texCount))

    return True

def poiArcTexFE(data, texList):
    rapi.processCommands("-texnorepfn")
    arc = NoeBitStream(data)

    arc.seek(0x24)
    if arc.readUInt() == 0:
        arcEndian = NOE_BIGENDIAN
        arc.setEndian(arcEndian)
    else:
        arcEndian = NOE_LITTLEENDIAN

    arc.seek(0x20)
    ramAddress = arc.readUInt() - 0x20

    arc.seek(0x8)
    texOffset = arc.readUInt() - ramAddress - 0x8
    poiTexParse(arc, arcEndian, texList, texOffset, ramAddress)
    return True

def poiArcTexGrd(data, texList):
    rapi.processCommands("-texnorepfn")
    arc = NoeBitStream(data, NOE_BIGENDIAN)

    arc.seek(0x110)
    ramAddress = arc.readUInt() - 0x120
    texCount = arc.readUInt()
    arc.seek(0x128)
    texOffset = arc.readUInt() - ramAddress - 0x8

    poiTexParse(arc, NOE_BIGENDIAN, texList, texOffset, ramAddress, 0x120)
    return True

def poiArcTexCar(data, texList):
    rapi.processCommands("-texnorepfn")
    arc, arcEndian = poiGetHdrEndian(data)

    arcVer = arc.readUInt()

    arc.seek(0x88)
    texCount = arc.readUInt() if arcVer == 0xB2CA2001 else 1
    for tex in range(texCount):
        texOffset = arc.readUInt()
        curTexOffset = arc.getOffset()
        poiTexParse(arc, arcEndian, texList, texOffset)

        if PoiDebug and arcVer == 0xB2CA2001:
            print("Texture {} of {}".format(tex + 1, texCount))

        arc.seek(curTexOffset)

    arc.seek(0xCE8 if arcVer == 0xB2CA2001 else 0xCD8)
    texOffset = arc.readUInt()
    if texOffset:
        poiTexParse(arc, arcEndian, texList, texOffset)
    return True

def poiArcTexPss(data, texList):
    rapi.processCommands("-texnorepfn")
    arc, arcEndian = poiGetHdrEndian(data)

    arcVer = arc.readUInt()

    arc.seek(0x10)
    texCount = arc.readUInt()

    # It's consistent at 0x1C0 in PS2 and Xbox, but in GCN it changes per file.
    # Assuming the offset never exceeds 0x1000 and is always aligned to it too.
    texArrayOffset = arc.readUInt()
    ramAddress = texArrayOffset & 0xFFFFF000
    texArrayOffset ^= ramAddress

    arc.seek(texArrayOffset)
    for tex in range(texCount):
        texOffset = arc.readUInt() - ramAddress
        curTexOffset = arc.getOffset()
        poiTexParse(arc, arcEndian, texList, texOffset, ramAddress)

        if PoiDebug:
            print("Texture {} of {}".format(tex + 1, texCount))

        arc.seek(curTexOffset)
    return True

def poiArcTexTra(data, texList):
    rapi.processCommands("-texnorepfn")
    arc, arcEndian = poiGetHdrEndian(data)

    arcVer = arc.readUInt()

    # I hate this whole thing, but everything is tied to RAM addresses and nothing makes sense
    arc.seek(0x6C)  # 3 pointers to the wheels texture, hardcoded(?)
    texOffset = 0x18000 | arc.readUInt() & 0xFFF
    ramAddress = arc.readUInt() - texOffset
    poiTexParse(arc, arcEndian, texList, texOffset, ramAddress)

    # Hardcoding this because I can't figure it out (works for their appropriate systems)
    texStart, texSeek = {
        NOE_BIGENDIAN: (0xFE0, 0xF40),
        NOE_LITTLEENDIAN: (0xFA0, 0xF00),
    }.get(arcEndian)

    arc.seek(texStart)
    #while arc.getOffset() < texOffsetWheels:
    for tex in range(25):  # int @ 0x17740 ??? (PS2)
        curTexOffset = arc.getOffset()
        texOffset = arc.readUInt() - ramAddress
        poiTexParse(arc, arcEndian, texList, texOffset, ramAddress)

        if PoiDebug:
            print("Texture {} of {}".format(tex + 1, 25))

        arc.seek(curTexOffset + texSeek)
    return True
