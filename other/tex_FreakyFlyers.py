# Freaky Flyers PS2 and Xbox textures
# Written by Edness   v1.0   2022-07-15

from inc_noesis import *

def registerNoesisTypes():
    handlePtx = noesis.register("Freaky Flyers - Textures [PS2]", ".ptx")
    noesis.setHandlerTypeCheck(handlePtx, ffChkPtx)
    noesis.setHandlerLoadRGBA(handlePtx, ffTexPtx)

    handleXtx = noesis.register("Freaky Flyers - Textures [Xbox]", ".xtx")
    noesis.setHandlerTypeCheck(handleXtx, ffChkXtx)
    noesis.setHandlerLoadRGBA(handleXtx, ffTexXtx)
    return True

def ffChkPtx(data):
    chk = NoeBitStream(data)
    if chk.readUInt() in {3, 4} and chk.readUInt() == 1:
        return True
    return False

def ffChkXtx(data):
    chk = NoeBitStream(data)
    # Terrible validation check, but oh well...
    if os.path.split(rapi.getInputName())[1].startswith(chk.readString()):
        return True
    return False




def ffTexPtx(data, texList):
    tex = NoeBitStream(data)
    texFmt = tex.readUInt()
    tex.seek(0x8)
    texWidth = tex.readUInt()
    texHeight = tex.readUInt()

    def texPS2Read32(col):
        rData = list()
        for i in range(col):
            rData.extend(tex.readBytes(3))
            rAlpha = tex.readUByte() * 2
            if rAlpha == 0x100:
                rAlpha -= 1
            rData.append(rAlpha)
        return bytearray(rData)

    tex.seek(0x14)
    if texFmt == 3:
        bitDepth = 8
        palData = texPS2Read32(256)
        texData = tex.readBytes(texWidth * texHeight)
    elif texFmt == 4:
        bitDepth = 4
        palData = texPS2Read32(16)
        texData = tex.readBytes(texWidth * texHeight // 2)
    texData = rapi.imageDecodeRawPal(texData, palData, texWidth, texHeight, bitDepth, "R8G8B8A8")
    texList.append(NoeTexture(rapi.getInputName(), texWidth, texHeight, texData, noesis.NOESISTEX_RGBA32))
    return True

def ffTexXtx(data, texList):
    tex = NoeBitStream(data)
    tex.seek(0x1C)
    texFmt = tex.readUShort()
    tex.seek(0x20)
    texWidth = tex.readUShort()
    texHeight = tex.readUShort()
    texData = tex.readBytes(tex.getSize() - 0x24)
    if texFmt in {0, 1}:
        texFmt = noesis.NOESISTEX_RGBA32
        texData = rapi.imageDecodeRaw(texData, texWidth, texHeight, "B8G8R8A8")
    elif texFmt == 6:
        texFmt = noesis.NOESISTEX_DXT1
    elif texFmt == 7:
        texFmt = noesis.NOESISTEX_DXT3
    else:
        noesis.doException("Unhandled texture format!")
    texList.append(NoeTexture(rapi.getInputName(), texWidth, texHeight, texData, texFmt))
    return True
