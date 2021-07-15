# Edness   2021-07-15

from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("Yakuza TXBP",".txb")
    noesis.setHandlerTypeCheck(handle,checkType)
    noesis.setHandlerLoadRGBA(handle,getTex)
    return 1

def checkType(data):
    bs = NoeBitStream(data,NOE_BIGENDIAN)
    if bs.readUInt() == 0x54584250: return 1 # TXBP
    return 0

def getTex(data,texList):
    rapi.processCommands("-nofslwr -texnorepfn")
    bs = NoeBitStream(data)
    bs.seek(4)
    texCount = bs.readUInt()
    dataSize = bs.readUInt()
    bs.seek(0x20)
    texName = 1
    for i in range(texCount):
        texSize = bs.readUInt()
        texWidth = bs.readUInt()
        texHeight = bs.readUInt()
        texFmt = bs.readUInt()
        bs.seek(0x10,1)
        texType(bs,data,texSize,texName,texWidth,texHeight,texFmt,texList)
        texName += 1
    return 1

def texType(bs,data,texSize,texName,texWidth,texHeight,texFmt,texList):
    texName = os.path.splitext(rapi.getInputName())[0]+"_"+str(texName)
    if texFmt == 0x14:
        palData = bs.readBytes(0x40)
        texData = bs.readBytes(texWidth*texHeight//2)
        texData = rapi.imageDecodeRawPal(texData,palData,texWidth,texHeight,4,"R8G8B8A8")
        texList.append(NoeTexture(texName,texWidth,texHeight,texData,noesis.NOESISTEX_RGBA32))
    elif texFmt == 0x15:
        palData = bs.readBytes(0x400)
        texData = bs.readBytes(texWidth*texHeight)
        texData = rapi.imageDecodeRawPal(texData,palData,texWidth,texHeight,8,"R8G8B8A8",noesis.DECODEFLAG_PS2SHIFT)
        texList.append(NoeTexture(texName,texWidth,texHeight,texData,noesis.NOESISTEX_RGBA32))
    elif texFmt == 0x0B:
        texData = bs.readBytes(texSize)
        texList.append(NoeTexture(texName,texWidth,texWidth,texData,noesis.NOESISTEX_DXT5))
