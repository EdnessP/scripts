# Written by Edness    v1.1
# 2021-07-15  -  2022-06-05

from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("Yakuza TXBP", ".txb")
    noesis.setHandlerTypeCheck(handle, txbpCheckType)
    noesis.setHandlerLoadRGBA(handle, txbpLoadTex)
    return 1

def txbpCheckType(data):
    bs = NoeBitStream(data)
    if bs.readBytes(4) == b"TXBP":
        return 1
    return 0

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

        texExport = True
        texWorkaround = 0
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
        elif texFmt == 0x23:
            texExport = False
            texWorkaround += 1
            # Thanks to aboood40091's GTX-Extractor for letting
            # me know what the Gfx2 header should look like.
            with open(texName + ".gtx", "wb") as gtx:
                gtx.write(b"Gfx2"
                        + noePack(">IIIIIII", 32, 7, 1, 2, 1, 0, 0)
                        + data[bs.tell():][:texSize])
        else:
            noesis.doException("Unhandled texture format 0x{:02X}".format(texFmt))

        if texExport:
            texList.append(NoeTexture(texName, texWidth, texWidth, texData, texFmt))

    if texWorkaround:
        noesis.messagePrompt("{} of the textures in this container have been rebuilt with a GTX header and placed in the same directory as this file.\n\nThose files can be natively loaded through Noesis' built-in GTX plugin.".format("All" if texWorkaround == texCount else "Some"))
    return 1
