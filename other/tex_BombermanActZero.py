# Bomberman: Act Zero XPR2 textures (.XPR, .DAT)

# There are other XPR2 plugins out there, but I couldn't be bothered
# to debug them to find out why they refused to load these textures.

# Written by Edness
# 2022-05-31   v1.2

# Set SwizzleOverride to True if a texture looks garbled.
SwizzleOverride = False
XprDebug = False

from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("Bomberman: Act Zero Textures", ".dat;.xpr")
    noesis.setHandlerTypeCheck(handle, xprCheckType)
    noesis.setHandlerLoadRGBA(handle, xprLoadTexture)

    if XprDebug:
        noesis.logPopup()
    return True

def xprCheckType(data, isLoad=False):
    chk = NoeBitStream(data)

    # The XPR2 section isn't always at the start of the file (.DAT)
    # The DAT files seem to have other small files stored before the
    # XPR file; sometimes it's some sort of a BMP-like format, but I
    # won't deal with that for now.  Seems like too much of a pain.
    xprOffset = 0x0
    while xprOffset < chk.getSize():
        chk.seek(xprOffset)
        if chk.readBytes(4) == b"XPR2":
            chk.seek(0x8, 1)
            return True if not isLoad else xprOffset
        xprOffset += 0x1000
    return False

def xprLoadTexture(data, texList):
    rapi.processCommands("-texnorepfn")
    xprOffset = xprCheckType(data, isLoad=True)
    xpr = NoeBitStream(data[xprOffset:], NOE_BIGENDIAN)

    xpr.seek(0x4)
    xprHdrSize = xpr.readUInt()
    xprTexSize = xpr.readUInt()
    if xpr.readBytes(4) != b"FOfp":
        xpr.seek(-0x4, 1)
    xprInfoSize = xpr.tell()

    # Every pointer from here on is off by the XPR2 info header
    xpr = NoeBitStream(data[xprInfoSize + xprOffset:], NOE_BIGENDIAN)
    texCount = xpr.readUInt()
    for tex in range(texCount):
        if xpr.readBytes(4) != b"TX2D":
            noesis.doException("Unexpected header!")

        infoOffset = xpr.readUInt()
        infoSize = xpr.readUInt()
        texSize = xpr.readUInt()
        texOffset = xpr.readUInt() + xprHdrSize
        texHeight = xpr.readUInt()
        texWidth = xpr.readUInt()
        xpr.seek(0x4, 1)
        nameOffset = xpr.readUInt()
        curHdrPos = xpr.tell()

        xpr.seek(infoOffset + infoSize - 0x11)
        texFmt = xpr.readUByte()
        xpr.seek(nameOffset)
        texName = xpr.readString()
        if not texName:
            texName = "UnnamedTexture{:02}".format(tex + 1)

        xpr.seek(texOffset)
        if texWidth > 128 and texWidth % 128 != 0 and texFmt <= 0x54:
            # Fix textures with an unusual width and a larger buffer size.

            # Usually if a texture has to go through this, it's not swizzled
            # but I've seen two identical texture headers, neither of which
            # would've had to go here but one was swizzled and one wasn't...
            padWidth = (texWidth // 128 + 1) * 128
            blockSize = 8 if texFmt == 0x52 else 16
            wPad = texWidth if texWidth % 4 == 0 else (texWidth // 4 + 1) * 4
            hPad = texHeight if texHeight % 4 == 0 else (texHeight // 4 + 1) * 4
            texData = list()
            for i in range(hPad // 4):
                texData.extend(xpr.readBytes(wPad // 4 * blockSize))
                xpr.seek((padWidth - wPad) // 4 * blockSize, 1)
            texData = bytes(texData)
            texUntile = False
        else:
            texData = xpr.readBytes(texSize)
            texUntile = True

        if SwizzleOverride:
            texUntile = not texUntile

        if XprDebug:
            print("\nTexture name: {}".format(texName)
                + "\nTexture dimensions: {} x {}".format(texWidth, texHeight)
                + "\nTexture format: 0x{:X}".format(texFmt)
                + "\nTexture size: 0x{:X}".format(texSize)
                + "\nTexture offset: 0x{:X}".format(texOffset + xprOffset + xprInfoSize)
                + "\nTexture name offset: 0x{:X}".format(nameOffset + xprOffset + xprInfoSize)
                + "\nTexture info offset: 0x{:X}".format(infoOffset + xprOffset + xprInfoSize)
                + "\nTexture {} of {}".format(tex + 1, texCount))

        if texFmt == 0x52:
            texFmt = noesis.NOESISTEX_DXT1
            texData = rapi.swapEndianArray(texData, 2)
            if texUntile:
                texData = rapi.imageUntile360DXT(texData, texWidth, texHeight, 8)
        elif texFmt == 0x53:
            texFmt = noesis.NOESISTEX_DXT3
            texData = rapi.swapEndianArray(texData, 2)
            if texUntile:
                texData = rapi.imageUntile360DXT(texData, texWidth, texHeight, 16)
        elif texFmt == 0x54:
            texFmt = noesis.NOESISTEX_DXT5
            texData = rapi.swapEndianArray(texData, 2)
            if texUntile:
                texData = rapi.imageUntile360DXT(texData, texWidth, texHeight, 16)
        elif texFmt == 0x71:
            texFmt = noesis.NOESISTEX_RGBA32
            texData = rapi.imageUntile360DXT(rapi.swapEndianArray(texData, 2), texWidth, texHeight, 16)
            texData = rapi.imageDecodeDXT(texData, texWidth, texHeight, noesis.FOURCC_ATI2)
        elif texFmt == 0x7B:
            texFmt = noesis.NOESISTEX_RGBA32
            texData = rapi.imageUntile360DXT(rapi.swapEndianArray(texData, 2), texWidth, texHeight, 8)
            texData = rapi.imageDecodeDXT(texData, texWidth, texHeight, noesis.FOURCC_BC4)
        elif texFmt == 0x7C:
            texFmt = noesis.NOESISTEX_RGBA32
            texData = rapi.imageUntile360DXT(rapi.swapEndianArray(texData, 2), texWidth, texHeight, 8)
            texData = rapi.imageDecodeDXT(texData, texWidth, texHeight, noesis.FOURCC_DXT1NORMAL)
        elif texFmt == 0x86:
            texFmt = noesis.NOESISTEX_RGBA32
            texData = rapi.imageDecodeRaw(rapi.imageUntile360Raw(texData, texWidth, texHeight, 4), texWidth, texHeight, "A8R8G8B8")
        else:
            noesis.doException("Unhandled format 0x{:02X}!".format(texFmt))

        texList.append(NoeTexture(texName, texWidth, texHeight, texData, texFmt))
        xpr.seek(curHdrPos)

    if XprDebug:
        print("\nXPR offset: 0x{:X}".format(xprOffset)
            + "\nXPR header size: 0x{:X}".format(xprHdrSize)
            + "\nXPR data size: 0x{:X}".format(xprTexSize))
    return True
