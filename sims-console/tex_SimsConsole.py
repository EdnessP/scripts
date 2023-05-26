# Written by Edness    v0.2
# 2021-07-29  -  2023-05-25

from inc_noesis import *

def registerNoesisTypes():
    #handleArc = noesis.register("The Sims 1, 2, 3 & The Urbz Console", ".arc")
    #noesis.setHandlerExtractArc(handleArc, tscLoadArc)

    handleTxfl = noesis.register("The Sims 1, 2 & The Urbz Console TXFL [PS2]", ".arc")
    noesis.setHandlerTypeCheck(handleTxfl, tscCheckTxfl)
    noesis.setHandlerLoadRGBA(handleTxfl, tscLoadTxfl)
    return True

ID_TXFL = {b"TXFL", b"LFXT"}

def tscGetFilesEndian(noe, dataOffset):
    # Determine endianness based on the file entry count
    noe.seek(dataOffset)  # this one's always LE
    fileCount = noe.readBytes(0x4)
    fileCountLE = int.from_bytes(fileCount, "little")
    fileCountBE = int.from_bytes(fileCount, "big")
    if fileCountBE < fileCountLE:
        noe.setEndian(NOE_BIGENDIAN)
        return fileCountBE, NOE_BIGENDIAN
    return fileCountLE, NOE_LITTLEENDIAN

#def tscCheckArcGeneric(noe):
#    # Generic Sims console ARC checker for future expansions(tm)
#    return True

def tscCheckTxfl(data):
    chk = NoeBitStream(data)
    dataOffset = chk.readUInt()
    if dataOffset not in range(chk.getSize() - 0x20):
        return False
    fileCount = tscGetFilesEndian(chk, dataOffset)[0]
    chk.seek(dataOffset + 0x8)
    fileOffset = chk.readUInt()
    if fileOffset not in range(chk.getSize()):
        return False
    chk.seek(fileOffset)
    # identifier is stored in the first four bytes before The Sims 2
    if chk.readBytes(0x4) in ID_TXFL or chk.readBytes(0x4) in ID_TXFL:
        return True
    return False



def tscReadRGBA32(tex, data, rColors):
    rData = list()
    for x in range(rColors):
        rData.extend(tex.readBytes(0x3))
        rAlpha = tex.readUByte() * 2
        if rAlpha == 0x100:
            rAlpha -= 1
        rData.append(rAlpha)
    return bytes(rData)

def tscLoadTxfl(data, texList):
    rapi.processCommands("-texnorepfn")  # -nofslwr
    tex = NoeBitStream(data)

    dataOffset = tex.readUInt()
    texCount, texEndian = tscGetFilesEndian(tex, dataOffset)
    for i in range(texCount):
        fileNameHash = tex.readUInt()
        fileOffset = tex.readUInt()
        fileSize = tex.readUInt()
        fileName = tex.readString()
        fileTime = tex.readUInt64()
        curDataOffset = tex.getOffset()

        tex.seek(fileOffset)
        if tex.readBytes(0x4) in ID_TXFL:
            texVersion = tex.readUInt()
        else:
            tex.seek(fileOffset)
            texVersion = tex.readUInt()
            if tex.readBytes(0x4) not in ID_TXFL:
                noesis.doException("Unexpected file identifier!")

        if texVersion == 0x7:    # The Sims: Bustin' Out
            tex.seek(0xC, 1)
            texName = tex.readString()
            texFmt = tex.readUByte()  # 0x1 if 32bpp?
            palSize = {4: 16, 8: 256}.get(tex.readUByte(), 0)
            tex.setEndian(texEndian)
            texWidth = tex.readUShort()
            texHeight = tex.readUShort()
            texSize = fileSize - 0x29 - len(texName)
            tex.seek(0xE, 1)

        elif texVersion == 0x8:  # The Urbz: Sims in the City
            texSize = tex.readUInt()
            texName = tex.readString()
            texSize -= len(texName) + 0x21
            tex.seek(0x10, 1)  # texType? @ 0x8
            texWidth = tex.readUShort()
            texHeight = tex.readUShort()
            palSize = tex.readUShort()
            tex.seek(0xA, 1)

        elif texVersion == 0x9:  # The Sims 2, Pets, Castaway
            if tex.readUInt() != 0xFFFFFFFF:
                noesis.doException("Unexpected data after texture identifier!")
            texNameLen = tex.readUInt()
            texName = tex.readString()
            texSize = tex.readUInt() - 0x20
            tex.seek(0x10, 1)  # texType? @ 0x8
            texWidth = tex.readUShort()
            texHeight = tex.readUShort()
            palSize = tex.readUShort()
            tex.seek(0xA, 1)

        else:
            noesis.doException("Unhandled texture version!")

        if texName != fileName:
            print("Info! Texture and file name mismatch: {} -> {}".format(texName, fileName))
            texName = "{} ({})".format(fileName, texName)

        #print(texWidth, texHeight, palSize, hex(texType), hex(tex.getOffset()))
        if palSize == 256:
            texData = tex.readBytes(texWidth * texHeight)
            palData = tscReadRGBA32(tex, data, palSize)
            texData = rapi.imageDecodeRawPal(texData, palData, texWidth, texHeight, 8, "R8G8B8A8")

        elif palSize == 16:
            texData = tex.readBytes(texWidth * texHeight // 2)
            palData = tscReadRGBA32(tex, data, palSize)
            texData = rapi.imageDecodeRawPal(texData, palData, texWidth, texHeight, 4, "R8G8B8A8")

        if palSize == 0:
            if texSize == texWidth * texHeight * 4:
                texData = tscReadRGBA32(tex, data, texWidth * texHeight)
            elif texSize == texWidth * texHeight * 2:
                texData = rapi.imageDecodeRaw(tex.readBytes(texWidth * texHeight * 2), texWidth, texHeight, "R5G5B5A1")
            else:
                noesis.doException("Unhandled texture at {:X}".format(fileOffset))

        texData = rapi.imageFlipRGBA32(texData, texWidth, texHeight, 0, 1)
        texList.append(NoeTexture(texName, texWidth, texHeight, texData, noesis.NOESISTEX_RGBA32))
        tex.seek(curDataOffset)
    return True
