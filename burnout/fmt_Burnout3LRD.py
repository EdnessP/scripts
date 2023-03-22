# This Noesis plugin currently supports:
#
#   Textures:
#       Burnout 3: Takedown     (PS2, Xbox)
#       Burnout Legends         (PSP)
#       Burnout Revenge         (PS2, Xbox, X360)
#       Burnout Dominator       (PS2, PSP)
#       Black                   (PS2, Xbox)
#       Need for Speed: Shift   (PSP)
#
#   Archives:
#       Burnout Dominator DLC   (PSP)
#       Need for Speed: Shift   (PSP)
#
#   Models (Tracks, incomplete):
#       Burnout 3: Takedown     (PS2, Xbox)
#       Burnout Revenge         (Xbox, X360)
#       Burnout Dominator       (PS2)

# This plugin is brought to you by the Burnout Modding community.
#               burnout.wiki  |  discord.gg/8zxbb4x              

# TODO:
#   All streamed track materials
#   All vehicle model support
#   PSP track model support
#   PS2 two-point (Line) "triangles"
#   PS2 models now have several triangles backwards

# Written by Edness   v0.7b   2021-06-23 - 2023-03-22

BoDebug = False
BoModels = False

from inc_noesis import *
import zlib

def registerNoesisTypes():
    handleBxv = noesis.register("Burnout 3Td, Leg, Rev, Dom, NFS Shift - Vehicles", ".bgv;.btv")
    noesis.setHandlerTypeCheck(handleBxv, boChkBxv)
    noesis.setHandlerLoadModel(handleBxv, boArcMdlBxv)

    handleDatStat = noesis.register("Burnout 3Td, Leg, Rev, Dom, NFS Shift - Static", ".dat")
    noesis.setHandlerTypeCheck(handleDatStat, boChkDatStatic)
    noesis.setHandlerLoadModel(handleDatStat, boArcMdlDatStatic)

    if BoModels:
        handleDatSteam = noesis.register("Burnout 3Td, Leg, Rev, Dom, NFS Shift - Streamed", ".dat")
        noesis.setHandlerTypeCheck(handleDatSteam, boChkDatStream)
        noesis.setHandlerLoadModel(handleDatSteam, boArcMdlDatStream)

    handleDatEnv = noesis.register("Burnout 3Td, Leg, Rev, Dom, NFS Shift - Enviro", ".dat")
    noesis.setHandlerTypeCheck(handleDatEnv, boChkDatEnviro)
    noesis.setHandlerLoadRGBA(handleDatEnv, boArcTexDatEnviro)

    handleBinFE = noesis.register("Burnout Rev, Dom, Black - Frontend", ".bin")
    noesis.setHandlerTypeCheck(handleBinFE, boChkBinFE)
    noesis.setHandlerLoadRGBA(handleBinFE, boArcTexBinFE)

    handleBinLoad = noesis.register("Burnout 3Td, Leg - LoadScrn", ".bin")
    noesis.setHandlerTypeCheck(handleBinLoad, boChkBinLoad)
    noesis.setHandlerLoadRGBA(handleBinLoad, boArcTexBinLoad)

    handleBinFont = noesis.register("Burnout Rev, Dom, Black - Font", ".bin")
    noesis.setHandlerTypeCheck(handleBinFont, boChkBinFont)
    noesis.setHandlerLoadRGBA(handleBinFont, boArcTexBinFont)

    handleTxd = noesis.register("Burnout 3Td, Leg, Rev, Dom, NFS Shift - TXD", ".txd")
    noesis.setHandlerTypeCheck(handleTxd, boChkTxd)
    noesis.setHandlerLoadRGBA(handleTxd, boArcTexTxd)

    handleArena = noesis.register("Burnout Dominator, NFS Shift - ARENA [PSP]", ".arena")
    noesis.setHandlerTypeCheck(handleArena, boChkArena)
    noesis.setHandlerLoadRGBA(handleArena, boArcTexArena)

    handleFxp = noesis.register("Burnout Dominator DLC, NFS Shift - FXP [PSP]", ".fxp")
    noesis.setHandlerExtractArc(handleFxp, boArcFxp)

    ### Black - all of these call boArcTxdParse ###

    handleBinDb = noesis.register("Black - DB", ".db")
    noesis.setHandlerTypeCheck(handleBinDb, blkChkDb)
    noesis.setHandlerLoadRGBA(handleBinDb, blkArcTexDb)

    handleBinGlob = noesis.register("Black - GlobData", ".bin")
    noesis.setHandlerTypeCheck(handleBinGlob, blkChkBinGlob)
    noesis.setHandlerLoadRGBA(handleBinGlob, blkArcTexBinGlob)

    handleBinGuns = noesis.register("Black - Guns", ".bin")
    noesis.setHandlerTypeCheck(handleBinGuns, blkChkBinGuns)
    noesis.setHandlerLoadRGBA(handleBinGuns, blkArcTexBinGuns)

    handleBinLvl = noesis.register("Black - LevelDat", ".bin")
    noesis.setHandlerTypeCheck(handleBinLvl, blkChkBinLevel)
    noesis.setHandlerLoadRGBA(handleBinLvl, blkArcTexBinLevel)

    handleBinStLvl = noesis.register("Black - StLevel", ".bin")
    noesis.setHandlerTypeCheck(handleBinStLvl, blkChkBinStLevel)
    noesis.setHandlerLoadRGBA(handleBinStLvl, blkArcTexBinStLevel)

    handleBinStUnit = noesis.register("Black - StUnit", ".bin")
    noesis.setHandlerTypeCheck(handleBinStUnit, blkChkBinStUnit)
    noesis.setHandlerLoadRGBA(handleBinStUnit, blkArcTexBinStUnit)

    handleBinUnit = noesis.register("Black - Unit", ".bin")
    noesis.setHandlerTypeCheck(handleBinUnit, blkChkBinUnit)
    noesis.setHandlerLoadRGBA(handleBinUnit, blkArcTexBinUnit)

    if BoDebug:
        noesis.logPopup()
    return True




#  ##   ##  ##   ######   #####   
#  ### ###  ##  ##       ##   ##  
#  ## # ##  ##   #####   ##       
#  ##   ##  ##       ##  ##   ##  
#  ##   ##  ##  ######    #####   


def boCalcAlign(padFrom, padTo):
    # Calculates alignment to a value
    return (padFrom // padTo + 1) * padTo

def boDecGtID(cGtID: int):
    # Decompresses GtID strings
    char = " -/0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_"
    decStr = ""
    for chr in range(12):
        decStr += char[cGtID % len(char)]
        cGtID //= len(char)
    return decStr[::-1].rstrip()

def boDecZlib(data):
    # Not using Noesis' rapi.decompInflate() because it doesn't support partial decompression
    return zlib.decompressobj().decompress(data)

def boGetVerEndian(noe):
    # Expects to be a byte form int that's < 256 for version checks
    data = noe.readBytes(4)
    if data.endswith(bytes(3)):
        return int.from_bytes(data, "little"), "little"
    if data.startswith(bytes(3)):
        noe.setEndian(NOE_BIGENDIAN)
        return int.from_bytes(data, "big"), "big"
    return (None, None)

def boGetTexAptIndex(arc, aptDataOffset, texIndex):
    # Finds the given texture index in Apt Data
    arc.seek(aptDataOffset)
    while arc.readUInt() != texIndex:
        continue
    else:
        arc.seek(-0x8, 1)

def boPrepExportPath(subDir):
    # Creates the subdirectory path needed for -fulltexpath exports
    if rapi.noesisIsExporting():
        expDir = os.path.split(rapi.getOutputName())[0]
        if subDir and os.path.exists(expDir):
            os.makedirs(os.path.join(expDir, subDir), exist_ok=True)

def boSetDummyMdl(mdlList, texList):
    mdl = NoeModel()
    mdl.setModelMaterials(NoeModelMaterials(texList, list()))
    mdlList.append(mdl)

def boSetPalName(texName, palCount, palNum):
    # Used for PSP, Xbox and Xbox 360  -  PS2 has its own
    return "{} (Palette {})".format(texName, palNum + 1) if palCount > 1 else texName

# Known GtID compressed header values in Little Endian
G_ACTORDICTION = b"\x92\x37\x96\xA8\x73\xC0\xF8\x4D"
G_ANIMDICTIONA = b"\xDD\xAE\x78\x82\x08\x3C\x88\x4F"
G_BNKS         = b"\x00\x00\x00\x57\xE5\x57\x5C\x55"
G_CHARACTERDIC = b"\x57\xC3\x41\x63\x03\x9D\x45\x5A"
G_MODELS       = b"\x00\x00\x5C\x48\xF2\x0A\x82\x95"
G_MOVIEARRAY   = b"\x40\x79\x30\x26\x37\xE5\x92\x95"
G_MYDICTIONARY = b"\x15\xEA\x44\x72\xE2\xA8\xF6\x96"
G_RCBS         = b"\x00\x00\x00\x2F\x94\x09\xDC\xB0"
G_SHAREDBNKS   = b"\xC0\xD7\x61\x81\x3C\x79\x67\xB7"
G_TEXDIC       = b"\x00\x00\x3C\x54\x81\xED\xDE\xBC"
G_TEXTURE      = b"\x00\x80\x9A\xDD\xB7\x4E\xDF\xBC"
G_TEXTUREDICTI = b"\xD5\x64\x20\xE0\xB7\x4E\xDF\xBC"

# Global system variables
BoPS2 = 1
BoPSP = 2
BoXbox = 3
BoXbox360 = 4

# Global exception message
BoExcFmt = "Unsupported format! "

# Generic material name
BoMatName = "material_{:03}"

# Xbox and Xbox 360 mesh format IDs
BoXboxTris = {
    2: noesis.RPGEO_TRIANGLE,  # Line w/ workaround
    6: noesis.RPGEO_TRIANGLE_STRIP
}




#   #####   ##   ##  #######   #####   ##  ##   ######  
#  ##   ##  ##   ##  ##       ##   ##  ## ##   ##       
#  ##       #######  #####    ##       ####     #####   
#  ##   ##  ##   ##  ##       ##   ##  ## ##        ##  
#   #####   ##   ##  #######   #####   ##  ##  ######   


def boChkTxd(data):
    chk = NoeBitStream(data)
    if chk.readBytes(8) in {G_TEXDIC, G_TEXDIC[::-1]}:
        return True
    return False

def boChkBxv(data):
    chk = NoeBitStream(boDecZlib(data[:256]) if data.startswith(b"\x78\xDA") else data)
    chkVer, chkEndian = boGetVerEndian(chk)
    if chkEndian is not None:
        chkSize = chk.readUInt()
        if 0x14 <= chkVer <= 0x25 and chkSize in {0, chk.getSize()}:
            return True
    return False

def boChkDatStatic(data):
    chk = NoeBitStream(boDecZlib(data[:256]) if data.startswith(b"\x78\xDA") else data)
    chkVer, chkEndian = boGetVerEndian(chk)
    if chkEndian is not None:
        chkSize = chk.readUInt()
        if 0x21 <= chkVer <= 0x3E and chkSize in {0, chk.getSize()}:
            return True
    return False

def boChkDatStream(data):
    chk = NoeBitStream(data)
    chkValue, chkEndian = boGetVerEndian(chk)
    if chkEndian is not None:
        if chkValue == 1 and chk.readUInt() == 0:
            return True
    return False

def boChkDatEnviro(data):
    chk = NoeBitStream(data)
    chkSize = chk.getSize()

    # Minimum size check to not break Burnout Paradise .dats by seeking out of bounds
    if chkSize > 0x300:
        # Header values to check in Little Endian
        chkED02 = b"\x02\x00\x44\x45"
        chkED03 = b"\x03\x00\x44\x45"
        chkED04 = b"\x04\x00\x44\x45"

        chk.seek(0xA8)
        if chk.readBytes(4) == chkED02 and chk.readUInt() in {0, chkSize}:  # PS2 & Xbox
            return True
        chk.seek(0xB8)
        if chk.readBytes(4) == chkED03[::-1] and chk.readUInt() == 0:  # Xbox 360
            return True
        chk.seek(0x1C8)
        if chk.readBytes(4) == chkED03 and chk.readUInt() == chkSize:  # PSP (Legends)
            return True
        chk.seek(0x1D8)
        if chk.readBytes(4) == chkED04 and chk.readUInt() == chkSize:  # PSP (Dominator)
            return True
        chk.seek(0x2D4)
        if chk.readBytes(4) == chkED04 and chk.readUInt() == chkSize:  # PSP (NFS: Shift)
            return True
    return False

def boChkBinFE(data):
    chk = NoeBitStream(data)
    if chk.readBytes(8) in {G_MOVIEARRAY, G_MOVIEARRAY[::-1]}:
        return True
    return False

def boChkBinFont(data):
    chk = NoeBitStream(data)
    chkSize = chk.getSize()

    fontMagic = chk.readBytes(4)
    if fontMagic in {b"v1.4", b"4.1v"}:
        return True  # Revenge, Black
    elif chkSize > 0x2000:
        chk.seek(0x70)
        texOffset = chk.readUInt()
        if texOffset < (chkSize // 2):
            chk.seek(texOffset)
            if chk.readBytes(8) == bytes(4) + b"\x50\x02\x00\x00":
                return True  # Dominator (PS2)
    return False

def boChkBinLoad(data):
    chk = NoeBitStream(data)
    txdCount = chk.readUInt64()
    chkAlign = boCalcAlign(txdCount * 0x10 + 8, 0x800)
    if chkAlign < chk.getSize():
        chk.seek(chkAlign)
        if chk.readBytes(8) == G_TEXDIC:
            return True
    return False

def boChkArena(data):
    chk = NoeBitStream(data)
    if chk.readBytes(16) == b"Neko\x01" + bytes(11):
        return True
    return False

def blkChkDb(data):
    chk = NoeBitStream(data)

    chkSize = chk.getSize()
    chkVer = chk.readUInt()
    if chkVer != 0x04:
        chk.seek(0x18)
        chkVer = chk.readUInt()
    if chkVer in {0x04, 0x09}:
        dctOrder = (G_MODELS,
                    G_CHARACTERDIC,
                    G_ACTORDICTION,
                    G_BNKS,
                    G_SHAREDBNKS,
                    G_RCBS)
        txdOffset = chk.readUInt()
        curChkOffset = chk.getOffset()
        if txdOffset < chkSize:
            chk.seek(txdOffset)
            if chk.readBytes(8) not in {G_TEXDIC, G_TEXTURE}:
                return False
        for gtid in dctOrder:
            chk.seek(curChkOffset)
            dctOffset = chk.readUInt()
            curChkOffset = chk.getOffset()
            if dctOffset > chkSize:
                return False
            chk.seek(dctOffset)
            if chk.readBytes(8) != gtid:
                return False
        return True
    return False

def blkChkBinGlob(data):
    chk = NoeBitStream(data)

    chkSize = chk.getSize()
    if chk.readUInt() in {8, 9}:
        txdOffset = chk.readUInt()
        dctOffset = chk.readUInt()
        if txdOffset > chkSize or dctOffset > chkSize:
            return False
        chk.seek(txdOffset)
        if chk.readBytes(8) != G_TEXDIC:
            return False
        chk.seek(dctOffset)
        if chk.readBytes(8) != G_MYDICTIONARY:
            return False
        return True
    return False

def blkChkBinGuns(data):
    chk = NoeBitStream(data)

    chkSize = chk.getSize()
    txdOffset = chk.readUInt()
    mdlOffset = chk.readUInt()
    if txdOffset > chkSize or mdlOffset > chkSize:
        return False
    chk.seek(txdOffset)
    if chk.readBytes(8) == G_TEXTURE:
        chk.seek(mdlOffset)
        if chk.readBytes(8) == G_MODELS:
            return True
    return False

def blkChkBinLevel(data):
    chk = NoeBitStream(data)

    if chk.getSize() > 0x500:
        chkVer = chk.readUInt()
        if chkVer == 0x0A:
            chk.seek(0x2BC)  # -> 0x300
        elif chkVer == 0x11:
            chk.seek(0x390) # -> 0x400
        else:  # chkVer 0x01 has no textures
            return False
        txdOffset = chk.readUInt()
        chk.seek(txdOffset)
        if chk.readBytes(8) == G_TEXDIC:
            return True
    return False

def blkChkBinStLevel(data):
    chk = NoeBitStream(data)

    chkVer = chk.readUInt()
    txdOffset = chk.readUInt()
    if chkVer in {0x09, 0x0A}:
        chk.seek(0xC)
        hdrOffset = chk.readUInt()
        if hdrOffset < chk.getSize() - 8:
            chk.seek(hdrOffset + txdOffset)
            if chk.readBytes(8) == G_TEXTURE:
                return True
    return False

def blkChkBinStUnit(data):
    chk = NoeBitStream(data)

    chkSize = chk.getSize()
    if chk.readUInt() == 0x03:
        chk.seek(0x8)
        hdrOffset = chk.readUInt()
        chk.seek(hdrOffset + 0x18)
        if chk.readUInt() == 0x09:
            dctOrder = (G_TEXTURE,
                        G_MODELS,
                        G_CHARACTERDIC,
                        G_ACTORDICTION,
                        G_BNKS,
                        G_SHAREDBNKS,
                        G_RCBS)
            for gtid in dctOrder:
                dctOffset = chk.readUInt() + hdrOffset
                curChkOffset = chk.getOffset()
                if dctOffset > chkSize:
                    return False
                chk.seek(dctOffset)
                if chk.readBytes(8) != gtid:
                    return False
                chk.seek(curChkOffset)
            return True
    return False

def blkChkBinUnit(data):
    chk = NoeBitStream(data)

    chkVer = chk.readUInt()
    if chkVer == 0x0C:
        chk.seek(0x18)
    elif 0x16 <= chkVer <= 0x18:
        chk.seek(0x24)
    else:
        return False
    txdOffset = chk.readUInt()
    chk.seek(txdOffset)
    if chk.readBytes(8) == G_TEXTUREDICTI:
    # surrounded by G_MYDICTIONARY and G_ANIMDICTIONA 
        return True
    return False




#  ##   ##   #####   ######   #######  ##        ######  
#  ### ###  ##   ##  ##   ##  ##       ##       ##       
#  ## # ##  ##   ##  ##   ##  #####    ##        #####   
#  ##   ##  ##   ##  ##   ##  ##       ##            ##  
#  ##   ##   #####   ######   #######  #######  ######   


def boMdlGetTrackSystem(mdl, mdlEndian, mdlOffset):
    mdl.seek(mdlOffset + 0xC)
    #subOffset = mdl.readUInt()
    if mdlEndian == "big":
        return BoXbox360
    return BoPS2 if mdl.readUInt() == 0x0 else BoXbox
    #noesis.doException("Couldn't determine system!")

def boMdlGetMatIdx(mdl, mdlVer, mdlOffset, grpOffset, matOffset):
    # Last known version to calculate the static pointer from the group offset is 0x30
    # Earliest known version to calculate it from the model offset is 0x32
    matIdxOffset = mdl.readUInt()
    if mdlVer is not None:   # Static
        matIdxOffset += grpOffset if mdlVer <= 0x30 else mdlOffset - 0x40
    elif matIdxOffset == 0:  # Streamed
        matIdxOffset = mdlOffset + matOffset
    else:
        noesis.doException("Unhandled material index pointer")
    return matIdxOffset

def boMdlSkipVertexAlpha(clrData, clrOffset, clrStride):
    # Force 100% vertex color opacity while previewing
    # If the vertex color data type is set to RGB, it doesn't default the alpha to FF
    # but instead to 00, which means the whole model would become invisible in Noesis
    if not rapi.noesisIsExporting():
        clrData[clrOffset + 3::clrStride] = b"\xFF" * (len(clrData) // clrStride)

def boMdlXboxReadLine(mdl, faceCount):
    # Converts Xbox/Xbox 360 line meshtype to fake triangles
    faceData = list()
    for idx in range(faceCount):
        faceData.extend(mdl.readBytes(0x2) + mdl.readBytes(0x2) * 2)
    return bytearray(faceData)

def boMdlPS2(mdl, matList, matIdx, mdlOffset, mdlBaseName, subIdx, vertIdx):
    def boPS2Read12(vif, rData):  # Would be // vif.numElems if it weren't for car UVs
        for int in noeUnpack("<{}h".format(len(vif.data) // 2), vif.data):
            rData.extend(noePack("f", int / 4096))

    mdl.seek(mdlOffset)
    subSize = mdl.readUShort()
    mdl.seek(mdlOffset + 0x4)
    #print("SubHdr:", " ".join(["{:02X}".format(i) for i in mdl.read(0x2)]))

    mdlName = mdlBaseName + "{:03}_{}".format(subIdx, vertIdx)
    rapi.rpgSetName(mdlName)
    rapi.rpgSetMaterial(BoMatName.format(matIdx[subIdx]))

    vifData = rapi.unpackPS2VIF(mdl.read(subSize * 0x10 + 0xC))
    #print("MdlOffs", hex(mdlOffset), mdlName)  # NoePS2VIFUnpack
    vertData = list()
    faceData = list()
    clrData = list()
    uvData = list()
    # many submeshes have both RGB24 and RGBA32 vtxclrs, RGB24 seems to take precedence
    clr32 = True
    for vif in vifData:
        #print(vif, vif.data)
        if vif.elemBits == 32 and vif.numElems == 4:    # Vertices
            vertData.extend(vif.data)
        elif vif.elemBits == 16 and vif.numElems == 2:  # UVs (Tracks)
            boPS2Read12(vif, uvData)
        elif vif.elemBits == 16 and vif.numElems == 4:  # UVs (Vehicles)
            boPS2Read12(vif, uvData)
        elif vif.elemBits == 8 and vif.numElems == 3:   # Colors RGB24
            clr32 = False
            # Vertex colors need to be changed from RGB to RGBA
            for clr in range(len(vif.data) // 3):
                clrData.extend(vif.data[clr * 3:][:3] + b"\xFF")
        elif vif.elemBits == 8 and vif.numElems == 4:   # Colors RGBA32
            if clr32:
                clrData.extend(vif.data)
        else:
            noesis.doException("Unhandled VIF data: {}".format(vif))

    vertData = bytes(vertData)
    for vtx in range(len(vertData) // 0x10 - 2):
        if vertData[vtx * 0x10:][:0x30].endswith(bytes(4)):
            faceData.extend((vtx, vtx + 1, vtx + 2) if vtx % 2 == 0 else (vtx, vtx + 2, vtx + 1))

    if not uvData:
        uvData = bytes(len(vertData) // 0x10 * 8)

    clrData = bytearray(clrData)
    boMdlSkipVertexAlpha(clrData, 0x0, 0x4)

    faceData = b"".join([int.to_bytes(2, "little") for int in faceData])
    rapi.rpgBindPositionBuffer(vertData, noesis.RPGEODATA_FLOAT, 0x10)
    rapi.rpgBindUV1Buffer(bytes(uvData), noesis.RPGEODATA_FLOAT, 0x8)
    rapi.rpgBindColorBuffer(clrData, noesis.RPGEODATA_UBYTE, 0x4, 4)
    rapi.rpgCommitTriangles(bytes(faceData), noesis.RPGEODATA_USHORT, len(faceData) // 2, noesis.RPGEO_TRIANGLE)

def boMdlPS2Track(mdl, matList, mdlOffset, mdlBaseName, grpOffset, mdlVer):
    mdl.seek(mdlOffset)
    subCount = mdl.readUInt()
    subOffset = mdl.readUInt() + mdlOffset
    matIdxOffset = boMdlGetMatIdx(mdl, mdlVer, mdlOffset, grpOffset, 0x24)

    mdl.seek(matIdxOffset)
    matIdx = [mdl.readUShort() for mat in range(subCount)]

    for blk in range(subCount):
        mdl.seek(subOffset)
        vertOffsetList = list()
        for sub in range(2):
            mdl.seek(0xC, 1)
            vertOffset = mdl.readUInt()
            if vertOffset != 0:
                vertOffsetList.append(vertOffset + subOffset)
        subOffset += 0x40

        for vertIdx, vertOffset in enumerate(vertOffsetList):
            boMdlPS2(mdl, matList, matIdx, vertOffset, mdlBaseName, blk, vertIdx)

def boMdlPSPTrack():
    # The streamed format is entirely different in Legends
    # but in Dominator and NFS:Shift matIdxOffset == 0x104
    # UPD:Legends LOD order is inverted, matIdxOfs == 0x74
    matIdxOffset = boMdlGetMatIdx(mdl, mdlVer, mdlOffset, grpOffset, 0x104)

def boMdlXboxTrack(mdl, matList, mdlOffset, mdlBaseName, grpOffset, mdlVer):
    mdl.seek(mdlOffset)
    if mdl.readUInt() != 0x1:
        noesis.doException("Invalid block header!")
    vertOffset = mdl.readUInt() + mdlOffset
    mdl.seek(mdlOffset + 0xC)
    subOffset = mdl.readUInt() + mdlOffset
    subCount = mdl.readUInt()
    matIdxOffset = boMdlGetMatIdx(mdl, mdlVer, mdlOffset, grpOffset, 0x34)

    subData = list()
    mdl.seek(subOffset)
    for blk in range(subCount):
        subOffset = mdl.getOffset()
        mdl.seek(0x80, 1)
        # triFmt, faceCount, faceOffset
        subData.append([mdl.readUInt(), mdl.readUInt(), mdl.readUInt() + subOffset])
        mdl.seek(0x4, 1)

    mdl.seek(matIdxOffset)
    matIdx = [mdl.readUShort() for mat in range(subCount)]

    mdl.seek(vertOffset)
    vertData = bytearray(mdl.readBytes(subData[0][2] - vertOffset))  # I swear it was bytearray by default before...
    for clr in range(len(vertData) // 0x1C):
        # Vertex colors need to be flipped from BGRA to RGBA
        clrOffset = 0x10 + clr * 0x1C
        vertData[clrOffset:clrOffset + 3] = vertData[clrOffset:][:3][::-1]
    boMdlSkipVertexAlpha(vertData, 0x10, 0x1C)

    rapi.rpgBindPositionBuffer(vertData, noesis.RPGEODATA_FLOAT, 0x1C)
    rapi.rpgBindUV1BufferOfs(vertData, noesis.RPGEODATA_FLOAT, 0x1C, 0x14)
    rapi.rpgBindColorBufferOfs(vertData, noesis.RPGEODATA_UBYTE, 0x1C, 0x10, 4)

    for subIdx, (triFmt, faceCount, faceOffset) in enumerate(subData):
        mdlName = mdlBaseName + "{:03}".format(subIdx)
        rapi.rpgSetName(mdlName)
        rapi.rpgSetMaterial(BoMatName.format(matIdx[subIdx]))

        mdl.seek(faceOffset)
        if triFmt == 0x2:
            faceData = boMdlXboxReadLine(mdl, faceCount)
            faceCount = len(faceData) // 4
        elif triFmt == 0x6:
            faceData = mdl.readBytes(faceCount * 2)

        rapi.rpgCommitTriangles(faceData, noesis.RPGEODATA_USHORT, faceCount, BoXboxTris.get(triFmt))

def boMdlXbox360Track(mdl, matList, mdlOffset, mdlBaseName, grpOffset, mdlVer):
    mdl.seek(mdlOffset + 0x10)
    vertSize = mdl.readUInt() - 0x2  # For some reason it's always off by 2?
    vertOffset = mdl.readUInt() + mdlOffset
    vertCount = mdl.readUShort()
    mdl.seek(mdlOffset + 0x1C)
    subOffset = mdl.readUInt() + mdlOffset
    subCount = mdl.readUShort()
    mdl.seek(mdlOffset + 0x24)
    matIdxOffset = boMdlGetMatIdx(mdl, mdlVer, mdlOffset, grpOffset, 0x44)  # mdlVer = 0x3C, grpOffset = 0x0 (dummy)

    subData = list()
    mdl.seek(subOffset)
    for blk in range(subCount):
        subOffset = mdl.getOffset()
        mdl.seek(0x90, 1)
        # faceSize, faceOffset, faceCount (broken?), triFmt
        subData.append([mdl.readUInt(), mdl.readUInt() + subOffset, mdl.readUInt() >> 16, mdl.readUInt()])
        mdl.seek(0x10, 1)
    #faceOffset = vertOffset + vertSize

    mdl.seek(matIdxOffset)
    matIdx = [mdl.readUShort() for mat in range(subCount)]

    mdl.seek(vertOffset)
    vertData = bytearray(mdl.readBytes(vertSize))
    for clr in range(len(vertData) // 0x1C):
        # Vertex colors need to be changed from ARGB to RGBA
        clrOffset = 0x18 + clr * 0x1C
        clrData = list(vertData[clrOffset:][:4])
        clrData.append(clrData.pop(0))
        vertData[clrOffset:clrOffset + 4] = clrData
    boMdlSkipVertexAlpha(vertData, 0x18, 0x1C)

    rapi.rpgBindPositionBuffer(vertData, noesis.RPGEODATA_FLOAT, 0x1C)
    rapi.rpgBindUV1BufferOfs(vertData, noesis.RPGEODATA_FLOAT, 0x1C, 0x10)
    rapi.rpgBindColorBufferOfs(vertData, noesis.RPGEODATA_UBYTE, 0x1C, 0x18, 4)

    for subIdx, (faceSize, faceOffset, _faceCount, triFmt) in enumerate(subData):
        mdlName = mdlBaseName + "{:03}".format(subIdx)
        rapi.rpgSetName(mdlName)
        rapi.rpgSetMaterial(BoMatName.format(matIdx[subIdx]))

        mdl.seek(faceOffset)
        if triFmt == 0x2:
            faceData = boMdlXboxReadLine(mdl, faceSize // 2)
            faceCount = len(faceData) // 4
        elif triFmt == 0x6:
            faceData = mdl.readBytes(faceSize)
            faceCount = faceSize // 2

        rapi.rpgCommitTriangles(faceData, noesis.RPGEODATA_USHORT, faceCount, BoXboxTris.get(triFmt))

def boMdlParseTrack(mdl, mdlEndian, matList, mdlOffset, subCount, unitIdx, mdlType=None, grpOffset=None, mdlVer=None):
    mdlSystem = boMdlGetTrackSystem(mdl, mdlEndian, mdlOffset)

    # mdlType for streamed is reserved for LOD
    for sub in range(subCount):
        mdlName = "unit_{:03}_sub_".format(unitIdx) if mdlType is None else "{}_grp_{:03}_mdl_{:03}_sub_".format(mdlType, unitIdx, sub)
        if mdlSystem == BoPS2:
            boMdlPS2Track(mdl, matList, mdlOffset, mdlName, grpOffset, mdlVer)
            mdlOffset += 0x50
        elif mdlSystem == BoXbox:
            boMdlXboxTrack(mdl, matList, mdlOffset, mdlName, grpOffset, mdlVer)
            mdlOffset += 0x60
        elif mdlSystem == BoXbox360:
            boMdlXbox360Track(mdl, matList, mdlOffset, mdlName, grpOffset, mdlVer)
            mdlOffset += 0x70




#  ######  #######  ##   ##  ######  ##   ##  ######   #######   ######  
#    ##    ##        ## ##     ##    ##   ##  ##   ##  ##       ##       
#    ##    #####      ###      ##    ##   ##  ######   #####     #####   
#    ##    ##        ## ##     ##    ##   ##  ##   ##  ##            ##  
#    ##    #######  ##   ##    ##     #####   ##   ##  #######  ######   


def boTexGetSystem(tex, texEndian, texOffset):
    tex.seek(texOffset)
    texHeader = tex.readBytes(8)
    if texEndian == "big":
        return BoXbox360
    if texHeader.startswith(b"\x01\x00\x04\x00"):
        return BoXbox
    if texHeader == bytes(8):
        return BoPSP
    if texHeader.startswith(bytes(4)):
        return BoPS2
    noesis.doException("Couldn't determine system!")

def boTexGetName(tex, texEndian, texOffset):
    texSystem = boTexGetSystem(tex, texEndian, texOffset)

    #texSeek = {
    #    BoPS2: 0xA8,
    #    BoXbox: 0x44
    #}.get(texSystem, 0x0)
    #tex.seek(texOffset + texSeek)
    if texSystem == BoPS2:
        tex.seek(texOffset + 0xA8)
    elif texSystem == BoPSP:
        tex.seek(texOffset + 0xB0)
        tex.seek(texOffset + (0x8C if 1 <= tex.readUShort() <= 8 else 0x90))
    elif texSystem == BoXbox:
        tex.seek(texOffset + 0x40)
        tex.seek(texOffset + (0x48 if tex.readUInt() in {4, 8, 32} else 0x44))
    elif texSystem == BoXbox360:
        tex.seek(texOffset)
    return tex.readString()

def boTexPalRead(tex, bitDepth):
    return tex.readBytes({
        4: 0x40,
        8: 0x400
    }.get(bitDepth))

def boTexFixWidth(tex, texWidth, padWidth, texHeight):
    # Can fix by reading from a bit stream or from an existing bytearray
    if type(tex) is bytearray:
        tex = NoeBitStream(tex)
    texData = list()
    for byte in range(texHeight):
        texData.extend(tex.readBytes(texWidth))
        tex.seek(padWidth - texWidth, 1)
    return bytearray(texData)

def boTexPS2(tex, texList, texOffset, texName, fontName):
    def boPS2Read4(rSize):
        # Converts 4-bit data to 8-bit
        rData = list()
        for byte in tex.readBytes(rSize):
            # Not using Noesis' readBits() because it is very slow
            rData.extend((byte & 0xF, byte >> 4))
        return bytearray(rData)

    def boPS2Read32(rColors, rData=None):
        # Fixes alpha channel for 32-bit data
        # Can be used for both existing data lists and returning new bytearrays
        ret = False
        if rData is None:
            rData = list()
            ret = True
        for col in range(rColors):
            rData.extend(tex.readBytes(3))
            rAlpha = tex.readUByte() * 2
            if rAlpha == 0x100:
                rAlpha -= 1
            rData.append(rAlpha)
        if ret:
            return bytearray(rData)

    def boPS2TexPal(palData):
        texPalData = rapi.imageDecodeRawPal(texData, palData, texWidth, texHeight, 8, "R8G8B8A8", noesis.DECODEFLAG_PS2SHIFT)
        texList.append(NoeTexture("{} (Palette {})".format(texName, palNum), texWidth, texHeight, texPalData, texFmt))

    tex.seek(texOffset + 0x4)
    bmpOffset = tex.readUInt() + texOffset
    palOffset = tex.readUInt() + texOffset
    texWidth = tex.readUInt()
    texHeight = tex.readUInt()
    bitDepth = tex.readUInt()
    tex.seek(texOffset + 0xA0)
    palCount = tex.readUByte()
    if not texName:
        tex.seek(texOffset + 0xA8)
        texName = tex.readString()
    if fontName:
        texName += " ({})".format(fontName)

    if BoDebug:
        print("\nPlayStation 2 texture detected!"
            + "\nTexture name: {}".format(os.path.split(texName)[1])
            + "\nTexture offset: 0x{:X}".format(texOffset)
            + "\nTexture data offset: 0x{:X}".format(bmpOffset)
            + "\nTexture dimensions: {} x {}".format(texWidth, texHeight)
            + "\nTexture bit depth: {}".format(bitDepth)
            + "\nPalette amount: {}".format(palCount)
            + "\nPalette data offset: 0x{:X}".format(palOffset))

    tex.seek(bmpOffset)

    wPad = 16 if texWidth < 16 else texWidth
    hPad = 4 if texHeight < 4 else texHeight

    texFmt = noesis.NOESISTEX_RGBA32
    if bitDepth == 4:
        # Fix-up small textures with weird buffer sizes, pre-unswizzle
        if wPad == 16:
            texData = boPS2Read4(64 * hPad // 2)
            texData = boTexFixWidth(texData, 32, 64, hPad)
        else:
            texData = boPS2Read4(wPad * hPad // 2)
    elif bitDepth == 8:
        texData = tex.readBytes(wPad * texHeight)
    elif bitDepth == 24:
        texData = boTexFixWidth(tex, 3, 24, texHeight) if texWidth == 1 else tex.readBytes(texWidth * texHeight * 3)
        texFmt = noesis.NOESISTEX_RGB24
    elif bitDepth == 32:
        texData = boPS2Read32(texWidth * texHeight)
    else:
        noesis.doException(BoExcFmt + "{} bpp".format(bitDepth))

    if bitDepth in {4, 8}:
        texData = rapi.imageUntwiddlePS2(texData, wPad, texHeight, 8)
        # Fix-up small textures with weird buffer sizes, post-unswizzle
        if texWidth < 16:
            texData = boTexFixWidth(texData, texWidth, 16, hPad)

        tex.seek(palOffset)
        if palCount == 1:
            palData = boPS2Read32({4: 16, 8: 256}.get(bitDepth))
        elif bitDepth == 8 and palCount <= 8:
            # Interleaved-grouped palette splitter
            palData = [list() for pal in range(8)]
            for pal in range(16):
                boPS2Read32(16, palData[0])
                boPS2Read32(16, palData[1])
                if palCount == 3 or palCount >= 5:
                    boPS2Read32(16, palData[2])
                    if palCount >= 7:
                        boPS2Read32(16, palData[3])
            if palCount >= 4:
                for pal in range(16):
                    boPS2Read32(16, palData[4])
                    boPS2Read32(16, palData[5])
                    if palCount >= 5:
                        boPS2Read32(16, palData[6])
                        if palCount >= 7:
                            boPS2Read32(16, palData[7])
            palData = [bytearray(palData[pal]) for pal in range(8)]

            palNum = 1
            boPS2TexPal(palData[0])
            palNum = 2
            boPS2TexPal(palData[1])
            if palCount == 3 or palCount >= 5:
                palNum += 1
                boPS2TexPal(palData[2])
                if palCount >= 7:
                    palNum += 1
                    boPS2TexPal(palData[3])
            if palCount >= 4:
                palNum += 1
                boPS2TexPal(palData[4])
                palNum += 1
                boPS2TexPal(palData[5])
                if palCount >= 6:
                    palNum += 1
                    boPS2TexPal(palData[6])
                    if palCount == 8:
                        palNum += 1
                        boPS2TexPal(palData[7])
            return
        else:
            noesis.doException(BoExcFmt + "{} {}".format(bitDepth, palCount))
        texData = rapi.imageDecodeRawPal(texData, palData, texWidth, texHeight, 8, "R8G8B8A8", noesis.DECODEFLAG_PS2SHIFT if bitDepth == 8 else 0)
    texList.append(NoeTexture(texName, texWidth, texHeight, texData, texFmt))

def boTexPSP(tex, texList, texOffset):
    tex.seek(texOffset + 0x8)
    palOffset = tex.readUInt() + texOffset
    texWidth = tex.readUInt()
    texHeight = tex.readUInt()
    bitDepth = tex.readUInt()
    tex.seek(texOffset + 0x38)
    bmpOffset = tex.readUInt() + texOffset
    tex.seek(texOffset + 0xB0)
    palCount = tex.readUShort()
    if 1 <= palCount <= 8:
        newFmtNfs = False
    else:
        newFmtNfs = True
        tex.seek(texOffset + 0xB4)
        palCount = tex.readUShort()
    tex.seek(texOffset + 0x8C)
    if newFmtNfs:
        texSize = tex.readUInt()
    texName = tex.readString()

    if BoDebug:
        print("\nPlayStation Portable texture detected! ({}er revision)".format("New" if newFmtNfs else "Old")
            + "\nTexture name: {}".format(texName)
            +("\nTexture size: 0x{:X}".format(texSize) if newFmtNfs else "")
            + "\nTexture offset: 0x{:X}".format(texOffset)
            + "\nTexture data offset: 0x{:X}".format(bmpOffset)
            + "\nTexture dimensions: {} x {}".format(texWidth, texHeight)
            + "\nTexture bit depth: {}".format(bitDepth)
            + "\nPalette amount: {}".format(palCount)
            + "\nPalette data offset: 0x{:X}".format(palOffset))

    tex.seek(bmpOffset)
    if bitDepth == 4:
        wPad = texWidth * 2 if texWidth <= 16 else texWidth
        texData = tex.readBytes(wPad * texHeight // 2)
    elif bitDepth == 8:
        wPad = texWidth * 2 if texWidth <= 8 else texWidth
        texData = tex.readBytes(wPad * texHeight)
    elif bitDepth == 32:
        texData = tex.readBytes(texWidth * texHeight * 4)
    else:
        noesis.doException(BoExcFmt + "{} bpp".format(bitDepth))
    texData = rapi.imageUntwiddlePSP(texData, texWidth, texHeight, bitDepth)

    if bitDepth in {4, 8}:
        tex.seek(palOffset)
        for pal in range(palCount):
            palData = boTexPalRead(tex, bitDepth)
            texPalData = rapi.imageDecodeRawPal(texData, palData, texWidth, texHeight, bitDepth, "R8G8B8A8")
            texList.append(NoeTexture(boSetPalName(texName, palCount, pal), texWidth, texHeight, texPalData, noesis.NOESISTEX_RGBA32))
        return
    texList.append(NoeTexture(texName, texWidth, texHeight, texData, noesis.NOESISTEX_RGBA32))

def boTexPSPArena(tex, texList, texOffset, texName=None, fontName=None):
    # This isn't called through boTexParse, it's exclusively used by boArcTexArena
    tex.seek(texOffset)
    if not texName:
        texName = tex.readString()
    if fontName:
        texName += " ({})".format(fontName)
    tex.seek(texOffset + 0x44)
    texWidth = tex.readUShort()
    texHeight = tex.readUShort()
    texFmt = tex.readUInt()

    bitDepth = {
        2: 4,
        3: 8
    }.get(texFmt)
    if not bitDepth:
        noesis.doException(BoExcFmt + hex(texFmt))

    tex.seek(texOffset + 0x80)
    bmpOffset = tex.readUInt() + texOffset
    tex.seek(texOffset + 0xA0)
    palOffset = tex.readUInt() + texOffset

    if BoDebug:
        print("\nPlayStation Portable arena texture detected!"
            + "\nTexture name: {}".format(texName)
            + "\nTexture offset: 0x{:X}".format(texOffset + 16)
            + "\nTexture data offset: 0x{:X}".format(bmpOffset + 16)
            + "\nTexture dimensions: {} x {}".format(texWidth, texHeight)
            + "\nTexture bit depth: {}".format(bitDepth)
            + "\nPalette data offset: 0x{:X}".format(palOffset + 16))

    tex.seek(bmpOffset)
    if texFmt == 0x02:
        texData = tex.readBytes(texWidth * texHeight // 2)
    elif texFmt == 0x03:
        texData = tex.readBytes(texWidth * texHeight)

    tex.seek(palOffset)
    palData = boTexPalRead(tex, bitDepth)

    texData = rapi.imageUntwiddlePSP(texData, texWidth, texHeight, bitDepth)
    texData = rapi.imageDecodeRawPal(texData, palData, texWidth, texHeight, bitDepth, "R8G8B8A8")
    texList.append(NoeTexture(texName, texWidth, texHeight, texData, noesis.NOESISTEX_RGBA32))

def boTexXbox(tex, texList, texOffset, texName):
    tex.seek(texOffset + 0x4)
    bmpOffset = tex.readUInt() + texOffset
    tex.seek(texOffset + 0x34)
    texFmt = tex.readUInt()
    texWidth = tex.readUInt()
    texHeight = tex.readUInt()
    bitDepth = tex.readUInt()
    if bitDepth in {4, 8, 32}:
        newFmtRev = False
        tex.seek(texOffset + 0x68)
    else:
        newFmtRev = True
        tex.seek(texOffset + 0x64)
        bitDepth = tex.readUByte()
    tex.seek(0x1, 1)
    palCount = tex.readUByte()
    if not texName:
        tex.seek(texOffset + (0x44 if newFmtRev else 0x48))
        texName = tex.readString()

    if BoDebug:
        print("\nXbox texture detected! ({}er revision)".format("New" if newFmtRev else "Old")
            + "\nTexture name: {}".format(os.path.split(texName)[1])
            + "\nTexture offset: 0x{:X}".format(texOffset)
            + "\nTexture data offset: 0x{:X}".format(bmpOffset)
            + "\nTexture dimensions: {} x {}".format(texWidth, texHeight)
            + "\nTexture bit depth: {}".format(bitDepth)
            + "\nTexture format: 0x{:X} ({})".format(texFmt, {0xB: "Paletted", 0xC: "DXT1",
                                                              0xE: "DXT3", 0xF: "DXT5",
                                                              0x3A: "RGBA"}.get(texFmt))
            + "\nPalette amount: {}".format(palCount))

    tex.seek(bmpOffset)

    wPad = boCalcAlign(texWidth, 4) if texWidth % 4 != 0 else texWidth
    hPad = boCalcAlign(texHeight, 4) if texHeight % 4 != 0 else texHeight

    if texFmt == 0x0B:
        texData = rapi.imageFromMortonOrder(tex.readBytes(texWidth * texHeight), texWidth, texHeight, 1)
        tex.seek(texOffset + 0x14)
        for pal in range(palCount):
            palOffset = tex.readUInt() + texOffset
            curPalOffset = tex.getOffset()
            tex.seek(palOffset)
            if not tex.readBytes(4) in {b"\x01\x00\x03\x00", b"\x01\x00\x03\xC0"}:
                noesis.doException(BoExcFmt + "Invalid palette header!")
            palDataOffset = tex.readUInt() + texOffset

            if BoDebug:
                print("Palette {} offset: 0x{:X}".format(pal + 1, palOffset)
                    + "\nPalette {} data offset: 0x{:X}".format(pal + 1, palDataOffset))

            tex.seek(palDataOffset)
            palData = boTexPalRead(tex, bitDepth)
            texPalData = rapi.imageDecodeRawPal(texData, palData, texWidth, texHeight, 8, "B8G8R8A8")
            texList.append(NoeTexture(boSetPalName(texName, palCount, pal), texWidth, texHeight, texPalData, noesis.NOESISTEX_RGBA32))
            tex.seek(curPalOffset)
        return

    elif texFmt == 0x0C:
        texFmt = noesis.NOESISTEX_DXT1
        texData = tex.readBytes(wPad * hPad // 2)
    elif texFmt == 0x0E:
        texFmt = noesis.NOESISTEX_DXT3
        texData = tex.readBytes(wPad * hPad)
    elif texFmt == 0x0F:
        texFmt = noesis.NOESISTEX_DXT5
        texData = tex.readBytes(wPad * hPad)
    elif texFmt == 0x3A:
        texFmt = noesis.NOESISTEX_RGBA32
        texData = rapi.imageFromMortonOrder(tex.readBytes(texWidth * texHeight * 4), texWidth, texHeight, 4)
    else:
        noesis.doException(BoExcFmt + hex(texFmt))

    texList.append(NoeTexture(texName, texWidth, texHeight, texData, texFmt))

def boTexXbox360(tex, texList, texOffset, texName, palOffset):
    tex.seek(texOffset)
    if not texName:
        texName = tex.readString()
    tex.seek(texOffset + 0x20)
    texWidth = tex.readUShort()
    texHeight = tex.readUShort()
    tex.seek(texOffset + 0x26)
    palCount = tex.readUByte()
    tex.seek(texOffset + 0x2C)
    texSize = tex.readUInt()
    tex.seek(texOffset + 0x48)
    texFmt = tex.readUInt()

    if BoDebug:
        print("\nXbox 360 texture detected!"
            + "\nTexture name: {}".format(os.path.split(texName)[1])
            + "\nTexture size: 0x{:X}".format(texSize)
            + "\nTexture offset: 0x{:X}".format(texOffset)
            + "\nTexture dimensions: {} x {}".format(texWidth, texHeight)
            + "\nTexture format: 0x{:X} ({})".format(texFmt, {0x2: "8-bit", 0x52: "DXT1",
                                                              0x53: "DXT3", 0x54: "DXT5",
                                                              0x86: "ARGB"}.get(texFmt)))
        if palOffset:
            print("Palette offset: 0x{:X}".format(palOffset)
                + "\nPalette amount: {}".format(palCount))

    tex.seek(texOffset + 0x1000)
    texData = boTexFixWidth(tex, texWidth, 256, texHeight) if texFmt == 0x02 and texWidth < 256 else tex.readBytes(texSize - 0x1000)

    if texFmt == 0x02:
        texFmt = noesis.NOESISTEX_RGBA32
        if not palCount:
            texData = rapi.imageDecodeRaw(texData, texWidth, texHeight, "A8")
        else:
            tex.seek(palOffset + 0x1000)
            for pal in range(palCount):
                palData = tex.readBytes(0x400)
                texPalData = rapi.imageDecodeRawPal(texData, palData, texWidth, texHeight, 8, "A8R8G8B8")
                texList.append(NoeTexture(boSetPalName(texName, palCount, pal), texWidth, texHeight, texPalData, texFmt))
            return

    elif texFmt == 0x52:
        texFmt = noesis.NOESISTEX_DXT1
        texData = rapi.imageUntile360DXT(rapi.swapEndianArray(texData, 2), texWidth, texHeight, 8)
    elif texFmt == 0x53:
        texFmt = noesis.NOESISTEX_DXT3
        texData = rapi.imageUntile360DXT(rapi.swapEndianArray(texData, 2), texWidth, texHeight, 16)
    elif texFmt == 0x54:
        texFmt = noesis.NOESISTEX_DXT5
        texData = rapi.imageUntile360DXT(rapi.swapEndianArray(texData, 2), texWidth, texHeight, 16)
    elif texFmt == 0x86:
        texFmt = noesis.NOESISTEX_RGBA32
        texData = rapi.imageDecodeRaw(rapi.imageUntile360Raw(texData, texWidth, texHeight, 4), texWidth, texHeight, "A8R8G8B8")
    else:
        noesis.doException(BoExcFmt + hex(texFmt))

    texList.append(NoeTexture(texName, texWidth, texHeight, texData, texFmt))

def boTexParse(tex, texEndian, texList, texOffset, texName=None, texExtra=None):
    texSystem = boTexGetSystem(tex, texEndian, texOffset)

    if texSystem == BoPS2:
        boTexPS2(tex, texList, texOffset, texName, texExtra)
    elif texSystem == BoPSP:
        boTexPSP(tex, texList, texOffset)
    elif texSystem == BoXbox:
        boTexXbox(tex, texList, texOffset, texName)
    elif texSystem == BoXbox360:
        boTexXbox360(tex, texList, texOffset, texName, texExtra)




#   #####   ######    #####   ##   ##  ##  ##   ##  #######   ######  
#  ##   ##  ##   ##  ##   ##  ##   ##  ##  ##   ##  ##       ##       
#  #######  ######   ##       #######  ##   ## ##   #####     #####   
#  ##   ##  ##   ##  ##   ##  ##   ##  ##   #####   ##            ##  
#  ##   ##  ##   ##   #####   ##   ##  ##    ###    #######  ######   


def boArcTxdParse(arc, texList, startOffset=0x0):
    arc.seek(startOffset)
    if arc.readBytes(8) == G_TEXDIC[::-1]:
        arc.setEndian(NOE_BIGENDIAN)
        arcEndian = "big"
    else:
        arcEndian = "little"

    texCount = arc.readUInt()
    offStart = arc.readUInt() + startOffset
    arc.seek(offStart)
    for tex in range(texCount):
        texNum = arc.readUInt64()
        texOffset = arc.readUInt() + startOffset
        curOffset = arc.getOffset() + 0x4
        boTexParse(arc, arcEndian, texList, texOffset)
        if BoDebug:
            print("Texture {} of {}".format(texNum, texCount))
        arc.seek(curOffset)

def boArcMdlBxv(data, mdlList):
    rapi.processCommands("-texnorepfn")
    arc = NoeBitStream(boDecZlib(data) if data.startswith(b"\x78\xDA") else data)
    matList = list()
    texList = list()

    arcVer, arcEndian = boGetVerEndian(arc)

    arc.seek(0x60)
    if arcVer < 0x20:
        texOffset = arc.readUInt()
        boTexParse(arc, arcEndian, texList, texOffset)

    else:  # Xbox 360 only
        for tex in range(19):
            texOffset = arc.readUInt()
            if texOffset != 0:
                curTexOffset = arc.getOffset()
                arc.seek(texOffset + 0x48)
                if arc.readUInt() != 2:
                    # Non-paletted texture
                    boTexParse(arc, arcEndian, texList, texOffset)

                else:
                    texName = boTexGetName(arc, arcEndian, texOffset)
                    arc.seek(curTexOffset)
                    for pal in range(19 - tex):
                        palOffset = arc.readUInt()
                        if palOffset != 0:
                            curPalOffset = arc.getOffset()
                            palName = boTexGetName(arc, arcEndian, palOffset)

                            arc.seek(palOffset + 0x48)
                            if palName == texName and arc.readUInt() == 0x86:
                                boTexParse(arc, arcEndian, texList, texOffset, texExtra=palOffset)
                                # Remove entry in memory to avoid being picked up as a texture
                                arc.seek(curPalOffset - 4)
                                arc.writeUInt(0)
                                break

                            arc.seek(curPalOffset)
                arc.seek(curTexOffset)

    #if not BoModels:
    boSetDummyMdl(mdlList, texList)
    return True

def boArcMdlDatStatic(data, mdlList, matList=None, texList=None, mdlExport=True):
    rapi.processCommands("-texnorepfn")
    arc = NoeBitStream(boDecZlib(data) if data.startswith(b"\x78\xDA") else data)
    if matList is None and texList is None:
        # To allow calling through boArcMdlDatStream
        matList = list()
        texList = list()

    arcVer, arcEndian = boGetVerEndian(arc)

    if arcVer <= 0x25:  # B3 demo, Pre-Alpha US_C4
        arc.seek(0x14)
        texCount = arc.readUInt()
    else:
        arc.seek(0x16)
        texCount = arc.readUShort()
    texArrayOffset = arc.readUInt()

    texName = dict()
    arc.seek(texArrayOffset)
    for tex in range(texCount):
        texOffset = arc.readUInt()
        curTexOffset = arc.getOffset()
        boTexParse(arc, arcEndian, texList, texOffset)
        texName[texOffset] = boTexGetName(arc, arcEndian, texOffset)
        arc.seek(curTexOffset)

        if BoDebug:
            print("Texture {} of {}".format(tex + 1, texCount))

    arc.seek(0x8)
    matOffset = arc.readUInt()
    matCount = arc.readUShort()
    animCount = arc.readUShort()
    animOffset = arc.readUInt()

    arc.seek(matOffset)
    for mat in range(matCount):
        mat = NoeMaterial(BoMatName.format(mat), "")
        mat.setMetal(0, 0)  # For some reason set to 1 by default in Noesis

        matOffset = arc.getOffset()
        matType = arc.readUInt()  # Render type (normal, wireframe, etc.)
        arc.seek(matOffset + 0xC)
        texPtrOffset = arc.readUInt()
        if texPtrOffset != 0x0:
            arc.seek(texPtrOffset + matOffset)
            texOffset = arc.readInt() + matOffset
            mat.setTexture(texName.get(texOffset))
        #else:  # Wrong
        #    # If there's no texture pointer, it reuses the previous one
        #    mat.setTexture(matList[-1].texName)

        # Texture rendering parameters
        arc.seek(matOffset + 0x26)
        if arc.readUShort() == 0:
            #noesis.doException("not PS2 mtl detected!!!")
            # PSP(?), Xbox, Xbox 360
            arc.seek(matOffset + 0x24)
            matAlphaTest = arc.readUByte() / 100  # Xbox
            matBlend2 = arc.readUByte()

            if not 0x2 <= matType <= 0x6:
                mat.setDefaultBlend(0)
            else:
                mat.setAlphaTest(matAlphaTest)
            #if matType == 0x2:
                #mat.setTexture(None)
                #mat.setEnvTexture(texName.get(texOffset))
            arc.seek(matOffset + 0x28)

        else:
            # PS2
            #arc.seek(matOffset + 0x20)
            #matInfo = [arc.readUShort() for mat in range(4)]
            #if matInfo[3] >> 8 not in {0x44, 0x64}:  # might be & 0xFF
            #    noesis.doException("0x{:02X}".format(matInfo[3] >> 8))
            #print(matInfo[3] >> 8)
            arc.seek(matOffset + 0x28)

        mat.setFlags2(noesis.NMATFLAG2_VCOLORMATDIFFUSE)
        matList.append(mat)

    if not BoModels or not mdlExport:
        boSetDummyMdl(mdlList, texList)
        return True

    rapi.rpgCreateContext()
    if arcEndian == "big":
        rapi.rpgSetOption(noesis.RPGOPT_BIGENDIAN, 1)

    arc.seek(0x1C)
    mdlCount = [arc.readUShort() for mdl in range(4)]

    for mdl, mdlType in enumerate(("backdrop", "chevron", "water", "reflection")):
        arc.seek(0x24 + mdl * 4)
        grpOffset = arc.readUInt()
        arc.seek(grpOffset)
        for grp in range(mdlCount[mdl]):
            grpOffset = arc.getOffset()
            subCount = arc.readUShort()
            arc.seek(0x2, 1)
            mdlOffset = arc.readUInt() + grpOffset + 0x40
            boMdlParseTrack(arc, arcEndian, matList, mdlOffset, subCount, grp, mdlType, grpOffset, arcVer)
            arc.seek(grpOffset + 0x8)
    try:
        mdl = rapi.rpgConstructModel()
    except:
        mdl = NoeModel()
    mdl.setModelMaterials(NoeModelMaterials(texList, matList))
    mdlList.append(mdl)
    return True

def boArcMdlDatStream(data, mdlList):
    #rapi.setPreviewOption("setAngOfs", "0 -90 180")
    rapi.rpgCreateContext()
    arc = NoeBitStream(data)
    matList = list()
    texList = list()

    arcEndian = boGetVerEndian(arc)[1]
    if arcEndian == "big":
        rapi.rpgSetOption(noesis.RPGOPT_BIGENDIAN, 1)

    statFile = os.path.join(os.path.split(rapi.getInputName())[0], "static.dat")
    if os.path.exists(statFile):
        statData = rapi.loadIntoByteArray(statFile)
        if boChkDatStatic(statData):
            boArcMdlDatStatic(statData, list(), matList, texList, True)
            # Change the last argument in the above call to  True  to load static models together

    #prevUnit = -1
    blkOffset = 0
    arcSize = arc.getSize()
    while arc.getOffset() < arcSize:
        arc.seek(blkOffset)
        subOffset = blkOffset + 0x50
        if arc.readUInt() != 0x1:
            continue
        unitIdx = arc.readUInt()
        blkSize = arc.readUInt() + blkOffset

        boMdlParseTrack(arc, arcEndian, matList, subOffset, 1, unitIdx)

        #prevUnit = unitIdx
        # reserved for mdlType LOD
        #while prevUnit == unitIdx and blkSize != arcSize:
        arc.seek(blkSize)
        blkOffset = arc.getOffset()
        arc.seek(0x4, 1)
        unitIdx = arc.readUInt()
        blkOffset = arc.readUInt() + blkOffset
        #arc.seek(blkSize)

    mdl = rapi.rpgConstructModel()
    mdl.setModelMaterials(NoeModelMaterials(texList, matList))
    mdlList.append(mdl)
    return True

def boArcTexDatEnviro(data, texList):
    rapi.processCommands("-texnorepfn")
    arc = NoeBitStream(data)

    arc.seek(0xB8)
    if arc.readBytes(4) == b"\x45\x44\x00\x03":
        arc.setEndian(NOE_BIGENDIAN)
        arcEndian = "big"
    else:
        arcEndian = "little"

    arcSize = arc.getSize()
    arc.seek(0x98)
    while True:
        texOffset = arc.readUInt()
        if not 0xB0 <= texOffset <= arcSize:
            break
        curTexOffset = arc.getOffset()
        boTexParse(arc, arcEndian, texList, texOffset)
        arc.seek(curTexOffset)
    return True

def boArcTexBinFE(data, texList):
    rapi.processCommands("-texnorepfn -fulltexpath")
    arc = NoeBitStream(data)

    if arc.readBytes(8) == G_MOVIEARRAY:
        arcEndian = "little"
    else:
        arc.setEndian(NOE_BIGENDIAN)
        arcEndian = "big"

    dirCount = arc.readUInt()
    dirOffset = arc.readUInt()

    arc.seek(dirOffset)
    for dir in range(dirCount):
        dirInfoOffset = arc.readUInt()
        curHdrOffset = arc.getOffset()

        arc.seek(dirInfoOffset)
        dirNameOffset = arc.readUInt()
        dirDataOffset = arc.readUInt()
        arc.seek(dirNameOffset)
        dirName = arc.readString()

        arc.seek(dirDataOffset + 0x4)
        texCount = arc.readUInt()

        #boPrepExportPath(dirName)

        if texCount != 0:
            boPrepExportPath(dirName)

            texArrayOffset = arc.readUInt() + dirDataOffset
            aptDataOffset = arc.readUInt() + dirDataOffset
            aptConstOffset = arc.readUInt() + dirDataOffset

            arc.seek(texArrayOffset)
            texOffset = [arc.readUInt() + dirDataOffset for tex in range(texCount)]
            texName = [boTexGetName(arc, arcEndian, tex) for tex in texOffset]
            texArray = dict(zip(texName, texOffset))

            boGetTexAptIndex(arc, aptDataOffset, int(texName[0][11:]) + 1 if texName[0].startswith("TexturePage") else int(texName[0]))
            for name in range(texCount):
                texNameOffset = arc.readUInt() + aptDataOffset
                texNameIndex = arc.readUInt()
                curAptOffset = arc.getOffset()
                arc.seek(texNameOffset)
                texName = os.path.join(dirName, arc.readString())

                for tex in texArray:
                    if tex == str(texNameIndex) or tex[11:] == str(texNameIndex - 1):
                        boTexParse(arc, arcEndian, texList, texArray.pop(tex), texName=texName)
                        break
                #else:
                #    noesis.doException("Couldn't find texture!")  # Rev 360 demo broke this...

                if BoDebug:
                    print("Directory name: {}".format(dirName)
                        + "\nDirectory offset: 0x{:X}".format(dirDataOffset)
                        + "\nApt Data offset: 0x{:X}".format(aptDataOffset)
                        + "\nApt constant file offset: 0x{:X}".format(aptConstOffset)
                        + "\nTexture array offset: 0x{:X}".format(texArrayOffset)
                        + "\nTexture {} of {}".format(texNameIndex, texCount))

                arc.seek(curAptOffset)

            for tex in texArray:  # Clear out remaining textures, if any
                texName = os.path.join(dirName, tex)
                boTexParse(arc, arcEndian, texList, texArray.get(tex), texName=texName)

                if BoDebug:
                    print("Directory name: {}".format(dirName)
                        + "\nDirectory offset: 0x{:X}".format(dirDataOffset)
                        + "\nApt Data offset: 0x{:X}".format(aptDataOffset)
                        + "\nApt constant file offset: 0x{:X}".format(aptConstOffset)
                        + "\nTexture array offset: 0x{:X}".format(texArrayOffset)
                        + "\nTexture {} of {}".format(tex, texCount))

        arc.seek(curHdrOffset)
    return True

def boArcTexBinLoad(data, texList):
    rapi.processCommands("-texnorepfn")
    arc = NoeBitStream(data)

    txdCount = arc.readUInt64()
    arcAlign = boCalcAlign(txdCount * 0x10 + 8, 0x800)
    for txd in range(txdCount):
        txdName = boDecGtID(arc.readUInt64())
        txdSize = arc.readUInt()
        txdOffset = arc.readUInt() + arcAlign
        curOffset = arc.getOffset()
        boArcTxdParse(arc, texList, txdOffset)
        if BoDebug:
            print("Texture dictionary name: {}".format(txdName)
                + "\nTexture dictionary offset: 0x{:X}".format(txdOffset))
        arc.seek(curOffset)
    return True

def boArcTexBinFont(data, texList):
    rapi.processCommands("-texnorepfn")
    arc = NoeBitStream(data)

    arcEndian = "little"
    fontMagic = arc.readBytes(4)
    if fontMagic in {b"v1.4", b"4.1v"}:
        if fontMagic == b"v1.4":
            arc.setEndian(NOE_BIGENDIAN)
            arcEndian = "big"
        texOffset = arc.readUInt()
        boTexParse(arc, arcEndian, texList, texOffset)
    else:
        arc.seek(0x0)
        fontName = arc.readString()
        arc.seek(0x70)
        texOffset = arc.readUInt()
        boTexParse(arc, arcEndian, texList, texOffset, texExtra=fontName)
    return True

def boArcTexTxd(data, texList):
    rapi.processCommands("-texnorepfn")
    arc = NoeBitStream(data)
    boArcTxdParse(arc, texList)
    return True

def boArcTexArena(data, texList):
    rapi.processCommands("-texnorepfn -fulltexpath")
    arc = NoeBitStream(data[16:])

    arenaName = arc.readString()
    arc.seek(0x40)
    texOffset = arc.readUInt()

    if arenaName.lower().endswith(".msh"):  # Texture
        boTexPSPArena(arc, texList, 0x0)

    elif texOffset != 0:  # Font
        boTexPSPArena(arc, texList, texOffset, fontName=arenaName)

    else:  # Frontend
        arc.seek(0x80)
        aptDataOffset = arc.readUInt()
        aptConstOffset = arc.readUInt()
        unkPtrOffset = arc.readUInt()
        texPtrOffset = arc.readUInt()

        arc.seek(texPtrOffset)
        texCount = arc.readUInt()
        if texCount != 0:
            texArrayOffset = arc.readUInt()

            # If the first texture index isn't 1, there are no texture names stored in Apt Data.
            if arc.readUInt() == 1:
                boGetTexAptIndex(arc, aptDataOffset, 1)
                texNameOffset = arc.readUInt()
                if texNameOffset < texArrayOffset:
                    arc.seek(-0x4, 1)

                    for tex in range(texCount):
                        texNameOffset = arc.readUInt() + aptDataOffset
                        texNameIndex = arc.readUInt()
                        curAptOffset = arc.getOffset()

                        arc.seek(texNameOffset)
                        texName = arc.readString()
                        arc.seek(texArrayOffset)
                        texOffsetIndex = arc.readUInt()
                        texOffset = arc.readUInt()
                        texArrayOffset = arc.getOffset()

                        boPrepExportPath(os.path.split(texName)[0])  # A few textures are named with a directory
                        boTexPSPArena(arc, texList, texOffset, texName=texName if texNameIndex == texOffsetIndex else None)

                        if BoDebug:
                            print("Texture {} of {} (Index: {})".format(tex + 1, texCount, texOffsetIndex))
                        arc.seek(curAptOffset)
                    return True

            # Fallback without texture names
            arc.seek(texArrayOffset)
            for tex in range(texCount):
                texOffsetIndex = arc.readUInt()
                texOffset = arc.readUInt()
                texArrayOffset = arc.getOffset()
                boTexPSPArena(arc, texList, texOffset)

                if BoDebug:
                    print("Texture {} of {} (Index: {})".format(tex + 1, texCount, texOffsetIndex))
                arc.seek(texArrayOffset)

        if BoDebug:
            print("\nApt Data offset: 0x{:X}".format(aptDataOffset + 16)
                + "\nApt constant file offset: 0x{:X}".format(aptConstOffset + 16)
                + "\nTexture pointer offset: 0x{:X}".format(texPtrOffset + 16))
    return True

def boArcFxp(fileName, fileLen, isChk):
    with open(fileName, "rb") as chk:
        if chk.read(0xC) != b"FX1?\x03" + bytes(7):
            return False
        if isChk:
            return True

    print("Loading archive parts...")
    arc = [NoeBitStream(rapi.loadIntoByteArray(fileName))]

    arc[0].seek(0xC)
    fileCount = arc[0].readUInt()
    arcSize = arc[0].readUInt64()
    nameData = arc[0].readUInt()
    infoSize = arc[0].readUInt()
    if arcSize != fileLen:
        arcCount = arc[0].readUInt()
    else:
        arcIdx = 0
        arcCount = 1
    arc[0].seek(0x80, 1)
    nameData += arc[0].getOffset()

    arcRoot, arcExt = os.path.splitext(fileName)
    for fxp in range(1, arcCount):
        fileName = arcRoot + str(fxp) + arcExt
        arc.append(NoeBitStream(rapi.loadIntoByteArray(fileName)))

    for sub in range(fileCount):
        nameOfs = arc[0].readUInt() + nameData
        fileSize = arc[0].readUInt()
        fileOfs = arc[0].readUInt() * 0x800
        if arcSize != fileLen:
            arcIdx = arc[0].readUByte()
            arc[0].seek(0x3, 1)
        else:
            arc[0].seek(0x18, 1)
        curArcPos = arc[0].getOffset()

        arc[0].seek(nameOfs)
        fileName = arc[0].readString()
        arc[arcIdx].seek(fileOfs)
        rapi.exportArchiveFile(fileName, arc[arcIdx].readBytes(fileSize))

        if BoDebug:
            print("\nFXP archive file detected! (Version 3)"
                + "\nFile name: {}".format(fileName)
                + "\nFile name offset: 0x{:X}".format(nameOfs)
                + "\nFile size: 0x{:X}".format(fileSize)
                + "\nFile offset: 0x{:X}".format(fileOfs)
                + "\nArchive part index: {}".format(arcIdx)
                + "\nFile {} of {}".format(sub + 1, fileCount))
        else:
            print("Extracted", fileName)
        arc[0].seek(curArcPos)
    return True

def blkArcTexDb(data, texList):
    rapi.processCommands("-texnorepfn")
    arc = NoeBitStream(data)

    arcVer = arc.readUInt()
    if arcVer != 4:
        arc.seek(0x1C)
    txdOffset = arc.readUInt()
    boArcTxdParse(arc, texList, txdOffset)
    return True

def blkArcTexBinGlob(data, texList):
    rapi.processCommands("-texnorepfn")
    arc = NoeBitStream(data)

    arc.seek(0x4)
    txdOffset = arc.readUInt()
    boArcTxdParse(arc, texList, txdOffset)
    return True

def blkArcTexBinGuns(data, texList):
    rapi.processCommands("-texnorepfn")
    arc = NoeBitStream(data)

    txdOffset = arc.readUInt()
    boArcTxdParse(arc, texList, txdOffset)
    return True

def blkArcTexBinLevel(data, texList):
    rapi.processCommands("-texnorepfn")
    arc = NoeBitStream(data)

    chkVer = arc.readUInt()
    arc.seek({
        0x0A: 0x2BC,
        0x11: 0x390
    }.get(chkVer))
    txdOffset = arc.readUInt()
    boArcTxdParse(arc, texList, txdOffset)
    return True

def blkArcTexBinStLevel(data, texList):
    rapi.processCommands("-texnorepfn")
    arc = NoeBitStream(data)

    arc.seek(0xC)
    hdrOffset = arc.readUInt()
    arc.seek(0x4)
    txdOffset = arc.readUInt() + hdrOffset
    boArcTxdParse(arc, texList, txdOffset)
    return True

def blkArcTexBinStUnit(data, texList):
    rapi.processCommands("-texnorepfn")
    arc = NoeBitStream(data)

    arc.seek(0x8)
    hdrOffset = arc.readUInt()
    arc.seek(hdrOffset + 0x1C)
    txdOffset = arc.readUInt() + hdrOffset
    boArcTxdParse(arc, texList, txdOffset)
    return True

def blkArcTexBinUnit(data, texList):
    rapi.processCommands("-texnorepfn")
    arc = NoeBitStream(data)

    arcVer = arc.readUInt()
    if arcVer == 0x0C:
        arc.seek(0x18)
    elif 0x16 <= arcVer <= 0x18:
        arc.seek(0x24)
    txdOffset = arc.readUInt()
    boArcTxdParse(arc, texList, txdOffset)
    return True
