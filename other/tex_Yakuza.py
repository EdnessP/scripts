# Written by Edness    v1.5
# 2021-07-15  -  2023-03-16

from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("Yakuza SGT textures", ".sgt")
    noesis.setHandlerTypeCheck(handle, sgtCheckType)
    noesis.setHandlerLoadRGBA(handle, sgtLoadTex)

    handle = noesis.register("Yakuza TXB textures", ".txb")
    noesis.setHandlerTypeCheck(handle, txbCheckType)
    noesis.setHandlerLoadRGBA(handle, txbLoadTex)
    return True

def sgtCheckType(data):
    bs = NoeBitStream(data)
    if bs.readBytes(4) in {b"SG2\x00", b"SGT\x00"}:
        return True
    return False

def txbCheckType(data):
    bs = NoeBitStream(data)
    if bs.readBytes(4) == b"TXBP":
        return True
    return False

def sgtLoadTex(data, texList):
    texData = data[0x20:]
    if txbCheckType(texData):
        txbLoadTex(texData, texList)
    return True

def txbLoadTex(data, texList):
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
        texData = bs.readBytes(texSize)

        if texFmt == 0x0B:
            texFmt = noesis.NOESISTEX_DXT5

        elif texFmt == 0x14:
            texFmt = noesis.NOESISTEX_RGBA32
            texRes = texWidth * texHeight // 2
            palData = texData[:-texRes]
            #palData = bs.readBytes(0x40)  # Had a sample file where the palette was 0x20 bytes long instead
            #texData = bs.readBytes(texWidth * texHeight // 2)
            texData = rapi.imageDecodeRawPal(texData[-texRes:], palData, texWidth, texHeight, 4, "R8G8B8A8")

        elif texFmt == 0x15:
            texFmt = noesis.NOESISTEX_RGBA32
            texRes = texWidth * texHeight
            palData = texData[:-texRes]
            #palData = bs.readBytes(0x400)
            #texData = bs.readBytes(texWidth * texHeight)
            texData = rapi.imageDecodeRawPal(texData[-texRes:], palData, texWidth, texHeight, 8, "R8G8B8A8", noesis.DECODEFLAG_PS2SHIFT)

        elif texFmt == 0x1D:
            texFmt = noesis.NOESISTEX_RGBA32
            #texData = rapi.imageDecodeRaw(texData, texWidth, texHeight, "B8G8R8A8")  # Unsure if needed, only got one 0x1D sample

        elif texFmt == 0x23:
            # Thanks to aboood40091's GTX-Extractor for letting me know what the Gfx2 header should look like.
            tex = rapi.loadTexByHandler(b"Gfx2" + noePack(">7I", 32, 7, 1, 2, 1, 0, 0) + texData, ".gtx")
            tex.name = texName
            texList.append(tex)
            continue

        else:
            noesis.doException("Unhandled texture format 0x{:02X}".format(texFmt))

        texList.append(NoeTexture(texName, texWidth, texWidth, texData, texFmt))
    return True
