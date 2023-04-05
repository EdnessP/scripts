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
#       Burnout Legends         (PSP)
#       Burnout Revenge         (PS2, Xbox, X360)
#       Burnout Dominator       (PS2, PSP)
#       Need for Speed: Shift   (PSP)

# This plugin is brought to you by the Burnout Modding community.
#               burnout.wiki  |  discord.gg/8zxbb4x              

# TODO:
#   All track collisions and objects
#   All streamed track materials
#   All vehicle model support
#   All track material parsing (PS2 done?)
#   PS2 two-point (Line) meshes

# Written by Edness   v0.7d   2021-06-23 - 2023-04-05

BoDebug = False
BoModels = False

BoDmg = False  # Damage models
BoLOD = False  # LOD models

from inc_noesis import *
import zlib

def registerNoesisTypes():
    handleBxv = noesis.register("Burnout 3Td, Leg, Rev, Dom, NFS Shift - Vehicles", ".bgv;.btv")
    noesis.setHandlerTypeCheck(handleBxv, boChkBxv)
    noesis.setHandlerLoadModel(handleBxv, boArcMdlBxv)

    # Loads  streamed.dat  and  PropInst.dat  if those are needed and exist in the same folder
    handleDatStat = noesis.register("Burnout 3Td, Leg, Rev, Dom, NFS Shift - Static", ".dat")
    noesis.setHandlerTypeCheck(handleDatStat, boChkDatStatic)
    noesis.setHandlerLoadModel(handleDatStat, boArcMdlDatStatic)

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

def boChkDatPropInst(data):
    chk = NoeBitStream(data)
    chkVer, chkEndian = boGetVerEndian(chk)
    if chkEndian is not None:
        chkSize = chk.readUInt()
        if 0x2 <= chkVer <= 0x3 and chkSize == chk.getSize():
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


def boMdlGetMatIdx(mdl, mdlVer, mdlOffset, grpOffset, matOffset):
    # Last known version to calculate the static pointer from the group offset is 0x30
    # Earliest known version to calculate it from the model offset is 0x32
    matIdxOffset = mdl.readUInt()
    if matIdxOffset == 0:  # Streamed
        matIdxOffset = mdlOffset + matOffset
    else:                  # Static
        matIdxOffset += grpOffset if mdlVer <= 0x32 else mdlOffset - 0x40
    #else:
    #    noesis.doException("Unhandled material index pointer")
    return matIdxOffset

def boMdlVtxClrPreview(clrData, clrOffset, clrStride):
    # Force 100% vertex color opacity while previewing
    # If the vertex color data type is set to RGB, it doesn't default the alpha to FF
    # but instead to 00, which means the whole model would become invisible in Noesis
    if not rapi.noesisIsExporting():
        clrData[clrOffset + 3::clrStride] = b"\xFF" * (len(clrData) // clrStride)

    # Multiply the vertex RGB by 2 for better previewing (seems closer to in-game)
    # and the range always being 0-128 (but occasionally 129 in Dominator though?)
    for clr in range(3):
        clrChannel = clrData[clrOffset + clr::clrStride]
        clrMultiply = list()
        clrTest = sorted(set(clrChannel))[-1]
        if 129 < clrTest < 255:
            noesis.messagePrompt("VtxClr mul {}\nContact Edness!".format(clrTest))
        for byte in clrChannel:
            byte *= 2
            if byte > 255:
                byte = 255
            clrMultiply.append(byte)
        clrData[clrOffset + clr::clrStride] = bytes(clrMultiply)

def boMdlXboxReadLine(mdl, faceCount):
    # Converts Xbox/Xbox 360 line meshtype to fake triangles
    faceData = list()
    for idx in range(faceCount):
        faceData.extend(mdl.readBytes(0x2) + mdl.readBytes(0x2) * 2)
    return bytearray(faceData)

def boMdlPS2(mdl, vifOffset):
    def boPS2Read12(rData):  # (1 << 12) - 1
        rSize = len(rData) // 2  # Would be  // vif.numElems  if it weren't for car UVs
        rData = [int / 0xFFF for int in noeUnpack("<{}h".format(rSize), rData)]
        return noePack("<{}f".format(rSize), *rData)

    mdl.seek(vifOffset)
    vifSize = mdl.readUShort()
    mdl.seek(vifOffset + 0x4)
    vifData = rapi.unpackPS2VIF(mdl.read(0xC + vifSize * 0x10))
    #print("MdlOffs", hex(vifOffset))  # NoePS2VIFUnpack

    # Many submeshes have both V3-8 and V4-8 data, V3-8 seems to take precedence for
    # vertex colors. If V3-8 (RGB24) data doesn't exist then V4-8 is used as RGBA32.
    # Otherwise V4-8 is used for some reflection stuff which is usually placed after
    # V3-8, except for some cases where it's placed before V3-8 data. (if no V2-16?)
    # And for vehicles V3-8 seems to be used for normals and V4-16 is split in half,
    # left half being used for UVs and right half being used for reflection stuff?
    clr24 = True
    clr32 = True
    vifOrder = [(vifData[0].numElems, vifData[0].elemBits)]
    for idx in range(1, len(vifData)):
        vifIdx = (vifData[idx].numElems, vifData[idx].elemBits)
        if vifIdx == vifOrder[0] and not len(vifData) % idx:
            break  # not exactly accurate with PropInst data
        elif vifIdx == (3, 8):
            clr32 = False
        elif vifIdx == (4, 16):
            clr24 = False
        # if V4-16 exists, V3-8 is used as normals?
        vifOrder.append(vifIdx)

    if BoDebug:
        print("VIF data offset: 0x{:X}".format(vifOffset)
            + "\nVIF data size: 0x{:X}".format(0x10 + vifSize * 0x10)
            + "\nVIF data amount: {}".format(len(vifData))
            + "\nVIF data order: {}".format(", ".join(["V{}-{}".format(*fmt) for fmt in vifOrder])))

    vertData = list()
    clrData = list()
    nrmData = list()
    uvData = list()
    for vif in vifData:
        if vif.elemBits == 32 and vif.numElems == 4:    # Vertices, Normals?
            for idx in range(len(vif.data) // 0x10):
                if vif.data[0xC + idx * 0x10:][:0x4] not in (b"\x00\x00\x00\x00", b"\x00\x80\x00\x00"):
                    break
            else:
                vertData.append(vif.data)
                continue
            for idx in range(len(vif.data) // 0x40):
                if vif.data[0x30 + idx * 0x40:][:0x10] != bytes(16):
                    break
            else:
                continue  #nrmData.append?
            noesis.doException("Unhandled V2-32 data")

        elif vif.elemBits == 32 and vif.numElems == 2:  # UVs (PropInst)
            uvData.append(vif.data)

        elif vif.elemBits == 16 and vif.numElems == 2:  # UVs (Tracks)
            uvData.append(boPS2Read12(vif.data))

        elif vif.elemBits == 16 and vif.numElems == 4:  # UVs (Vehicles), Envmap?
            vifSplitUV = list()
            vifSplitUnk = list()  # Envmap?
            for idx in range(len(vif.data) // 0x10):  # (vif.elemBits // 8 * vif.numElems)
                #(vifSplitUnk if idx % 2 else vifSplitUV).extend(vif.data[idx * 8:][:8])
                vifSplitUV.extend(vifData[idx * 8:][:8])
                vifSplitUnk.extend(vifData[8 + idx * 8:][:8])
            uvData.append(boPS2Read12(bytes(vifSplitUV)))

        elif vif.elemBits == 8 and vif.numElems == 3:   # Colors (RGB24), Normals?
            if clr24:
                # Vertex colors need to be changed from RGB to RGBA
                clrData.append(rapi.imageDecodeRaw(vif.data, len(vif.data) // 3, 1, "R8G8B8"))

        elif vif.elemBits == 8 and vif.numElems == 4:   # Colors (RGBA32), Envmap?
            if clr32:
                clrData.append(vif.data)
            # if RGB24 exists, then these are used for some reflection stuff(?)
            # datasize seems to always be 3 more than vertex data, and never has uvs?

        else:
            noesis.doException("Unhandled VIF data: (V{}-{}) {}".format(vif.numElems, vif.elemBits, vif))

    if not clrData:
        clrData = [bytearray(b"\xFF" * (len(vtx) // 0x10 * 4)) for vtx in vertData]

    if not uvData:
        uvData = [bytes(len(vtx) // 0x10 * 8) for vtx in vertData]

    for vertData, clrData, uvData in zip(vertData, clrData, uvData):
        faceData = list()
        vertSize = len(vertData) // 0x10
        for vtx in range(vertSize - 2):
            if vertData[vtx * 0x10:][:0x30].endswith(bytes(4)):
                faceData.extend((vtx, vtx + 2, vtx + 1) if vtx % 2 else (vtx, vtx + 1, vtx + 2))

        faceData = bytes(faceData)
        boMdlVtxClrPreview(clrData, 0x0, 0x4)

        # Prevent two-point wire submeshes from breaking, can't be fixed until streamed materials are fixed first
        if vertSize > 2:
            rapi.rpgBindPositionBuffer(vertData, noesis.RPGEODATA_FLOAT, 0x10)
            rapi.rpgBindColorBuffer(clrData, noesis.RPGEODATA_UBYTE, 0x4, 4)
            rapi.rpgBindUV1Buffer(uvData, noesis.RPGEODATA_FLOAT, 0x8)
            rapi.rpgCommitTriangles(faceData, noesis.RPGEODATA_UBYTE, len(faceData), noesis.RPGEO_TRIANGLE)

def boMdlPS2Track(mdl, mdlVer, mdlOffset, mdlBaseName, grpOffset):
    mdl.seek(mdlOffset)
    subCount = mdl.readUInt()
    subOffset = mdl.readUInt() + mdlOffset
    matIdxOffset = boMdlGetMatIdx(mdl, mdlVer, mdlOffset, grpOffset, 0x24)

    mdl.seek(matIdxOffset)
    matIdx = [mdl.readUShort() for mat in range(subCount)]

    if BoDebug:
        print("\nPlayStation 2 track model detected!"
            + ("\nModel group offset: 0x{:X}".format(grpOffset) if grpOffset is not None else "")
            + "\nModel info offset: 0x{:X}".format(mdlOffset)  # - 0x40
            + "\nSubmesh info offset: 0x{:X}".format(subOffset)
            + "\nSubmesh amount: {}".format(subCount)
            + "\nMaterial index offset: 0x{:X}".format(matIdxOffset))

    for blk in range(subCount):
        mdlName = mdlBaseName + "{:03}".format(blk)
        rapi.rpgSetName(mdlName)
        rapi.rpgSetMaterial(BoMatName.format(matIdx[blk]))

        if BoDebug:
            print("\nSubmesh data offset: 0x{:X}".format(subOffset))

        for sub in range(2):
            mdl.seek(subOffset + 0xC + 0x10 * sub)
            vifOffset = mdl.readUInt() + subOffset
            if vifOffset != subOffset:  # not NULL
                boMdlPS2(mdl, vifOffset)

        if BoDebug:
            print("Submesh {} of {}".format(blk + 1, subCount))
        subOffset += 0x40

def boMdlPS2PropInst(mdl, mdlVer, mdlOffset, mdlBaseName):
    if mdlBaseName.startswith("prop") and mdlVer >= 0x30:
        # Revenge/Dominator props
        mdl.seek(mdlOffset + 0x44)
        matIdx = [mdl.readUShort() for mat in range(3)]
        print("{:X}".format(mdlOffset))

        for idx in range(3 if BoDmg else 1):
            mdl.seek(mdlOffset + 0x30 + 0x4 * idx)
            subOffset = mdl.readUInt() + mdlOffset
            if subOffset > mdl.getSize():
                continue

            for lod in range(2 if BoLOD else 1):
                subOffset += 0x8 * lod

                rapi.rpgSetName(mdlBaseName + "dmg_{:03}_lod_{:03}".format(idx, lod))
                rapi.rpgSetMaterial(BoMatName.format(matIdx[idx]))

                for sub in range(2):
                    mdl.seek(subOffset + 0x4 * sub)
                    vifOffset = mdl.readUInt() + subOffset
                    if vifOffset != subOffset:  # not NULL
                        boMdlPS2(mdl, vifOffset)

    else:
        # All instances and B3 props
        mdlOffset += 0x20

        mdl.seek(mdlOffset + 0x18)
        matIdx = [mdl.readUShort() for mat in range(3)]

        mdl.seek(mdlOffset)
        for idx in range(3 if BoLOD else 1):
            subOffset = mdlOffset + 0x8 * idx

            mdlName = mdlBaseName + "lod_{:03}".format(idx)
            rapi.rpgSetName(mdlName)
            rapi.rpgSetMaterial(BoMatName.format(matIdx[idx]))

            for sub in range(2):
                mdl.seek(subOffset + 0x4 * sub)
                vifOffset = mdl.readUInt() + subOffset
                if vifOffset != subOffset:  # not NULL
                    boMdlPS2(mdl, vifOffset)

def boMdlPSPTrack(mdl, mdlVer, mdlOffset, mdlBaseName, grpOffset):
    def boPSPRead11(rSize):  # (1 << 11 ) - 1
        rData = [int / 0x7FF for int in noeUnpack("<{}h".format(rSize), mdl.readBytes(rSize * 2))]
        return noePack("<{}f".format(rSize), *rData)

    # Parts of this will need to be moved to its own func (11-bit UV & Face indices generation)

    mdl.seek(mdlOffset)
    subOffset = mdl.readUInt() + mdlOffset
    subCount = mdl.readUInt()
    matIdxOffset = boMdlGetMatIdx(mdl, mdlVer, mdlOffset, grpOffset, 0x24 if mdlVer < 0x30 else 0x104)

    mdl.seek(matIdxOffset)
    matIdx = [mdl.readUShort() for mat in range(subCount)]

    # BoDebug

    for blk in range(subCount):
        mdlName = mdlBaseName + "{:03}".format(blk)
        rapi.rpgSetName(mdlName)
        rapi.rpgSetMaterial(BoMatName.format(matIdx[blk]))

        vertOffset = subOffset + 0xA0 * blk

        mdl.seek(vertOffset + 0x40)
        vertType = mdl.readUInt()
        if vertType not in {1, 4}:
            noesis.doException("Unhandled PSP vertex type")
        vertCount = mdl.readUInt()
        vertData = mdl.readUInt() + vertOffset
        if vertCount == 0:
            continue  # classic Legends...

        mdl.seek(vertOffset + 0x8C)
        faceData = mdl.readUInt() + vertOffset
        faceCount = mdl.readUInt()
        #mdlData = rapi.decodePSPVert(0x12000116)

        mdl.seek(vertOffset + 0x60)
        mdlTransform = [
            (mdl.readFloat(), 0, 0),
            (0, mdl.readFloat(), 0),
            (0, 0, mdl.readFloat()),
        ]
        mdl.seek(vertOffset + 0x50)
        mdlTransform.append((mdl.readFloat(), mdl.readFloat(), mdl.readFloat()))
        rapi.rpgSetTransform(NoeMat43(mdlTransform))
        #rapi.rpgSetTransform(NoeMat43(*mdlScale, mdlPos))

        if (faceData - vertData) // 0xC != vertCount:
            noesis.doException("Unhandled datatypes")

        mdl.seek(vertData)
        # no vertex colors & broken UVs (bound as 16-bit when they're 11-bit)
        #vertData = mdl.readBytes(vertCount * 0xC)
        #rapi.decodePSPVert(0x12000116).bindBuffers(vertData)

        uvData = list()
        clrData = list()
        vertData = list()
        for vtx in range(vertCount):
            uvData.extend(boPSPRead11(0x2))
            clrData.extend(mdl.readBytes(0x2))
            vertData.extend(mdl.readBytes(0x6))

        uvData = bytes(uvData)
        vertData = bytes(vertData)
        clrData = rapi.imageDecodeRaw(bytes(clrData), vertCount, 1, "R5G5B5A1")
        if mdlVer > 0x27:  # Legends fucking sucks LOL
            boMdlVtxClrPreview(clrData, 0x0, 0x4)

        rapi.rpgBindPositionBuffer(vertData, noesis.RPGEODATA_SHORT, 0x6)
        rapi.rpgBindColorBuffer(clrData, noesis.RPGEODATA_UBYTE, 0x4, 4)
        rapi.rpgBindUV1Buffer(uvData, noesis.RPGEODATA_FLOAT, 0x8)

        mdl.seek(faceData)
        if vertType == 0x1:  # Lines
            faceData = list()
            if faceCount - 1 != 1:
                noesis.doException("wire stuff")
            faceData.extend(range(mdl.readUInt() & 0xFFFF))
            for idx in range(len(faceData) - 1, 0, -2):
                faceData.insert(idx, faceData[idx])
            rapi.rpgCommitTriangles(bytes(faceData), noesis.RPGEODATA_UBYTE, len(faceData), noesis.RPGEO_TRIANGLE)
        elif vertType == 0x4:  # Tri-Strips
            faceData = [-1, -1]
            for face in range(faceCount - 1):
                faceRange = faceData[-2] + 1
                # this is kinda messy looking, it'll be improved if possible
                faceData.extend(range(faceRange, faceRange + mdl.readUInt() & 0xFFFF))
                faceData.append(-1)
            faceData = faceData[2:]
            faceCount = len(faceData)
            faceData = noePack("<{}h".format(faceCount), *faceData)
            rapi.rpgCommitTriangles(faceData, noesis.RPGEODATA_USHORT, faceCount, noesis.RPGEO_TRIANGLE_STRIP)

    rapi.rpgSetTransform(None)

def boMdlPSPPropInst(mdl, mdlVer, mdlOffset, mdlBaseName):
    pass

def boMdlXboxTrack(mdl, mdlVer, mdlOffset, mdlBaseName, grpOffset):
    mdl.seek(mdlOffset)
    if mdl.readUInt() != 0x1:
        noesis.doException("Invalid block header!")
    vertOffset = mdl.readUInt() + mdlOffset
    mdl.seek(mdlOffset + 0xC)
    subOffset = mdl.readUInt() + mdlOffset
    subCount = mdl.readUInt()
    matIdxOffset = boMdlGetMatIdx(mdl, mdlVer, mdlOffset, grpOffset, 0x34)

    if BoDebug:
        print("\nXbox track model detected!"
            + ("\nModel group offset: 0x{:X}".format(grpOffset) if grpOffset is not None else "")
            + "\nModel info offset: 0x{:X}".format(mdlOffset)  # - 0x40
            + "\nSubmesh info offset: 0x{:X}".format(subOffset)
            + "\nSubmesh amount: {}".format(subCount)
            + "\nMaterial index offset: 0x{:X}".format(matIdxOffset)
            + "\nVertex data offset: 0x{:X}".format(vertOffset))

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
    boMdlVtxClrPreview(vertData, 0x10, 0x1C)

    rapi.rpgBindPositionBuffer(vertData, noesis.RPGEODATA_FLOAT, 0x1C)
    rapi.rpgBindUV1BufferOfs(vertData, noesis.RPGEODATA_FLOAT, 0x1C, 0x14)
    rapi.rpgBindColorBufferOfs(vertData, noesis.RPGEODATA_UBYTE, 0x1C, 0x10, 4)

    for subIdx, (triFmt, faceCount, faceOffset) in enumerate(subData):
        mdlName = mdlBaseName + "{:03}".format(subIdx)
        rapi.rpgSetName(mdlName)
        rapi.rpgSetMaterial(BoMatName.format(matIdx[subIdx]))

        if BoDebug:
            print("\nFace data offset: 0x{:X}".format(faceOffset)
                + "\nFace index amount: {}".format(faceCount)
                + "\nTriangle format: {}".format(triFmt)
                + "\nSubmesh {} of {}".format(subIdx + 1, subCount))

        mdl.seek(faceOffset)
        if triFmt == 0x2:
            faceData = boMdlXboxReadLine(mdl, faceCount)
            faceCount = len(faceData) // 4
        elif triFmt == 0x6:
            faceData = mdl.readBytes(faceCount * 2)

        rapi.rpgCommitTriangles(faceData, noesis.RPGEODATA_USHORT, faceCount, BoXboxTris.get(triFmt))

def boMdlXboxPropInst(mdl, mdlVer, mdlOffset, mdlBaseName):
    pass

def boMdlXbox360Track(mdl, mdlVer, mdlOffset, mdlBaseName, grpOffset):
    mdl.seek(mdlOffset + 0x10)
    vertSize = mdl.readUInt() - 0x2  # For some reason it's always off by 2?
    vertOffset = mdl.readUInt() + mdlOffset
    vertCount = mdl.readUShort()
    mdl.seek(mdlOffset + 0x1C)
    subOffset = mdl.readUInt() + mdlOffset
    subCount = mdl.readUShort()
    mdl.seek(mdlOffset + 0x24)
    matIdxOffset = boMdlGetMatIdx(mdl, mdlVer, mdlOffset, grpOffset, 0x44)

    if BoDebug:
        print("\nXbox 360 track model detected!"
            + ("\nModel group offset: 0x{:X}".format(grpOffset) if grpOffset is not None else "")
            + "\nModel info offset: 0x{:X}".format(mdlOffset)  # - 0x40
            + "\nSubmesh info offset: 0x{:X}".format(subOffset)
            + "\nSubmesh amount: {}".format(subCount)
            + "\nMaterial index offset: 0x{:X}".format(matIdxOffset)
            + "\nVertex data offset: 0x{:X}".format(vertOffset)
            + "\nVertex data size: 0x{:X}".format(vertSize)
            + "\nVertex amount: {}".format(vertCount))

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
    boMdlVtxClrPreview(vertData, 0x18, 0x1C)

    rapi.rpgBindPositionBuffer(vertData, noesis.RPGEODATA_FLOAT, 0x1C)
    rapi.rpgBindUV1BufferOfs(vertData, noesis.RPGEODATA_FLOAT, 0x1C, 0x10)
    rapi.rpgBindColorBufferOfs(vertData, noesis.RPGEODATA_UBYTE, 0x1C, 0x18, 4)

    for subIdx, (faceSize, faceOffset, _faceCount, triFmt) in enumerate(subData):
        mdlName = mdlBaseName + "{:03}".format(subIdx)
        rapi.rpgSetName(mdlName)
        rapi.rpgSetMaterial(BoMatName.format(matIdx[subIdx]))

        if BoDebug:
            print("\nFace data offset: 0x{:X}".format(faceOffset)
                + "\nFace index amount: {}".format(_faceCount)  # likely wrong?
                + "\nTriangle format: {}".format(triFmt)
                + "\nSubmesh {} of {}".format(subIdx + 1, subCount))

        mdl.seek(faceOffset)
        if triFmt == 0x2:
            faceData = boMdlXboxReadLine(mdl, faceSize // 2)
            faceCount = len(faceData) // 4
        elif triFmt == 0x6:
            faceData = mdl.readBytes(faceSize)
            faceCount = faceSize // 2

        rapi.rpgCommitTriangles(faceData, noesis.RPGEODATA_USHORT, faceCount, BoXboxTris.get(triFmt))

def boMdlXbox360PropInst(mdl, mdlVer, mdlOffset, mdlBaseName):
    pass

def boMdlParseTrack(mdl, mdlVer, mdlSystem, mdlOffset, subCount, unitIdx, mdlType=None, grpOffset=None):
    # mdlType for streamed is reserved for LOD if is int? (maybe)
    for sub in range(subCount):
        mdlOffset += 0x40  # The first 0x40 bytes of each model header are some floats before actual info data starts
        mdlName = "unit_{:03}_sub_".format(unitIdx) if mdlType is None else "{}_grp_{:03}_mdl_{:03}_sub_".format(mdlType, unitIdx, sub)
        if mdlSystem == BoPS2:
            boMdlPS2Track(mdl, mdlVer, mdlOffset, mdlName, grpOffset)
            mdlOffset += 0x10
        elif mdlSystem == BoPSP:
            boMdlPSPTrack(mdl, mdlVer, mdlOffset, mdlName, grpOffset)
            mdlOffset += 0x10
        elif mdlSystem == BoXbox:
            boMdlXboxTrack(mdl, mdlVer, mdlOffset, mdlName, grpOffset)
            mdlOffset += 0x20
        elif mdlSystem == BoXbox360:
            boMdlXbox360Track(mdl, mdlVer, mdlOffset, mdlName, grpOffset)
            mdlOffset += 0x30

        if BoDebug:
            print("Mesh {} of {}".format(sub + 1, subCount))

def boMdlParsePropInst(mdl, mdlVer, mdlSystem, mdlOffset, subCount, mdlType, mdlIdx=None):
    def boPropInstSubSize():
        return 0x50 if mdlVer >= 0x30 and mdlType.startswith("prop") else {
            BoPS2: 0x50,
            BoPSP: 0x130,
            BoXbox: 0x70,
            BoXbox360: 0xE0
        }.get(mdlSystem)

    if mdlIdx is None:
        # For debugging, loads everything at their default position
        for sub in range(subCount):  # or alternatively separated every sub*x units
            rapi.rpgSetTransform(NoeMat43(((1, 0, 0), (0, 1, 0), (0, 0, 1), (0, 0, sub * 3))))
            mdlName = "{}_{:03}_".format(mdlType, sub)
            if mdlSystem == BoPS2:
                boMdlPS2PropInst(mdl, mdlVer, mdlOffset, mdlName)
            elif mdlSystem == BoPSP:
                boMdlPSPPropInst(mdl, mdlVer, mdlOffset, mdlName)
            elif mdlSystem == BoXbox:
                boMdlXboxPropInst(mdl, mdlVer, mdlOffset, mdlName)
            elif mdlSystem == BoXbox360:
                boMdlXbox360PropInst(mdl, mdlVer, mdlOffset, mdlName)
            mdlOffset += boPropInstSubSize()
        rapi.rpgSetTransform(None)
        return

    if mdlIdx >= subCount:
        noesis.doException("Tried loading prop {} out of {} total props".format(mdlIdx + 1, subCount))

    mdlOffset = mdlOffset + boPropInstSubSize() * mdlIdx
    mdlName = "{}_{:03}_".format(mdlType, mdlIdx)
    if mdlSystem == BoPS2:
        boMdlPS2PropInst(mdl, mdlVer, mdlOffset, mdlName)
    elif mdlSystem == BoPSP:
        boMdlPSPPropInst(mdl, mdlVer, mdlOffset, mdlName)
    elif mdlSystem == BoXbox:
        boMdlXboxPropInst(mdl, mdlVer, mdlOffset, mdlName)
    elif mdlSystem == BoXbox360:
        boMdlXbox360PropInst(mdl, mdlVer, mdlOffset, mdlName)




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
    # Originally the idea was to allow potential multi-system textures in an archive
    # but detecting the system for static model data is a pain, so just returning this
    return texSystem




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
    #rapi.rpgCreateContext()
    #matList.append(NoeMaterial("mat0", texList[0].name))
    #rapi.rpgSetMaterial("mat0")
    #boMdlPS2(arc, 0x15100)
    #mdl = rapi.rpgConstructModel()
    #mdl.setModelMaterials(NoeModelMaterials(texList, matList))
    #mdlList.append(mdl)
    return True

def boArcMdlDatStatic(data, mdlList):
    #rapi.setPreviewOption("setAngOfs", "0 -60 120")  # 0 -60 120 # 0 -240 60
    rapi.processCommands("-texnorepfn")  # -rotate 0 15 0 # 0 -15 0
    arc = NoeBitStream(boDecZlib(data) if data.startswith(b"\x78\xDA") else data)
    texList = list()

    arcVer, arcEndian = boGetVerEndian(arc)

    if arcVer <= 0x25:  # B3 demo & pre-alpha US_C4
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
        arcSystem = boTexParse(arc, arcEndian, texList, texOffset)
        texName[texOffset] = boTexGetName(arc, arcEndian, texOffset)
        arc.seek(curTexOffset)

        if BoDebug:
            print("Texture {} of {}".format(tex + 1, texCount))

    if not BoModels:
        boSetDummyMdl(mdlList, texList)
        return True

    rapi.rpgCreateContext()
    matList = list()

    if arcEndian == "big":
        rapi.rpgSetOption(noesis.RPGOPT_BIGENDIAN, 1)

    arc.seek(0x8)
    matOffset = arc.readUInt()
    matCount = arc.readUShort()
    animCount = arc.readUShort()
    animOffset = arc.readUInt()

    # Materials (to be moved into its own function loop)
    arc.seek(matOffset)
    for mat in range(matCount):
        mat = NoeMaterial(BoMatName.format(mat), "")
        mat.setMetal(0, 0)  # For some reason set to 1 by default in Noesis
        matOffset = arc.getOffset()

        matType = arc.readUInt()  # Render type (normal, wireframe, use alpha specular etc.) NEEDED FOR PS2 LINE DRAWS
        arc.seek(matOffset + 0xC)
        # The byte after the pointer offsets the index, but I don't think it's ever used (always NULL)
        texPtrOffset = arc.readInt() + arc.readByte() * 0x4
        if texPtrOffset != 0x0:
            arc.seek(texPtrOffset + matOffset)
            texOffset = arc.readInt() + matOffset
            mat.setTexture(texName.get(texOffset))

        # Texture rendering parameters
        matFlags = 0
        if arcSystem == BoPS2:
            arc.seek(matOffset + 0x20)
            matInfoAlpha = arc.readUInt()  # 0x20
            matInfo = arc.readUShort()  # 0x24
            if matInfo & 0x0020 or matType in {0x4, 0x5}:
                matFlags |= noesis.NMATFLAG_TWOSIDED
            #if matInfo & 0x0018:  # makes water show through?  also reflect heavily on cars?
            #if matInfo & 0x0400:  # makes props show through?
            #if matInfo & 0x0200:  # unknown
            matInfo = arc.readUByte()   # 0x26  # also color related like matAlpha?
            #if matInfo & 0x04:  # draw mesh with the stuff below?
            #if matInfo & 0x44:  # use original alpha
            #if matInfo & 0x80:  # full black texture?
            if matInfo == 0x64:  # 0x24 | 0x44 (0x64)  # override texture alpha
                #matAlpha = arc.readUByte()  # 0x27
                if matInfoAlpha & 0xFF != 0xD:
                    mat.setDefaultBlend(0)

        else:  # PSP(?), Xbox, Xbox 360?  to be split
            arc.seek(matOffset + 0x24)
            #matAlphaTest = arc.readUByte() / 100  # Xbox
            matBlend2 = arc.readUByte()

            if not 0x2 <= matType <= 0x6:
                mat.setDefaultBlend(0)
            #else:
            #    mat.setAlphaTest(matAlphaTest)
            #if matType == 0x2:
                #mat.setTexture(None)
                #mat.setEnvTexture(texName.get(texOffset))

        arc.seek(matOffset + 0x28)
        mat.setFlags(matFlags)
        matList.append(mat)

    # Static Models
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
            mdlOffset = arc.readUInt() + grpOffset
            boMdlParseTrack(arc, arcVer, arcSystem, mdlOffset, subCount, grp, mdlType, grpOffset)
            arc.seek(grpOffset + 0x8)

            if BoDebug:
                print("Model {} of {} ({})".format(grp + 1, mdlCount[mdl], mdlType))

    # Everything beyond this point has 0x70 bytes of nothing on PSP

    # Props & Instances
    # not a fan of relative seeks for readability, to be redone
    arc.seek(0x34)
    if arcSystem == BoPSP:
        arc.seek(0x70, 1)
    instCount = arc.readUShort()
    propCount = arc.readUShort()
    instOffset = arc.readUInt()
    propOffset = arc.readUInt()
    if arcVer >= 0x30:
        if propCount != 0:
            noesis.doException("Invalid State! Expected 0 for props at 0x36 for Static version {:02X}, got {}".format(arcVer, propCount))
        propCount = arc.readUInt()
    if arcSystem == BoXbox360:
        arc.seek(0x4, 1)  # unk
    arc.seek(0x4, 1)  # also unk
    propSpawns = arc.readUInt()
    # other pointers beyond this are null if PropInst.dat exists (B3/Legends)

    # probably just have to call with a specific index and scale/transform params
    #boMdlParsePropInst(arc, arcVer, arcSystem, instOffset, instCount, "inst")
    #boMdlParsePropInst(arc, arcVer, arcSystem, propOffset, propCount, "prop", 0)

    propFile = os.path.join(os.path.split(rapi.getInputName())[0], "PropInst.dat")
    if os.path.exists(propFile) and os.path.getsize(propFile):
        data = rapi.loadIntoByteArray(propFile)
        if boChkDatPropInst(data):
            prop = NoeBitStream(data)
            boGetVerEndian(prop)  # just to override endianness

            prop.seek(0x8)
            propIdxOffset = prop.readUInt()
            propMatOffset = prop.readUInt()

            #if prop.readUInt() != prop.readUInt():  # == prop.getSize()
            prop.seek(0x18)
            propIdxCount = prop.readUShort()
            prop.seek(0x1C)
            propMatCount = prop.readUShort()
            if propIdxCount != propSpawns or propMatCount != propSpawns:
                noesis.doException("Prop index and/or transformation matrix amount mismatch!")

            for idx in range(propSpawns):
                prop.seek(propIdxOffset + idx * 0x50 + 0x40)
                propNum = prop.readUShort()
                propIdx = prop.readUByte()

                prop.seek(propMatOffset + idx * 0x40)
                propName = "prop_{:03}_mdl".format(propNum)
                rapi.rpgSetTransform(NoeMat44.fromBytes(prop.readBytes(0x40)).toMat43())
                boMdlParsePropInst(arc, arcVer, arcSystem, propOffset, propCount, propName, propIdx)

            rapi.rpgSetTransform(None)

    # Streamed Units
    streamFile = os.path.join(os.path.split(rapi.getInputName())[0], "streamed.dat")
    if os.path.exists(streamFile) and os.path.getsize(streamFile):
        mdl = NoeBitStream(rapi.loadIntoByteArray(streamFile))
        boGetVerEndian(mdl)  # just to override endianness

        # PSP Dominator uses ver 0x30 for whatever reason, but has changes
        # introduced in PS2 ver 0x34. PS2 Dominator uses ver 0x3E at least
        if arcSystem != BoXbox360:
            arc.seek(0x54)
            if arcVer >= (0x30 if arcSystem == BoPSP else 0x34):
                arc.seek(0x4, 1)
            if arcSystem == BoPSP:
                arc.seek(0x70, 1)
        else:
            arc.seek(0x6C)

        unitCount = arc.readUShort()
        arc.seek(0x2, 1)
        unitOffset = arc.readUInt()

        arc.seek(unitOffset)
        for idx in range(unitCount):
            subOffset = arc.readUInt() + 0x10
            lodOffset = arc.readUInt() + 0x10
            subSize = arc.readUInt()
            lodSize = arc.readUInt()
            boMdlParseTrack(mdl, arcVer, arcSystem, subOffset, 1, idx)
            # material array is nonexistent and instead inherited from above
            #boMdlParseTrack(mdl, arcVer, arcSystem, lodOffset, 1, idx)

            if BoDebug:
                print("Unit {} of {}".format(idx + 1, unitCount))

    try:
        mdl = rapi.rpgConstructModel()
    except:
        mdl = NoeModel()
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
