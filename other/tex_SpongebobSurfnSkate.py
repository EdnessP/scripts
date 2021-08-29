# Written by Edness
# 2021-08-29   v1.1

from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("Spongebob Surf & Skate Textures [X360]",".xen")
    noesis.setHandlerTypeCheck(handle,checkType)
    noesis.setHandlerLoadRGBA(handle,parseArchive)
    return 1

def checkType(data):
    bs = NoeBitStream(data)
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
    dataOffset = bs.readUInt() * mulSize
    bs.seek(0x28)
    nameOffset = bs.readUInt() * mulSize

    bs.seek(dataOffset)
    for i in range(fileCount):
        dataOffset = bs.readUInt() * mulSize
        bs.seek(8,1)
        #fileSize = bs.readUInt()
        fileName = bs.readUInt() + nameOffset
        curPos = bs.tell() + 4
        bs.seek(fileName)
        fileName = bs.readString()

        if fileName.startswith(("t_","lm_","g_","hvd","framework_v","te")) and not fileName.startswith("t_k"):
            getTexture(bs,data,texList,fileName,dataOffset if fileName.startswith(("t_","lm_","g_")) else dataOffset + 0x1000)

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
    # janky crop, partly taken from fmt_Burnout3LRD.py
    if texWidth % 128 != 0 and texFmt <= 0x16:
        padWidth = (texWidth//128+1)*128
        if texWidth % 4 != 0: wPad = (texWidth//4+1)*4
        else: wPad = texWidth
        if texHeight % 4 != 0: hPad = (texHeight//4+1)*4
        else: hPad = texHeight
        texData = list()
        for i in range(hPad//4):
            texData.extend(bs.readBytes((wPad//4)*(8 if texFmt == 0x12 else 16)))
            bs.seek(((padWidth-wPad)//4)*(8 if texFmt == 0x12 else 16),1)
        texData = bytes(texData)
    else:
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
        texData = rapi.imageDecodeRaw(rapi.imageUntile360Raw(texData,texWidth,texHeight,4),texWidth,texHeight,"A8R8G8B8")
        texFmt = noesis.NOESISTEX_RGBA32
    else:
        # texFmt 0x42 and 0x43 = ??? some 8-bit looking textures
        print("ERROR! Unsupported texture format!",hex(texFmt),texName)
        return

    texList.append(NoeTexture(texName,texWidth,texHeight,texData,texFmt))
