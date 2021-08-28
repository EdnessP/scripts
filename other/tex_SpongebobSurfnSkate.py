# Written by Edness
# 2021-08-28   v1.0

from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("Spongebob Surf & Skate Textures [X360]",".xen")
    noesis.setHandlerTypeCheck(handle,checkType)
    noesis.setHandlerLoadRGBA(handle,parseArchive)
    return 1

def checkType(data):
    bs = NoeBitStream(data,NOE_BIGENDIAN)
    bs.seek(8)
    if bs.readUInt() == 0:
        bs.seek(0x1C) # doublecheck
        if bs.readUInt() == 0:
            return 1
    return 0

def parseArchive(data,texList):
    bs = NoeBitStream(data,NOE_BIGENDIAN)
    rapi.processCommands("-texnorepfn")
    bs.seek(4)
    mulSize = bs.readUInt()
    bs.seek(12)
    fileCount = bs.readUInt()
    fileOffset = bs.readUInt() * mulSize
    bs.seek(0x28)
    nameOffset = bs.readUInt() * mulSize

    bs.seek(fileOffset)
    for i in range(fileCount):
        texOffset = bs.readUInt() * mulSize
        bs.seek(8,1)
        #texSize = bs.readUInt()
        texName = bs.readUInt() + nameOffset
        bs.seek(4,1)
        curPos = bs.tell()
        bs.seek(texName)
        texName = bs.readString()

        if texName.startswith(("t_","lm_","g_","hvd","framework_v","te")) and not texName.startswith(("t_k")):
            getTexture(bs,data,texList,texName,texOffset if texName.startswith(("t_","lm_","g_")) else texOffset + 0x1000)

        bs.seek(curPos)
    return 1

def getTexture(bs,data,texList,texName,texOffset):
    bs.seek(texOffset + 0xC)
    texSize = bs.readUInt() - 0x1000
    bs.seek(texOffset + 0x24)
    texWidth = bs.readUShort()
    texHeight = bs.readUShort()
    texFmt = bs.readUShort()

    bs.seek(texOffset + 0x1000)
    if texWidth % 128 != 0:
        texName += " (Crop to "+str(texWidth)+"px width)"
        texWidth = (texWidth//128+1)*128
    texData = bs.readBytes(texSize)

    if texFmt == 0x12:
        texData = rapi.swapEndianArray(texData,2)
        texFmt = noesis.NOESISTEX_DXT1
    elif texFmt == 0x14:
        texData = rapi.swapEndianArray(texData,2)
        texFmt = noesis.NOESISTEX_DXT3
    elif texFmt == 0x16:
        texData = rapi.swapEndianArray(texData,2)
        texFmt = noesis.NOESISTEX_DXT5
    elif texFmt == 0x3F:
        texData = rapi.imageUntile360Raw(rapi.imageDecodeRaw(texData,texWidth,texHeight,"A8R8G8B8"),texWidth,texHeight,4)
        texFmt = noesis.NOESISTEX_RGBA32
    else:
        # texFmt 0x42 and 0x43 = ??? some 8-bit looking textures
        print("ERROR! Unsupported texture format!",hex(texFmt),texName)

    texList.append(NoeTexture(texName,texWidth,texHeight,texData,texFmt))
