# Xbox 360 XPR2 Textures for Bomberman: Act Zero

# There are other XPR2 plugins out there, but I couldn't be bothered
# to debug them to find out why they refused to load these textures.

# Written by Edness
# 2022-05-31   v1.0

XprDebug = False

from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("Bomberman: Act Zero [X360]", ".dat;.xpr")
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
            return True if not isLoad else xprOffset
        xprOffset += 0x1000
    return False

def xprLoadTexture(data, texList):
    rapi.processCommands("-texnorepfn")
    xprOffset = xprCheckType(data, True)
    xpr = NoeBitStream(data[xprOffset:], NOE_BIGENDIAN)

    xpr.seek(0x4)
    xprHdrSize = xpr.readUInt()
    xprTexSize = xpr.readUInt()
    # xpr.readBytes(4) == b"FOfp"

    # Everything from here on out is off by 16 bytes
    xpr = NoeBitStream(data[16 + xprOffset:], NOE_BIGENDIAN)
    texCount = xpr.readUInt()
    for tex in range(texCount):
        if xpr.readBytes(4) != b"TX2D":
            noesis.doException("Unexpected header!")
        infoOfs = xpr.readUInt()
        xpr.seek(0x4, 1)  # 0x34?
        texSize = xpr.readUInt()
        texOffset = xpr.readUInt() + xprHdrSize
        texHeight = xpr.readUInt()
        texWidth = xpr.readUInt()
        xpr.seek(0x4, 1)
        nameOfs = xpr.readUInt()
        curHdrPos = xpr.tell()

        xpr.seek(nameOfs)
        texName = xpr.readString()
        xpr.seek(infoOfs)
        # Sometimes they're 32-bit, sometimes they're 16-bit...
        infoHdr = xpr.readUInt()
        if infoHdr == 3:
            xpr.seek(infoOfs + 0x23)
        elif infoHdr >> 16 == 3:
            xpr.seek(infoOfs + 0x17)
        else:
            noesis.doException("Unhandled info header!")
        texFmt = xpr.readUByte()

        # The one texture I saw that had an unusual width was also not tiled.
        # It could also be the value at infoOfs + 0x1C (in the 32-bit layout)
        # which I saw was 0x2 specifically for that texture, but I'm unsure.
        xpr.seek(texOffset)
        if texWidth > 128 and texWidth % 128 != 0 and texFmt <= 0x54:
            # Fix textures with an unusual width and a larger buffer size.
            padWidth = (texWidth // 128 + 1) * 128
            blockSize = 8 if texFmt == 0x52 else 16
            wPad = texWidth if not texWidth % 4 else (texWidth // 4 + 1) * 4
            hPad = texHeight if not texHeight % 4 else (texHeight // 4 + 1) * 4
            texData = list()
            for i in range(hPad // 4):
                texData.extend(xpr.readBytes((wPad // 4) * (blockSize)))
                xpr.seek(((padWidth - wPad) // 4) * (blockSize), 1)
            texData = bytes(texData)
            texUntile = False
        else:
            texData = xpr.readBytes(texSize)
            texUntile = True

        if XprDebug:
            print("\nTexture name: {}".format(texName)
                + "\nTexture dimensions: {} x {}".format(texWidth, texHeight)
                + "\nTexture format: 0x{:X}".format(texFmt)
                + "\nTexture size: 0x{:X}".format(texSize)
                + "\nTexture offset: 0x{:X}".format(texOffset + xprOffset + 16)
                + "\nTexture name offset: 0x{:X}".format(nameOfs + xprOffset + 16)
                + "\nTexture info offset: 0x{:X}".format(infoOfs + xprOffset + 16)
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
    return True
