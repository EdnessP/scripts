# Burnout CRASH! PS3, X360, iOS model and texture plugin
# Written by Edness   v1.3   2022-07-09 - 2022-07-12

# NOTE:
#   The Xbox 360 .DDX textures don't store their intended size and had
#   to be manually calculated with what little info there is.
#   If you see something that looks weird or out of place when loading
#   models with Xbox 360 textures, please inform me!

from inc_noesis import *

def registerNoesisTypes():
    handleCxm = noesis.register("Burnout CRASH! - Models [PS3, X360, iOS]", ".cxm")
    noesis.setHandlerTypeCheck(handleCxm, boCheckMdlCxm)
    noesis.setHandlerLoadModel(handleCxm, boParseMdlCxm)

    handleDdx = noesis.register("Burnout CRASH! - Textures [X360]", ".ddx")
    noesis.setHandlerTypeCheck(handleDdx, boCheckTexDdx)
    noesis.setHandlerLoadRGBA(handleDdx, boParseTexDdx)

    handleGtf = noesis.register("Burnout CRASH! - Textures [PS3]", ".gtf")
    noesis.setHandlerTypeCheck(handleGtf, boCheckTexGtf)
    noesis.setHandlerLoadRGBA(handleGtf, boParseTexGtf)

    handlePvr = noesis.register("Burnout CRASH! - Textures [iOS]", ".pvr")
    noesis.setHandlerTypeCheck(handlePvr, boCheckTexPvr)
    noesis.setHandlerLoadRGBA(handlePvr, boParseTexPvr)
    return True

def boCheckMdlCxm(data):
    chk = NoeBitStream(data)
    if chk.readBytes(0x4) == b"CXM-" and chk.readUInt() in {0x4, 0x04000000}:
        return True
    return False

def boCheckTexDdx(data):
    chk = NoeBitStream(data, NOE_BIGENDIAN)
    if chk.readUInt() == 3 and chk.readUInt() == 1:  # and chk.readBytes(0xC) == bytes(0xC)
        return True                                  # This would be True in all cases anyway, but kinda overkill
    return False

def boCheckTexGtf(data):
    chk = NoeBitStream(data, NOE_BIGENDIAN)
    if chk.readBytes(0x4) == b"\x02\x01\x01\xFF":
        chk.seek(0x8)
        if chk.readUInt() == 1:
            return True
    return False

def boCheckTexPvr(data):
    chk = NoeBitStream(data)
    if chk.readUInt() == 0x34:
        chk.seek(0x10)
        # All the existing PVR tools I looked at didn't support these format IDs
        if chk.readUInt() in {0x20D, 0x820D}:
            chk.seek(0x2C)
            if chk.readBytes(0x4) == b"PVR!":
                return True
    return False





def boSplitName(name):
    return os.path.splitext(os.path.split(name)[1])[0]

def boParseMdlCxm(data, mdlList):
    #rapi.setPreviewOption("setAngOfs", "0 -90 180")
    rapi.rpgCreateContext()
    mdl = NoeBitStream(data)
    matList = list()
    texList = list()

    mdl.seek(0x4)
    if mdl.readUInt() != 4:
        mdl.setEndian(NOE_BIGENDIAN)
        rapi.rpgSetOption(noesis.RPGOPT_BIGENDIAN, 1)
    rapi.rpgSetOption(noesis.RPGOPT_TRIWINDBACKWARD, 1)

    subCount = mdl.readUInt()
    vertCount = mdl.readUInt()
    faceCount = mdl.readUInt()
    #subCount = mdl.readUInt()  # again?
    if mdl.readUInt() != subCount:
        noesis.doException("Unhandled data parsing!")

    # a bunch of floats here
    mdl.seek(0x28)
    subType = list()
    subTexture = list()
    for i in range(subCount):
        mdl.seek(0x40, 1)  # a bunch more floats
        #subType.append(noeStrFromBytes(mdl.readBytes(0x20)))
        #subTexture.append(noeStrFromBytes(mdl.readBytes(0x80)))
        mdlPos = mdl.tell()
        subType.append(mdl.readString())
        mdl.seek(mdlPos + 0x20)
        subTexture.append(mdl.readString())
        mdl.seek(mdlPos + 0xA0)

    vertData = mdl.readBytes(vertCount * 32)
    faceData = mdl.readBytes(faceCount * 2)

    rapi.rpgBindPositionBuffer(vertData, noesis.RPGEODATA_FLOAT, 32)
    rapi.rpgBindNormalBuffer(vertData[12:], noesis.RPGEODATA_FLOAT, 32)
    rapi.rpgBindUV1Buffer(vertData[24:], noesis.RPGEODATA_FLOAT, 32)

    callList = {
        "DDX": (boCheckTexDdx, boParseTexDdx),
        "GTF": (boCheckTexGtf, boParseTexGtf),
        "PVR": (boCheckTexPvr, boParseTexPvr),
    }

    for i in range(subCount):
        mdl.seek(0x2, 1)  # 0x0001(?)
        subIdx = mdl.readUShort()  # == i?
        subFaceStart = mdl.readUShort()
        subFaceCount = mdl.readUShort()
        subVertStart = mdl.readUShort()
        subVertCount = mdl.readUShort()

        for texExt in callList:
            # It's a relative path going a to a different folder in the directory above
            texName = r"{}\{}.{}".format(os.path.split(rapi.getInputName())[0], os.path.splitext(subTexture[subIdx])[0], texExt)

            if os.path.exists(texName):
                chkCall, texCall = callList[texExt]
                texData = rapi.loadIntoByteArray(texName)
                if chkCall(texData) and texCall(texData, texList, texName):
                    break

        texName = boSplitName(texName)
        mtlName = "MTL_{}_{}".format(subIdx, texName)
        rapi.rpgSetMaterial(mtlName)
        rapi.rpgSetName("MSH_{}_{}".format(i, texName))

        mat = NoeMaterial(mtlName, texName)
        mat.setFlags(noesis.NMATFLAG_TWOSIDED)
        matList.append(mat)

        rapi.rpgCommitTriangles(faceData[subFaceStart * 2:][:subFaceCount * 2], noesis.RPGEODATA_SHORT, subFaceCount, noesis.RPGEO_TRIANGLE_STRIP)

    mdl = rapi.rpgConstructModel()
    mdl.setModelMaterials(NoeModelMaterials(texList, matList))
    mdlList.append(mdl)
    return True

def boParseTexDdx(data, texList, texName=None):
    rapi.processCommands("-texnorepfn")
    tex = NoeBitStream(data, NOE_BIGENDIAN)

    if texName is None:
        texName = rapi.getInputName()

    tex.seek(0x1C)
    texWidth = tex.readUShort() // 2
    texDiv = tex.readUShort()  # i think???
    texFmt = tex.readUInt()
    if texDiv != 2:
        noesis.doException("Texture division size is not 2 but instead {}".format(texDiv))

    tex.seek(0x34)
    texData = rapi.swapEndianArray(tex.readBytes(tex.getSize() - 0x34), 2)
    texHeight = len(texData) // texWidth

    if texFmt != 0x54:
        noesis.doException("Unhandled texture format 0x{:X}".format(texFmt))

    # jank workaround for textures with a larger buffer
    # i think there's a cleaner way to do this but i cba
    if texWidth == 128:
        texWidthDiv = texWidth
        for i in range(6):
            texWidthDiv //= 2
            if not texData.endswith(bytes((texWidth - texWidthDiv) * 4)):
                texWidth = texWidthDiv * 2
                break
        if texWidth != 128:
            tex = NoeBitStream(texData)
            texData = list()
            texSkip = list()
            for i in range(texHeight // 4):
                texData.extend(tex.readBytes(texWidth * 4))
                texSkip.extend(tex.readBytes((128 - texWidth) * 4))
                #tex.seek((128 - texWidth) * 4, 1)
            texData = bytes(texData)
            texSkip = bytes(texSkip)
            if texSkip != bytes(len(texSkip)):
                noesis.doException("Width adjustment failed!")

    texList.append(NoeTexture(boSplitName(texName), texWidth, texHeight, texData, noesis.NOESISTEX_DXT5))
    return True

def boParseTexGtf(data, texList, texName=None):
    rapi.processCommands("-texnorepfn")
    tex = NoeBitStream(data, NOE_BIGENDIAN)

    if texName is None:
        texName = rapi.getInputName()

    tex.seek(0x4)
    texSize = tex.readUInt()
    tex.seek(0x10)
    texOffset = tex.readUInt()
    tex.seek(0x20)
    texWidth = tex.readUShort()
    texHeight = tex.readUShort()

    tex.seek(texOffset)
    texData = tex.readBytes(texSize)

    texList.append(NoeTexture(boSplitName(texName), texWidth, texHeight, texData, noesis.NOESISTEX_DXT5))
    return True

def boParseTexPvr(data, texList, texName=None):
    rapi.processCommands("-texnorepfn")
    tex = NoeBitStream(data)

    if texName is None:
        texName = rapi.getInputName()

    tex.seek(0x4)
    texWidth = tex.readUInt()
    texHeight = tex.readUInt()
    tex.seek(0x14)
    texSize = tex.readUInt()
    tex.seek(0x34)
    texData = rapi.imageDecodePVRTC(tex.readBytes(texSize), texWidth, texHeight, 4, noesis.PVRTC_DECODE_PVRTC2_ROTATE_BLOCK_PAL)

    texList.append(NoeTexture(boSplitName(texName), texWidth, texHeight, texData))
    return True
