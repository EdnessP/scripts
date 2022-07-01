# Burnout 1 PS2 and Xbox texture plugin
# These formats broke me on a spiritual level and I just
# really couldn't be bothered to make it work flawlessly

# The PS2 .PSS files have an infrequent tendency to skip some textures
# but the PS2 .TRA files have a tendency to duplicate a few textures.
# This doesn't affect Burnout 2: Point of Impact's script in any way!

# Written by Edness   2022-07-01   v1.0

BoDebug = False

from inc_noesis import *

def registerNoesisTypes():
    handleDic = noesis.register("Burnout 1 - Dictionary", ".dic")
    noesis.setHandlerTypeCheck(handleDic, boChkDic)
    noesis.setHandlerLoadRGBA(handleDic, boArcTexDic)

    handleFnt = noesis.register("Burnout 1 - Fonts", ".fnt")
    noesis.setHandlerTypeCheck(handleFnt, boChkFnt)
    noesis.setHandlerLoadRGBA(handleFnt, boArcTexFnt)

    handleCar = noesis.register("Burnout 1 - Player Cars", ".ac2;.ac3;.ac4;.pc1;.pc2;.pcf")
    noesis.setHandlerTypeCheck(handleCar, boChkCar)
    noesis.setHandlerLoadRGBA(handleCar, boArcTexCar)

    handlePss = noesis.register("Burnout 1 - Track Environments", ".pss")
    noesis.setHandlerTypeCheck(handlePss, boChkPss)
    noesis.setHandlerLoadRGBA(handlePss, boArcTexPss)

    handlePxw = noesis.register("Burnout 1 - Tracks", ".p1w;.p2w;.psw")
    noesis.setHandlerTypeCheck(handlePxw, boChkPxw)
    noesis.setHandlerLoadRGBA(handlePxw, boArcTexPxw)

    handleTra = noesis.register("Burnout 1 - Traffic", ".tra")
    noesis.setHandlerTypeCheck(handleTra, boChkTra)
    noesis.setHandlerLoadRGBA(handleTra, boArcTexTra)

    if BoDebug:
        noesis.logPopup()
    return True

def boChkDic(data):
    chk = NoeBitStream(data)
    if chk.readUInt() == 0x16:
        return True
    return False

def boChkFnt(data):
    chk = NoeBitStream(data)
    if chk.readUInt() == 0x915:
        dicOffset = chk.readUInt() + 0xC
        if dicOffset < chk.getSize():
            chk.seek(dicOffset)
            if chk.readUInt() == 0x16:
                return True
    return False

def boChkCar(data):
    chk = NoeBitStream(data)
    if chk.readBytes(0xC)[::4] == b"\x90\xC0\xF0":
        return True
    return False

def boChkPss(data):
    chk = NoeBitStream(data)
    if chk.readUInt() == 0xF00D0003:
        return True
    return False

def boChkPxw(data):
    chk = NoeBitStream(data)
    if chk.readUInt() in {0xAF20000A, 0xAF22000A}:
        return True
    return False

def boChkTra(data):
    # There is literally no identifier here, all I can do
    # is make it fail if it spots the B2 Traffic.TRA file
    # I could in theory do the same thing as  boChkCar
    # but I don't have different B1 TRA files handy...
    chk = NoeBitStream(data)
    #if chk.readUInt64() in {0xB2DA0007, 0xB2DA0008, 0xB2DA2001}:
    #    return False

    # Well, it's something...
    if chk.readUShort() == 0xFE10:
        return True
    return False





def boPS2Read4(tex, rSize):
    # Converts 4-bit data to 8-bit
    rData = list()
    for byte in tex.readBytes(rSize):
        # Not using Noesis' readBits() because it is very slow
        rData.extend((byte & 0xF, byte >> 4))
    return bytearray(rData)

def boPS2Read32(tex, rColors):
    # Fixes alpha channel for 32-bit data
    rData = list()
    for col in range(rColors):
        rData.extend(tex.readBytes(3))
        rAlpha = tex.readUByte() * 2
        if rAlpha == 0x100:
            rAlpha -= 1
        rData.append(rAlpha)
    return bytearray(rData)





def boTexDicParse(tex, texList, texOffset):
    tex.seek(texOffset + 0xC)

    if tex.readBytes(0x4) == b"PS2\x00":
        texFmt = noesis.NOESISTEX_RGBA32
        tex.seek(texOffset + 0x18)
        nameLen = tex.readUInt()
        tex.seek(texOffset + 0x20)
        texName = noeStrFromBytes(tex.readBytes(nameLen))
        texOffsetNew = tex.tell()
        tex.seek(texOffsetNew + 0x28)
        texWidth = tex.readUInt()
        texHeight = tex.readUInt()
        bitDepth = tex.readUInt()
        tex.seek(texOffsetNew + 0x58)
        palOffset = tex.readUInt() + texOffsetNew + 0x74
        tex.seek(texOffsetNew + 0x74)
        if tex.readUInt64() == 0x1000000000000003:
            texSwizzle = True
            tex.seek(0x48, 1)
            palOffset += 0x50
        else:
            texSwizzle = False
            tex.seek(-0x8, 1)
        bmpOffset = tex.tell()

        if BoDebug:
            print("\nPlayStation 2 texture detected!"
                + "\nTexture name: {}".format(texName)
                + "\nTexture offset: 0x{:X}".format(texOffset)
                + "\nTexture data offset: 0x{:X}".format(bmpOffset)
                + "\nTexture dimensions: {} x {}".format(texWidth, texHeight)
                + "\nTexture bit depth: {}".format(bitDepth)
                + "\nPalette data offset: 0x{:X}".format(palOffset))

        if bitDepth == 4:
            texData = boPS2Read4(tex, texWidth * texHeight // 2)
        elif bitDepth == 8:
            texData = tex.readBytes(texWidth * texHeight)
        elif bitDepth == 32:
            texData = boPS2Read32(tex, texWidth * texHeight)
        else:
            noesis.doException("Unhandled bit-depth: {}".format(bitDepth))

        if bitDepth <= 8:
            tex.seek(palOffset)
            if bitDepth == 4:
                palData = boPS2Read32(tex, 16)
                tex.seek(0x20, 1)
            elif bitDepth == 8:
                palData = boPS2Read32(tex, 256)
            if texSwizzle:
                texData = rapi.imageUntwiddlePS2(texData, texWidth, texHeight, 8)
            texData = rapi.imageDecodeRawPal(texData, palData, texWidth, texHeight, 8, "R8G8B8A8", noesis.DECODEFLAG_PS2SHIFT if bitDepth == 8 else 0)

    else:  # XBOX, 0x5
        tex.seek(texOffset + 0x14)
        texName = tex.readString()
        tex.seek(texOffset + 0x5C)
        texWidth = tex.readUShort()
        texHeight = tex.readUShort()
        tex.seek(texOffset + 0x61)
        texMips = tex.readUByte()
        tex.seek(texOffset + 0x63)
        texFmt = tex.readUByte()
        if not texFmt:
            palData = tex.readBytes(0x400)
        texSize = tex.readUInt()

        if BoDebug:
            print("\nXbox texture detected!"
                + "\nTexture name: {}".format(texName)
                + "\nTexture offset: 0x{:X}".format(texOffset)
                +("\nPalette data offset: 0x{:X}".format(tex.tell() - 0x400) if not texFmt else "")
                + "\nTexture data offset: 0x{:X}".format(tex.tell())
                + "\nTexture size: 0x{:X}".format(texSize)
                + "\nTexture dimensions: {} x {}".format(texWidth, texHeight)
                + "\nTexture format: 0x{:X}".format(texFmt)
                + "\nTexture mip maps: {}".format(texMips))

        texData = tex.readBytes(texSize)
        for mip in range(texMips - 1):
            mipSize = tex.readUInt()
            tex.seek(mipSize, 1)

        if texFmt == 0x00:
            texFmt = noesis.NOESISTEX_RGBA32
            texData = rapi.imageFromMortonOrder(texData, texWidth, texHeight, 1)
            texData = rapi.imageDecodeRawPal(texData, palData, texWidth, texHeight, 8, "B8G8R8A8")
        elif texFmt == 0x0C:
            texFmt = noesis.NOESISTEX_DXT1
        elif texFmt == 0x0E:
            texFmt = noesis.NOESISTEX_DXT3
        elif texFmt == 0x0F:
            texFmt = noesis.NOESISTEX_DXT5
        else:
            noesis.doException("Unhandled format: 0x{:X}".format(texFmt))

    tex.seek(0x4, 1)  # this is jank and should probably be improved
    tex.seek(tex.readUInt() + 0x10, 1)

    texList.append(NoeTexture(texName, texWidth, texHeight, texData, texFmt))

def boTexParse(tex, texList, hdrOffset, ramAddress):
    tex.seek(hdrOffset)
    texOffset = tex.readUInt() - ramAddress
    if texOffset == hdrOffset:
        noName = True
        texName = "__unnamed_texture"
    else:
        noName = False
        if texOffset < 0:
            return

        tex.seek(hdrOffset + 0x10)
        texName = tex.readString()
        tex.seek(hdrOffset + 0x30)
        texNameAlt = tex.readString()
        if texNameAlt != "" and texName != texNameAlt:
            texName += " ({})".format(texNameAlt)

    #boTexPS2Parse
    tex.seek(texOffset)
    if tex.readUInt() - ramAddress != texOffset:
        noesis.doException("Pointer mismatch!")

    bmpOffset = tex.readUInt() - ramAddress
    palOffset = tex.readUInt() - ramAddress
    texWidth = tex.readUInt()
    texHeight = tex.readUInt()
    bitDepth = tex.readUInt()

    if BoDebug:
        print("\nPlayStation 2 texture detected!"
            + "\nTexture name: {}".format(texName)
            +("\nTexture header offset: 0x{:X} (0x{:X} in RAM)".format(hdrOffset, hdrOffset + ramAddress) if not noName else "")
            + "\nTexture offset: 0x{:X} (0x{:X} in RAM)".format(texOffset, texOffset + ramAddress)
            + "\nTexture data offset: 0x{:X} (0x{:X} in RAM)".format(bmpOffset, bmpOffset + ramAddress)
            + "\nTexture dimensions: {} x {}".format(texWidth, texHeight)
            + "\nTexture bit depth: {}".format(bitDepth)
            +("\nPalette data offset: 0x{:X} (0x{:X} in RAM)".format(palOffset, palOffset + ramAddress) if bitDepth <= 8 else ""))

    tex.seek(bmpOffset)
    if bitDepth == 4:
        texData = boPS2Read4(tex, texWidth * texHeight // 2)
    elif bitDepth == 8:
        texData = tex.readBytes(texWidth * texHeight)
    elif bitDepth == 32:
        texData = boPS2Read32(tex, texWidth * texHeight)
    else:
        noesis.doException("Unhandled bit-depth: {}".format(bitDepth))

    if bitDepth <= 8:
        tex.seek(palOffset)
        if bitDepth == 4:
            palData = boPS2Read32(tex, 16)
            tex.seek(0x20, 1)
        elif bitDepth == 8:
            palData = boPS2Read32(tex, 256)
        texData = rapi.imageUntwiddlePS2(texData, texWidth, texHeight, 8)
        texData = rapi.imageDecodeRawPal(texData, palData, texWidth, texHeight, 8, "R8G8B8A8", noesis.DECODEFLAG_PS2SHIFT if bitDepth == 8 else 0)

    texList.append(NoeTexture(texName, texWidth, texHeight, texData, noesis.NOESISTEX_RGBA32))





def boArcParseSubBlock(arc, blkOffset, ramAddress, fileSize, texOffsetList):
    # I have no clue what in the world all these chained pointers 
    # going all over the place are.
    # I gave up trying to manually work this out, so I just looked
    # at what the game's disassembled instructions do.
    arc.seek(blkOffset)
    if arc.readUInt() == 0:
        return

    arc.seek(blkOffset + 0x18)
    dataOffset = arc.readUInt() - ramAddress
    if dataOffset in range(fileSize):
        arc.seek(dataOffset + 0x10)
        arc.seek(arc.readUInt() - ramAddress)
        while True:
            texOffset = arc.readUInt() - ramAddress
            if texOffset not in range(fileSize):
                break

            curTexPos = arc.tell()

            arc.seek(texOffset)
            texOffset = arc.readUInt() - ramAddress
            if texOffset in range(fileSize) and texOffset not in texOffsetList:
                arc.seek(texOffset)
                arc.seek(arc.readUInt() - ramAddress)
                texOffsetList.append(texOffset)

            arc.seek(curTexPos)

def boArcParseTopBlock(arc, blkOffset, ramAddress, fileSize, texOffsetList):
    # same as above
    for blk in range(3):
        arc.seek(blkOffset + blk * 4 + 0x4)
        subOffset = arc.readUInt() - ramAddress - 0x40
        if subOffset in range(fileSize):
            boArcParseSubBlock(arc, subOffset, ramAddress, fileSize, texOffsetList)

def boArcTexDic(data, texList, dicOffset=0x0):
    rapi.processCommands("-texnorepfn")
    arc = NoeBitStream(data)

    arc.seek(dicOffset + 0x28)
    while arc.tell() < arc.getSize():
        texOffset = arc.tell()
        boTexDicParse(arc, texList, texOffset)
    return True

def boArcTexFnt(data, texList):
    arc = NoeBitStream(data)
    arc.seek(0x4)
    dicOffset = arc.readUInt() + 0xC
    boArcTexDic(data, texList, dicOffset)
    return True

def boArcTexCar(data, texList):
    rapi.processCommands("-texnorepfn")
    arc = NoeBitStream(data)

    fileSize = arc.getSize()
    ramAddress = arc.readUInt() - 0x90
    texOffsetList = []
    arc.seek(0x0)
    while True:
        blkOffset = arc.readUInt() - ramAddress
        if blkOffset not in range(fileSize):
            break
        curHdrPos = arc.tell()
        boArcParseSubBlock(arc, blkOffset, ramAddress, fileSize, texOffsetList)
        arc.seek(curHdrPos)

    for texOffset in texOffsetList:
        boTexParse(arc, texList, texOffset, ramAddress)
    return True

def boArcTexPss(data, texList):
    rapi.processCommands("-texnorepfn")
    arc = NoeBitStream(data)

    arc.seek(0x860)  # 1st texture pointer to itself
    ramAddress = arc.readUInt() - 0x860

    arc.seek(0x8)  # usually it's just 7 pointers, sometimes 6
    blkOffsetList = [arc.readUInt() - ramAddress for tex in range(20)]
    arc.seek(0x84)
    blkOffsetList.append(arc.readUInt() - ramAddress)

    texOffsetList = []
    fileSize = arc.getSize()
    for blkOffset in blkOffsetList:
        if blkOffset > 0:
            arc.seek(blkOffset)
            if arc.readUInt() == 2:
                boArcParseTopBlock(arc, blkOffset, ramAddress, fileSize, texOffsetList)
            elif blkOffset not in texOffsetList:
                texOffsetList.append(blkOffset)

    for texOffset in texOffsetList:
        boTexParse(arc, texList, texOffset, ramAddress)

    # While there are pointers to these few textures in the file somewhere
    # I can't be bothered to deal with this stupid ass format any longer

    # This can find all the remaining textures except for
    #   TRACKS\EU4\EU4.PSS\bridges
    #   TRACKS\REV\EU2\EU2.PSS\bridges
    #   TRACKS\REV\USA2\USA2.PSS\skyline1
    # due to a chunk of floats in-between interrupting them
    # HOWEVER there are identical duplicates in other PSSes
    #if readAhead:
    #    while True:
    #        arcSkip = arc.readBytes(16)
    #        while arcSkip == bytes(16):
    #            arcSkip = arc.readBytes(16)
    #        if arcSkip.endswith(bytes(12)):
    #            boTexParse(arc, texList, arc.tell() - 16, ramAddress)
    #        else: break
    return True

def boArcTexPxw(data, texList):
    rapi.processCommands("-texnorepfn")
    arc = NoeBitStream(data)

    arc.seek(0x7FC)
    texOffset = arc.readUInt() + arc.tell()
    arc.seek(texOffset)
    while arc.tell() < arc.getSize():
        arc.seek(-0x8, 1)
        ramAddress = arc.readUInt() - arc.tell() - 0x4
        texSize = arc.readUInt()
        texOffset = arc.tell()
        if texOffset > 0 and ramAddress > 0:
            boTexParse(arc, texList, texOffset, ramAddress)
        arc.seek(texOffset + texSize)
    return True

def boArcTexTra(data, texList):
    rapi.processCommands("-texnorepfn")
    arc = NoeBitStream(data)

    texOffsetList = []
    fileSize = arc.getSize()
    # Both Demo and Retail have the same address, so I don't
    # know where to reliably retrieve the RAM location from.
    ramAddress = 0x01890000
    for tex in range(80):
        arc.seek(tex * 0x4)
        texOffset = arc.readUInt() - ramAddress
        if texOffset > 0:
            arc.seek(texOffset)
            if arc.readUInt() == 2:
                boArcParseTopBlock(arc, texOffset, ramAddress, fileSize, texOffsetList)
            elif texOffset not in texOffsetList:
                texOffsetList.append(texOffset)

    for texOffset in texOffsetList:
        boTexParse(arc, texList, texOffset, ramAddress)
    return True
