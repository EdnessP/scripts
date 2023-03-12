# Written by Edness    v1.3
# 2021-07-15  -  2023-03-12

from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("Yakuza TXBP", ".txb")
    noesis.setHandlerTypeCheck(handle, txbpCheckType)
    noesis.setHandlerLoadRGBA(handle, txbpLoadTex)
    return True

def txbpCheckType(data):
    bs = NoeBitStream(data)
    if bs.readBytes(4) == b"TXBP":
        return True
    return False

def txbpLoadTex(data, texList):
    rapi.processCommands("-texnorepfn")
    bs = NoeBitStream(data)
    bs.seek(0x4)
    texCount = bs.readUInt()
    dataSize = bs.readUInt()
    bs.seek(0x20)
    for tex in range(texCount):
        texSize = bs.readUInt()
        texWidth = bs.readUInt()
        texHeight = bs.readUInt()
        texFmt = bs.readUInt()
        bs.seek(0x10, 1)

        texName = os.path.splitext(rapi.getInputName())[0] + "_{}".format(tex)
        if texFmt == 0x0B:
            texFmt = noesis.NOESISTEX_DXT5
            texData = bs.readBytes(texSize)

        elif texFmt == 0x14:
            texFmt = noesis.NOESISTEX_RGBA32
            palData = bs.readBytes(0x40)
            texData = bs.readBytes(texWidth * texHeight // 2)
            texData = rapi.imageDecodeRawPal(texData, palData, texWidth, texHeight, 4, "R8G8B8A8")

        elif texFmt == 0x15:
            texFmt = noesis.NOESISTEX_RGBA32
            palData = bs.readBytes(0x400)
            texData = bs.readBytes(texWidth * texHeight)
            texData = rapi.imageDecodeRawPal(texData, palData, texWidth, texHeight, 8, "R8G8B8A8", noesis.DECODEFLAG_PS2SHIFT)

        elif texFmt == 0x1D:
            texFmt = noesis.NOESISTEX_RGBA32
            texData = bs.readBytes(texWidth * texHeight * 4)

        elif texFmt == 0x23:
            # Thanks to aboood40091's GTX-Extractor for letting me know what the Gfx2 header should look like.
            tex = rapi.loadTexByHandler(b"".join((b"Gfx2", noePack(">IIIIIII", 32, 7, 1, 2, 1, 0, 0), bs.readBytes(texSize))), ".gtx")
            tex.name = texName
            texList.append(tex)
            continue

        else:
            noesis.doException("Unhandled texture format 0x{:02X}".format(texFmt))

        texList.append(NoeTexture(texName, texWidth, texWidth, texData, texFmt))
    return True
