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
#   All track collisions
#   All vehicle model support
#   Xbox streamed instance support
#   X360 streamed instance and prop support
#   Xbox/X360 track material parsing
#   Convert line geometry to fake quads
#   Redo loop returns consistently

# Written by Edness   v0.8d   2021-06-23 - 2023-12-25

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

    handleTmm = noesis.register("NFS Shift - TrackMaps [PSP]", ".tmm")
    noesis.setHandlerTypeCheck(handleTmm, nfsChkTmm)
    noesis.setHandlerLoadModel(handleTmm, nfsArcMdlTmm)

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


def boSuper(clObj):
    # Superclass base shortcut, noeSuper() "fix" for BoBitStream
    return super(clObj.__class__.__base__, clObj)

class BoBitStream(NoeBitStream):
    #def __init__(self, data=None, bigEndian=NOE_LITTLEENDIAN):
    #    noeSuper(self).__init__(data, bigEndian)

    def seek(self, addr, isRelative=NOESEEK_ABS):
        # Normally calling this would infinitely recurse on NoeBitStream instead of going to NoeUnpacker
        # read() and checkOverrun() also use noeSuper() which would break here but I don't use them (yet)
        #self.toUnpacker(); r = NoeUnpacker.seek(self, addr, isRelative); self.fromUnpacker(); return r
        self.toUnpacker(); r = boSuper(self).seek(addr, isRelative); self.fromUnpacker(); return r

    def tell(self):
        # Normally I use getOffset() but for debugging I like to use tell() instead
        self.toUnpacker(); r = boSuper(self).tell(); self.fromUnpacker(); return r

    def readPtr(self, relOffset=0x0):
        # For easier handling of relative null pointers
        dataOffset = noesis.bsReadInt(self.h)  # self.readInt()
        if dataOffset: dataOffset += relOffset
        return dataOffset

def boCalcAlign(padFrom, padTo):
    # Calculates alignment to a value
    return (padFrom // padTo + 1) * padTo

def boDecGtID(cGtID):
    # Decompresses GtID strings
    char = " -/0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_"
    decStr = str()
    for chr in range(12):
        decStr += char[cGtID % len(char)]
        cGtID //= len(char)
    return decStr[::-1].rstrip()

def boDecZlib(data):
    # Not using Noesis' rapi.decompInflate() because it doesn't support partial decompression
    return zlib.decompressobj().decompress(data)

def boGetVerEndian(noe):
    # Expects to be a byte form int that's < 256 for version checks
    data = noe.readBytes(0x4)
    if data.endswith(bytes(0x3)):
        return int.from_bytes(data, "little"), NOE_LITTLEENDIAN
    if data.startswith(bytes(0x3)):
        noe.setEndian(NOE_BIGENDIAN)
        return int.from_bytes(data, "big"), NOE_BIGENDIAN
    return None, None

def boGetTexAptIndex(arc, aptDataOffset, texIndex):
    # Finds the given texture index in Apt Data
    arc.seek(aptDataOffset)
    while arc.readUInt() != texIndex:
        continue
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

# Global exception messages
BoExcFmt = "Unsupported format! "
BoExcVif = "Unhandled VIF unpack: "

# Generic material name
BoMatName = "material_{:03}"

# PSP hardcoded vertex tags
BoPSPVtagDef = 0x12000102  # pos uv
BoPSPVtagClr = 0x12000116  # pos uv clr
BoPSPVtagNrm = 0x12000122  # pos uv nrm

# Global max streamed units to render at once:
# Current unit + 8 before + 8 ahead = 17 units
BoMaxUnits = 17

# Xbox and Xbox 360 mesh format IDs
BoXboxTris = {
    0x2: noesis.RPGEO_TRIANGLE,  # Line w/ workaround
    0x6: noesis.RPGEO_TRIANGLE_STRIP
}




#   #####   ##   ##  #######   #####   ##  ##   ######  
#  ##   ##  ##   ##  ##       ##   ##  ## ##   ##       
#  ##       #######  #####    ##       ####     #####   
#  ##   ##  ##   ##  ##       ##   ##  ## ##        ##  
#   #####   ##   ##  #######   #####   ##  ##  ######   


def boChkTxd(data):
    chk = BoBitStream(data)
    if chk.readBytes(0x8) in {G_TEXDIC, G_TEXDIC[::-1]}:
        return True
    return False

def boChkBxv(data):
    chk = BoBitStream(boDecZlib(data[:256]) if data.startswith(b"\x78\xDA") else data)
    chkVer, chkEndian = boGetVerEndian(chk)
    if chkEndian is not None:
        chkSize = chk.readUInt()
        if 0x14 <= chkVer <= 0x25 and chkSize in {0x0, chk.getSize()}:
            return True
    return False

def boChkDatStatic(data):
    chk = BoBitStream(boDecZlib(data[:256]) if data.startswith(b"\x78\xDA") else data)
    chkVer, chkEndian = boGetVerEndian(chk)
    if chkEndian is not None:
        chkSize = chk.readUInt()
        if 0x21 <= chkVer <= 0x3E and chkSize in {0x0, chk.getSize()}:
            return True
    return False

def boChkDatPropInst(data):
    chk = BoBitStream(data)
    chkVer, chkEndian = boGetVerEndian(chk)
    if chkEndian is not None:
        chkSize = chk.readUInt()
        if 0x2 <= chkVer <= 0x3 and chkSize == chk.getSize():
            return True
    return False

def boChkDatEnviro(data):
    chk = BoBitStream(data)
    chkSize = chk.getSize()

    # Minimum size check to not break Burnout Paradise .dats by seeking out of bounds
    if chkSize > 0x300:
        # Header values to check in Little Endian
        chkED02 = b"\x02\x00\x44\x45"
        chkED03 = b"\x03\x00\x44\x45"
        chkED04 = b"\x04\x00\x44\x45"

        chk.seek(0xA8)
        if chk.readBytes(0x4) == chkED02 and chk.readUInt() in {0x0, chkSize}:  # PS2 & Xbox
            return True
        chk.seek(0xB8)
        if chk.readBytes(0x4) == chkED03[::-1] and chk.readUInt() == 0x0:  # Xbox 360
            return True
        chk.seek(0x1C8)
        if chk.readBytes(0x4) == chkED03 and chk.readUInt() == chkSize:  # PSP (Legends)
            return True
        chk.seek(0x1D8)
        if chk.readBytes(0x4) == chkED04 and chk.readUInt() == chkSize:  # PSP (Dominator)
            return True
        chk.seek(0x2D4)
        if chk.readBytes(0x4) == chkED04 and chk.readUInt() == chkSize:  # PSP (NFS: Shift)
            return True
    return False

def boChkBinFE(data):
    chk = BoBitStream(data)
    if chk.readBytes(8) in {G_MOVIEARRAY, G_MOVIEARRAY[::-1]}:
        return True
    return False

def boChkBinFont(data):
    chk = BoBitStream(data)
    chkSize = chk.getSize()

    fontMagic = chk.readBytes(0x4)
    if fontMagic in {b"v1.4", b"4.1v"}:
        return True  # Revenge, Black
    elif chkSize > 0x2000:
        chk.seek(0x70)
        texOffset = chk.readPtr()
        if texOffset < (chkSize // 2):
            chk.seek(texOffset)
            if chk.readBytes(0x8) == bytes(0x4) + b"\x50\x02\x00\x00":
                return True  # Dominator (PS2)
    return False

def boChkBinLoad(data):
    chk = BoBitStream(data)
    txdCount = chk.readUInt64()
    chkAlign = boCalcAlign(txdCount * 0x10 + 0x8, 0x800)
    if chkAlign < chk.getSize():
        chk.seek(chkAlign)
        if chk.readBytes(8) == G_TEXDIC:
            return True
    return False

def boChkArena(data):
    chk = BoBitStream(data)
    if chk.readBytes(0x10) == b"Neko\x01" + bytes(0xB):
        return True
    return False

def nfsChkTmm(data):
    chk = BoBitStream(data)
    if chk.getSize() > 0x50:
        for hdr in range(3):
            chk.seek(0xC + hdr * 0x10)
            if chk.readBytes(0x4) != bytes(0x4):
                return False
        return True
    return False

def blkChkDb(data):
    chk = BoBitStream(data)

    chkSize = chk.getSize()
    chkVer = chk.readUInt()
    if chkVer != 0x4:
        chk.seek(0x18)
        chkVer = chk.readUInt()
    if chkVer in {0x4, 0x9}:
        dctOrder = (
            G_MODELS,
            G_CHARACTERDIC,
            G_ACTORDICTION,
            G_BNKS,
            G_SHAREDBNKS,
            G_RCBS
        )
        txdOffset = chk.readPtr()
        curChkOffset = chk.getOffset()
        if txdOffset < chkSize:
            chk.seek(txdOffset)
            if chk.readBytes(0x8) not in {G_TEXDIC, G_TEXTURE}:
                return False
        for gtid in dctOrder:
            chk.seek(curChkOffset)
            dctOffset = chk.readPtr()
            curChkOffset = chk.getOffset()
            if dctOffset > chkSize:
                return False
            chk.seek(dctOffset)
            if chk.readBytes(0x8) != gtid:
                return False
        return True
    return False

def blkChkBinGlob(data):
    chk = BoBitStream(data)

    chkSize = chk.getSize()
    chkVer = chk.readUInt()
    if chkVer in {0x8, 0x9}:
        txdOffset = chk.readPtr()
        dctOffset = chk.readPtr()
        if txdOffset > chkSize or dctOffset > chkSize:
            return False
        chk.seek(txdOffset)
        if chk.readBytes(0x8) != G_TEXDIC:
            return False
        chk.seek(dctOffset)
        if chk.readBytes(0x8) != G_MYDICTIONARY:
            return False
        return True
    return False

def blkChkBinGuns(data):
    chk = BoBitStream(data)

    chkSize = chk.getSize()
    txdOffset = chk.readPtr()
    mdlOffset = chk.readPtr()
    if txdOffset > chkSize or mdlOffset > chkSize:
        return False
    chk.seek(txdOffset)
    if chk.readBytes(0x8) == G_TEXTURE:
        chk.seek(mdlOffset)
        if chk.readBytes(0x8) == G_MODELS:
            return True
    return False

def blkChkBinLevel(data):
    chk = BoBitStream(data)

    if chk.getSize() > 0x500:
        chkVer = chk.readUInt()
        if chkVer == 0xA:
            chk.seek(0x2BC)  # -> 0x300
        elif chkVer == 0x11:
            chk.seek(0x390) # -> 0x400
        else:  # chkVer 0x1 has no textures
            return False
        txdOffset = chk.readPtr()
        chk.seek(txdOffset)
        if chk.readBytes(8) == G_TEXDIC:
            return True
    return False

def blkChkBinStLevel(data):
    chk = BoBitStream(data)

    chkVer = chk.readUInt()
    txdOffset = chk.readPtr()
    if chkVer in {0x9, 0xA}:
        chk.seek(0xC)
        hdrOffset = chk.readPtr()
        if hdrOffset < chk.getSize() - 0x8:
            chk.seek(hdrOffset + txdOffset)
            if chk.readBytes(0x8) == G_TEXTURE:
                return True
    return False

def blkChkBinStUnit(data):
    chk = BoBitStream(data)

    chkSize = chk.getSize()
    if chk.readUInt() == 0x3:
        chk.seek(0x8)
        hdrOffset = chk.readPtr()
        chk.seek(hdrOffset + 0x18)
        if chk.readUInt() == 0x9:
            dctOrder = (
                G_TEXTURE,
                G_MODELS,
                G_CHARACTERDIC,
                G_ACTORDICTION,
                G_BNKS,
                G_SHAREDBNKS,
                G_RCBS
            )
            for gtid in dctOrder:
                dctOffset = chk.readPtr(hdrOffset)
                curChkOffset = chk.getOffset()
                if dctOffset > chkSize:
                    return False
                chk.seek(dctOffset)
                if chk.readBytes(0x8) != gtid:
                    return False
                chk.seek(curChkOffset)
            return True
    return False

def blkChkBinUnit(data):
    chk = BoBitStream(data)

    chkVer = chk.readUInt()
    if chkVer == 0xC:
        chk.seek(0x18)
    elif 0x16 <= chkVer <= 0x18:
        chk.seek(0x24)
    else:
        return False
    txdOffset = chk.readPtr()
    chk.seek(txdOffset)
    if chk.readBytes(0x8) == G_TEXTUREDICTI:
    # surrounded by G_MYDICTIONARY and G_ANIMDICTIONA
        return True
    return False




#  ##   ##   #####   ######   #######  ##        ######  
#  ### ###  ##   ##  ##   ##  ##       ##       ##       
#  ## # ##  ##   ##  ##   ##  #####    ##        #####   
#  ##   ##  ##   ##  ##   ##  ##       ##            ##  
#  ##   ##   #####   ######   #######  #######  ######   


def boMdlTrackGetMatIdx(mdl, mdlVer, mdlOffset, grpOffset, subCount, mdlSystem):
    # Last known version to calculate the static pointer from the group offset is 0x30
    # Earliest known version to calculate it from the model offset is 0x32
    matIdxOffset = mdl.readPtr(grpOffset if mdlVer <= 0x30 else mdlOffset - 0x40)

    if matIdxOffset:  # Static
        mdl.seek(matIdxOffset)
        matIdx = [mdl.readUShort() for mat in range(subCount)]

    else:             # Streamed
        # while PSP has this data, they go unused in favor
        # of material indices stored in the submesh header
        if mdlSystem == BoPSP:
            return list(), int()

        pvsOffset = mdlOffset + {
            BoPS2: 0x10,
            #BoPSP: (0x10, 0x60),
            BoXbox: 0x20,
            BoXbox360: 0x30
        }.get(mdlSystem)

        mdl.seek(pvsOffset)
        matCount = mdl.readUByte()
        if mdlVer <= 0x32:
            matCount = mdl.readUByte()

        matIdxOffset = pvsOffset + 0x14
        mdl.seek(matIdxOffset)
        matIdx = [mdl.readUShort() for mat in range(matCount)]

        if mdlVer < 0x34 or mdlSystem == BoXbox:
            # Old version, each unit chunk contains submesh indices applied to the material array
            if mdlVer <= 0x27:
                unitRenders = pvsOffset + 0xBA
            elif mdlVer <= 0x32:
                unitRenders = pvsOffset + 0xC3
            else:
                unitRenders = pvsOffset + 0xD0
                # Retail Xbox Revenge version 0x34 is assumed to be 0x33 that was
                # bumped up but never adjusted along with the fully reworked 0x34+

            #  pvsOffset + 0xBC  and  0xAB * chnk  for PSP Dom which uses some weird hybrid of old/new?
            for chnk in range(BoMaxUnits):
                mdl.seek(unitRenders + 0xA9 * chnk)
                unitIdx = mdl.readByte()
                if unitIdx == 0:  # current
                    break
            else:
                noesis.doException("Failed to find rendering info for the current unit!")
            unitRender = mdl.readUShort()
            mdlIdx = list(mdl.readBytes(matCount))

        else:
            # New version, each chunk is a material index that contains submesh indices
            if mdlSystem == BoXbox360:
                # Xbox 360 stores 120 materials per unit, as opposed to 83 for oldgen
                unitRenders = pvsOffset + 0x10D
                unitRenderStart = pvsOffset + 0x130
            else:
                unitRenders = pvsOffset + 0xC3
                unitRenderStart = pvsOffset + 0xF0

            mdl.seek(unitRenders)
            unitRender = mdl.readBytes(BoMaxUnits)
            unitIdx = list(mdl.readBytes(BoMaxUnits)).index(0)  # current

            mdl.seek(unitRenderStart)
            mdlIdx = list(mdl.readBytes(matCount * 0x30)[unitIdx::0x30])

        matIdx = [matIdx[mdlIdx.index(mat)] for mat in range(subCount)]

    return matIdx, matIdxOffset  # matIdxOffset is just for BoDebug

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
            #if 131 < clrTest < 255:  # 131 because PSP RGBA5551
            #    noesis.messagePrompt("VtxClr mul {}\nContact Edness!".format(clrTest))
            for byte in clrChannel:
                byte *= 2
                if byte > 255:
                    byte = 255
                clrMultiply.append(byte)
            clrData[clrOffset + clr::clrStride] = bytes(clrMultiply)

def boMdlPS2(mdl, vifStart, vifFull, primLine=False):
    def boPS2Read12(rData):
        rSize = len(rData) // 2  # 0xFFFF / (0x10000 / (1 << 12)) = 4095.9375?
        rData = [int / 4096 for int in noeUnpack("<{}h".format(rSize), rData)]
        return noePack("<{}f".format(rSize), *rData)

    def boPS2Unpack(vifOffset):
        mdl.seek(vifOffset)
        vifSize = 0xC + mdl.readUShort() * 0x10
        if mdl.readUShort() != 0x6000:
            noesis.doException("Unexpected VIF identifier!")
        vifUnpack.extend(rapi.unpackPS2VIF(mdl.readBytes(vifSize)))
        return vifSize

    def boPS2UnpackFmt():
        return "V{}-{}".format(vu.numElems, vu.elemBits).replace("V1", "S")

    rapi.rpgClearBufferBinds()

    vifUnpack = list()
    vifStartSize = boPS2Unpack(vifStart)

    # Many submeshes have both V3-8 and V4-8 data, V3-8 seems to take precedence for
    # vertex colors. If V3-8 (RGB24) data doesn't exist then V4-8 is used as RGBA32.
    # Otherwise V4-8 is used for some reflection stuff which is usually placed after
    # V3-8, except for some cases where it's placed before V3-8 data. (if no V2-16?)
    # And for vehicles V3-8 seems to be used for normals and V4-16 is split in half,
    # left half being used for UVs, and right half being used for reflection stuff?
    # ...Except for wheel models where the elem count is halved and all of it is UV.
    clr24 = True
    clr32 = True
    vuOrder = list()
    for vu in vifUnpack:
        if vu.numElems == 3 and vu.elemBits == 8:
            clr32 = False
        elif vu.numElems == 4 and vu.elemBits == 16:
            clr24 = False
        # if V4-16 exists, V3-8 is used as normals
        vuOrder.append(boPS2UnpackFmt())

    if vifFull:
        vifFullSize = boPS2Unpack(vifFull)

    if BoDebug:
        print("VIF data start offset: 0x{:X}".format(vifStart)
            + "\nVIF data start size: 0x{:X}".format(vifStartSize + 0x4)
            + (("\nVIF data full offset: 0x{:X}".format(vifFull)
            + "\nVIF data full size: 0x{:X}".format(vifFullSize + 0x4)) if vifFull else "")
            + "\nVIF unpack amount: {}".format(len(vifUnpack))
            + "\nVIF unpack order: {}".format(", ".join(vuOrder)))

    vtxData = list()
    clrData = list()
    nrmData = list()
    uvData = list()
    for vu in vifUnpack:
        if vu.elemBits == 32 and vu.numElems == 4:    # Vertices, Normals (Tracks)
            for idx in range(0xC, len(vu.data), 0x10):
                if vu.data[idx:idx + 0x4] not in (b"\x00\x00\x00\x00", b"\x00\x80\x00\x00"):
                    break
            else:
                vtxData.append(vu.data)
                continue
            for idx in range(0x30, len(vu.data), 0x40):
                if vu.data[idx:idx + 0x10] != bytes(0x10):
                    break
            else:
                # Normals are interleaved as XXXXYYYYZZZZWWWW
                nrmSplit = list()
                for idx in range(0x0, len(vu.data), 0x40):
                    for nrm in range(0x0, 0x10, 0x4):
                        nrmSplit.extend(vu.data[idx + nrm + 0x00:][:0x4])
                        nrmSplit.extend(vu.data[idx + nrm + 0x10:][:0x4])
                        nrmSplit.extend(vu.data[idx + nrm + 0x20:][:0x4])
                nrmSplit = bytes(nrmSplit)
                nrmData.append(nrmSplit)
                continue
            noesis.doException(BoExcVif + boPS2UnpackFmt())

        elif vu.elemBits == 32 and vu.numElems == 2:  # UVs (PropInst)
            uvData.append(vu.data)

        elif vu.elemBits == 16 and vu.numElems == 2:  # UVs (Tracks)
            uvData.append(boPS2Read12(vu.data))

        elif vu.elemBits == 16 and vu.numElems == 4:  # UVs (Vehicles), Envmap?
            # UVs are interleaved as UUVV, and with other
            # data interleaved as AAAABBBB for body parts
            if len(vtxData[-1]) // 16 - len(vu.data) // 8 <= 0:
                uvStep = 0x10  # body
            elif len(vtxData[-1]) // 32 - len(vu.data) // 8 <= 0:
                uvStep = 0x8   # wheels
            else:
                noesis.doException(BoExcVif + boPS2UnpackFmt())

            uvSplit = list()
            #unkSplit = list()  # Envmap?
            for idx in range(0x0, len(vu.data), uvStep * 2):
                uvSplit.extend(vu.data[idx + 0x0:][:0x4])
                uvSplit.extend(vu.data[idx + uvStep + 0x0:][:0x4])
                uvSplit.extend(vu.data[idx + 0x4:][:0x4])
                uvSplit.extend(vu.data[idx + uvStep + 0x4:][:0x4])
                #if uvStep == 0x10:
                #    unkSplit.extend(vu.data[idx +  0x8:][:0x8])
                #    unkSplit.extend(vu.data[idx + 0x18:][:0x8])
            uvData.append(boPS2Read12(bytes(uvSplit)))

        elif vu.elemBits == 8 and vu.numElems == 3:   # Colors (RGB24), Normals (Vehicles)
            if clr24:
                # Vertex colors need to be changed from RGB to RGBA
                clrData.append(rapi.imageDecodeRaw(vu.data, len(vu.data) // 3, 1, "R8G8B8"))
            #else:
                #nrmTemp = [int / 127 for int in noeUnpack("<{}b".format(len(vu.data)), vu.data)]
                #nrmData.append(noePack("<{}f".format(len(nrmTemp)), *nrmTemp))
                #nrmData.append(vu.data)  # unknown stride?

        elif vu.elemBits == 8 and vu.numElems == 4:   # Colors (RGBA32), Envmap?
            if clr32:
                clrData.append(vu.data)
            # if RGB24 exists, then these are used for some reflection stuff(?)
            # datasize seems to always be 3 more than vertex data, and never has uvs?

        else:
            noesis.doException(BoExcVif + boPS2UnpackFmt())

    for idx in range(len(vtxData)):  # not using enumerate() just because
        vtxCount = len(vtxData[idx]) // 0x10

        faceData = list()
        if not primLine:
            for vtx in range(vtxCount - 2):
                if vtxData[idx][vtx * 0x10:][:0x30].endswith(bytes(0x4)):
                    faceData.extend((vtx, vtx + 2, vtx + 1) if vtx % 2 else (vtx, vtx + 1, vtx + 2))
        else:
            for vtx in range(0, vtxCount, 2):
                faceData.extend((vtx, vtx + 1, vtx))
        faceData = bytes(faceData)

        rapi.rpgBindPositionBuffer(vtxData[idx], noesis.RPGEODATA_FLOAT, 0x10)
        if clrData:
            boMdlVtxClrPreview(clrData[idx], 0x0, 0x4)
            rapi.rpgBindColorBuffer(clrData[idx], noesis.RPGEODATA_UBYTE, 0x4, 4)
        if nrmData:
            rapi.rpgBindNormalBuffer(nrmData[idx], noesis.RPGEODATA_FLOAT, 0xC)
            #rapi.rpgBindNormalBuffer(nrmData[idx], noesis.RPGEODATA_BYTE, 0x3)
        if uvData:
            rapi.rpgBindUV1Buffer(uvData[idx], noesis.RPGEODATA_FLOAT, 0x8)
        rapi.rpgCommitTriangles(faceData, noesis.RPGEODATA_UBYTE, len(faceData), noesis.RPGEO_TRIANGLE)

def boMdlPS2Track(mdl, mdlVer, mdlOffset, mdlBaseName, grpOffset, matList):
    mdl.seek(mdlOffset)
    subCount = mdl.readUInt()
    subOffset = mdl.readPtr(mdlOffset)
    matIdx, matIdxOffset = boMdlTrackGetMatIdx(mdl, mdlVer, mdlOffset, grpOffset, subCount, BoPS2)

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

        mdl.seek(subOffset + 0xC)
        vifStart = mdl.readPtr(subOffset)
        mdl.seek(subOffset + 0x1C)
        vifFull = mdl.readPtr(subOffset)

        boMdlPS2(mdl, vifStart, vifFull, eval(matList[matIdx[blk]].userData))

        if BoDebug:
            print("Submesh {} of {}".format(blk + 1, subCount))
        subOffset += 0x40

def boMdlPS2PropInst(mdl, mdlVer, mdlOffset, mdlBaseName):
    if mdlBaseName.startswith("prop") and mdlVer >= 0x30:
        # Revenge/Dominator props
        mdl.seek(mdlOffset + 0x44)
        matIdx = [mdl.readUShort() for mat in range(3)]

        for idx in range(3 if BoDmg else 1):
            mdl.seek(mdlOffset + 0x30 + 0x4 * idx)
            subOffset = mdl.readPtr(mdlOffset)
            if subOffset > mdl.getSize():
                continue

            for lod in range(2 if BoLOD else 1):
                subOffset += 0x8 * lod

                rapi.rpgSetName(mdlBaseName + "dmg_{:03}_lod_{:03}".format(idx, lod))
                rapi.rpgSetMaterial(BoMatName.format(matIdx[idx]))

                mdl.seek(subOffset)
                vifStart = mdl.readPtr(subOffset)
                vifFull = mdl.readPtr(subOffset)
                boMdlPS2(mdl, vifStart, vifFull)

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

            mdl.seek(subOffset)
            vifStart = mdl.readPtr(subOffset)
            vifFull = mdl.readPtr(subOffset)
            boMdlPS2(mdl, vifStart, vifFull)

def boMdlPSP(mdl, mdlOffset, hdrSkip, geOffset, vtxTag, clrFix=True):
    def boPSPReadIdx():
        geInstr = mdl.readUInt()
        geFmt = geInstr >> 16 & 0xFF
        geCmd = geInstr >> 24
        if geCmd == 0x0B:
            return -1
        if geCmd != 0x04:
            noesis.doException("Unexpected GE command {:02X}".format(geCmd))
        if geFmt != vtxType:
            noesis.doException("Vertex type mismatch! Expected {:02X}, got {:02X}".format(vtxType, geFmt))
        return geInstr & 0xFFFF

    mdl.seek(hdrSkip + mdlOffset)
    vtxType = mdl.readUInt()
    vtxCount = mdl.readUInt()
    vtxOffset = mdl.readPtr(mdlOffset)

    mdl.seek(hdrSkip + mdlOffset + 0x10)
    mdlBias = NoeVec3.fromBytes(mdl.readBytes(0xC))
    mdl.seek(hdrSkip + mdlOffset + 0x20)
    mdlScale = NoeVec3.fromBytes(mdl.readBytes(0xC))
    rapi.rpgSetPosScaleBias(mdlScale, mdlBias)

    mdl.seek(hdrSkip + mdlOffset + geOffset)
    cmdOffset = mdl.readPtr(mdlOffset)
    cmdCount = mdl.readUInt()

    if BoDebug:
        print("Model offset: 0x{:X}".format(hdrSkip + mdlOffset)
            + "\nVertex data offset: 0x{:X}".format(vtxOffset)
            + "\nVertex data amount: {}".format(vtxCount)
            + "\nVertex data format: {}".format(vtxType)
            + "\nVertex data tag: 0x{:X}".format(vtxTag)
            + "\nGE data offset: 0x{:X}".format(cmdOffset)
            + "\nGE data amount: {}".format(cmdCount))

    if vtxCount == 0:
        return

    mdl.seek(vtxOffset)
    vtxFmt = rapi.decodePSPVert(vtxTag)
    vtxData = mdl.readBytes(vtxCount * vtxFmt.vertexSize)
    rapi.rpgSetUVScaleBias(NoeVec3((32, 32, 0)), NoeVec3((-7, -7, 0)))
    vtxFmt.bindBuffers(vtxData)

    # 16-bit vertex colors don't get auto-bound
    if 4 <= vtxFmt.colorType <= 6:
        clrData = list()
        for clr in range(vtxFmt.colorOfs, len(vtxData), vtxFmt.vertexSize):
            clrData.extend(vtxData[clr:clr + 0x2])
        clrData = rapi.imageDecodeRaw(bytes(clrData), vtxCount, 1, {
            4: "R5G6B5",
            5: "R5G5B5A1",
            6: "R4G4B4A4"
        }.get(vtxFmt.colorType))
        if clrFix:  # Legends' vertex colors use the full range
            boMdlVtxClrPreview(clrData, 0x0, 0x4)
        rapi.rpgBindColorBuffer(clrData, noesis.RPGEODATA_UBYTE, 0x4, 4)

    mdl.seek(cmdOffset)
    if vtxType == 0x1:    # Lines
        faceData = list()
        if cmdCount - 1 != 1:  # 1 command + RET
            noesis.doException("GE Wire mesh with more than 1 command")
        faceData.extend(range(boPSPReadIdx()))
        for idx in range(len(faceData) - 1, 0, -2):
            faceData.insert(idx, faceData[idx])
        faceType = noesis.RPGEO_TRIANGLE

    elif vtxType == 0x4:  # Tri-Strips
        faceData = [-1, -1]
        for face in range(cmdCount):  # in theory always cmdCount - 1 but just in case
            faceStart = faceData[-2] + 1
            faceEnd = faceStart + boPSPReadIdx()
            if faceEnd < faceStart:  # RET (-1)
                break
            faceData.extend(range(faceStart, faceEnd))
            faceData.append(-1)
        faceData = faceData[2:]
        faceType = noesis.RPGEO_TRIANGLE_STRIP

    else:
        noesis.doException("Unhandled GE vertex type {}".format(vtxType))

    faceCount = len(faceData)
    faceData = noePack("<{}h".format(faceCount), *faceData)
    rapi.rpgCommitTriangles(faceData, noesis.RPGEODATA_USHORT, faceCount, faceType)

    rapi.rpgSetPosScaleBias(None, None)
    rapi.rpgSetUVScaleBias(None, None)

def boMdlPSPTrack(mdl, mdlVer, mdlOffset, mdlBaseName, grpOffset):
    mdl.seek(mdlOffset)
    subOffset = mdl.readPtr(mdlOffset)
    subCount = mdl.readUInt()
    matIdx, matIdxOffset = boMdlTrackGetMatIdx(mdl, mdlVer, mdlOffset, grpOffset, subCount, BoPSP)

    if BoDebug:
        print("\nPlayStation Portable track model detected!"
            + ("\nModel group offset: 0x{:X}".format(grpOffset) if grpOffset is not None else "")
            + "\nModel info offset: 0x{:X}".format(mdlOffset)  # - 0x40
            + "\nSubmesh info offset: 0x{:X}".format(subOffset)
            + "\nSubmesh amount: {}".format(subCount)
            + ("\nMaterial index offset: 0x{:X}".format(matIdxOffset) if matIdxOffset != mdlOffset else ""))

    for sub in range(subCount):
        mdlOffset = subOffset + 0xA0 * sub

        mdlName = mdlBaseName + "{:03}".format(sub)
        rapi.rpgSetName(mdlName)

        if matIdxOffset:
            rapi.rpgSetMaterial(BoMatName.format(matIdx[sub]))
        else:
            mdl.seek(mdlOffset + 0x88)
            rapi.rpgSetMaterial(BoMatName.format(mdl.readUShort()))

        if BoDebug:
            print("\nSubmesh data offset: 0x{:X}".format(mdlOffset))

        boMdlPSP(mdl, mdlOffset, 0x40, 0x4C, BoPSPVtagClr, clrFix=True if mdlVer > 0x27 else False)

        if BoDebug:
            print("Submesh {} of {}".format(sub + 1, subCount))

def boMdlPSPPropInst(mdl, mdlVer, mdlOffset, mdlBaseName):
    if mdlBaseName.startswith("prop") and mdlVer >= 0x30:
        # Dominator props
        mdl.seek(mdlOffset + 0x20)  # has up to 4 lod/dmg meshes, but all are empty?
        subOffset = mdl.readPtr(mdlOffset)
        if subOffset > mdl.getSize():
            return
        mdl.seek(mdlOffset + 0x34)
        matIdx = mdl.readUShort()

        #rapi.rpgSetName(mdlBaseName + "dmg_{:03}_lod_{:03}".format(idx, lod))
        rapi.rpgSetName(mdlBaseName + "dmg_000")
        rapi.rpgSetMaterial(BoMatName.format(matIdx))
        boMdlPSP(mdl, subOffset, 0x0, 0x44, BoPSPVtagDef)

    else:
        # All instances and Legends props
        mdl.seek(mdlOffset + 0x110)
        matIdx = [mdl.readUShort() for mat in range(3)]

        callExtra = (BoPSPVtagDef, True) if mdlVer > 0x27 else (BoPSPVtagClr, False)

        for lod in range(3 if BoLOD else 1):
            subOffset = mdlOffset + 0x50 * lod + 0x20

            mdlName = mdlBaseName + "lod_{:03}".format(lod)
            rapi.rpgSetName(mdlName)
            rapi.rpgSetMaterial(BoMatName.format(matIdx[lod]))

            boMdlPSP(mdl, subOffset, 0x0, 0x44, *callExtra)

def boMdlXboxReadLine(mdl, faceCount):
    # Converts Xbox/Xbox 360 line meshtype to fake triangles
    faceData = list()
    for idx in range(faceCount):
        faceData.extend(mdl.readBytes(0x2) + mdl.readBytes(0x2) * 2)
    return bytearray(faceData)

def boMdlXboxTrack(mdl, mdlVer, mdlOffset, mdlBaseName, grpOffset):
    mdl.seek(mdlOffset)
    if mdl.readUInt() != 0x1:
        noesis.doException("Invalid block header!")
    vtxOffset = mdl.readPtr(mdlOffset)
    mdl.seek(mdlOffset + 0xC)
    subOffset = mdl.readPtr(mdlOffset)
    subCount = mdl.readUInt()
    matIdx, matIdxOffset = boMdlTrackGetMatIdx(mdl, mdlVer, mdlOffset, grpOffset, subCount, BoXbox)

    if BoDebug:
        print("\nXbox track model detected!"
            + ("\nModel group offset: 0x{:X}".format(grpOffset) if grpOffset is not None else "")
            + "\nModel info offset: 0x{:X}".format(mdlOffset)  # - 0x40
            + "\nSubmesh info offset: 0x{:X}".format(subOffset)
            + "\nSubmesh amount: {}".format(subCount)
            + "\nMaterial index offset: 0x{:X}".format(matIdxOffset)
            + "\nVertex data offset: 0x{:X}".format(vtxOffset))

    subData = list()
    mdl.seek(subOffset)
    for blk in range(subCount):
        subOffset = mdl.getOffset()
        mdl.seek(0x80, 1)
        # triFmt, faceCount, faceOffset
        subData.append([mdl.readUInt(), mdl.readUInt(), mdl.readPtr(subOffset)])
        mdl.seek(0x4, 1)

    mdl.seek(vtxOffset)
    vtxData = bytearray(mdl.readBytes(subData[0][2] - vtxOffset))  # I swear it was bytearray by default before...
    for clr in range(0x10, len(vtxData), 0x1C):
        # Vertex colors need to be flipped from BGRA to RGBA
        vtxData[clr:clr + 3] = vtxData[clr:clr + 3][::-1]
    boMdlVtxClrPreview(vtxData, 0x10, 0x1C)

    rapi.rpgBindPositionBuffer(vtxData, noesis.RPGEODATA_FLOAT, 0x1C)
    rapi.rpgBindUV1BufferOfs(vtxData, noesis.RPGEODATA_FLOAT, 0x1C, 0x14)
    rapi.rpgBindColorBufferOfs(vtxData, noesis.RPGEODATA_UBYTE, 0x1C, 0x10, 4)

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
    def boXboxReadMdl():
        rapi.rpgClearBufferBinds()
        #mdl.seek(subOffset)
        #if mdl.readUInt() != 0x1:
        #    noesis.doException("Invalid block header!")
        mdl.seek(subOffset + 0x4)
        vtxOffset = mdl.readPtr(subOffset)
        mdl.seek(subOffset + 0xC)
        faceCount = mdl.readUInt()
        faceOffset = mdl.readPtr(subOffset)

        if not faceCount:
            return

        mdl.seek(vtxOffset)
        vtxData = mdl.readBytes(faceOffset - vtxOffset)

        mdl.seek(faceOffset)
        faceData = mdl.readBytes(faceCount * 2)

        if len(vtxData) % 0x14 == 0:
            rapi.rpgBindPositionBuffer(vtxData, noesis.RPGEODATA_FLOAT, 0x14)
            rapi.rpgBindUV1BufferOfs(vtxData, noesis.RPGEODATA_FLOAT, 0x14, 0xC)

        elif len(vtxData) % 0x18 == 0:
            rapi.rpgBindPositionBuffer(vtxData, noesis.RPGEODATA_FLOAT, 0x18)
            rapi.rpgBindUV1BufferOfs(vtxData, noesis.RPGEODATA_FLOAT, 0x18, 0x10)
            #rapi.rpgBindColorBufferOfs(vtxData, noesis.RPGEODATA_UBYTE, 0x18, 0xC, 4)

        rapi.rpgCommitTriangles(faceData, noesis.RPGEODATA_USHORT, faceCount, noesis.RPGEO_TRIANGLE_STRIP)

    if mdlBaseName.startswith("prop") and mdlVer >= 0x30:
        # Revenge props
        mdl.seek(mdlOffset + 0x44)
        matIdx = [mdl.readUShort() for mat in range(3)]

        for idx in range(3 if BoDmg else 1):
            rapi.rpgSetName(mdlBaseName + "dmg_{:03}".format(idx))
            rapi.rpgSetMaterial(BoMatName.format(matIdx[idx]))

            mdl.seek(mdlOffset + 0x30 + idx * 0x4)
            subOffset = mdl.readPtr(mdlOffset)
            if subOffset and subOffset < mdl.getSize():
                boXboxReadMdl()

    else:
        # All instances and B3 props
        pass

def boMdlXbox360Track(mdl, mdlVer, mdlOffset, mdlBaseName, grpOffset):
    mdl.seek(mdlOffset + 0x10)
    vtxSize = mdl.readUInt() - 0x2  # For some reason it's always off by 2?
    vtxOffset = mdl.readPtr(mdlOffset)
    vtxCount = mdl.readUShort()
    mdl.seek(mdlOffset + 0x1C)
    subOffset = mdl.readPtr(mdlOffset)
    subCount = mdl.readUShort()
    mdl.seek(mdlOffset + 0x24)
    matIdx, matIdxOffset = boMdlTrackGetMatIdx(mdl, mdlVer, mdlOffset, grpOffset, subCount, BoXbox360)

    if BoDebug:
        print("\nXbox 360 track model detected!"
            + ("\nModel group offset: 0x{:X}".format(grpOffset) if grpOffset is not None else "")
            + "\nModel info offset: 0x{:X}".format(mdlOffset)  # - 0x40
            + "\nSubmesh info offset: 0x{:X}".format(subOffset)
            + "\nSubmesh amount: {}".format(subCount)
            + "\nMaterial index offset: 0x{:X}".format(matIdxOffset)
            + "\nVertex data offset: 0x{:X}".format(vtxOffset)
            + "\nVertex data size: 0x{:X}".format(vtxSize)
            + "\nVertex amount: {}".format(vtxCount))

    subData = list()
    mdl.seek(subOffset)
    for blk in range(subCount):
        subOffset = mdl.getOffset()
        mdl.seek(0x90, 1)
        # faceSize, faceOffset, faceCount (broken?), triFmt
        subData.append([mdl.readUInt(), mdl.readPtr(subOffset), mdl.readUInt() >> 16, mdl.readUInt()])
        mdl.seek(0x10, 1)
    #faceOffset = vtxOffset + vtxSize

    mdl.seek(vtxOffset)
    vtxData = bytearray(mdl.readBytes(vtxSize))
    for clr in range(0x18, len(vtxData), 0x1C):
        # Vertex colors need to be changed from ARGB to RGBA
        clrData = list(vtxData[clr:clr + 4])
        clrData.append(clrData.pop(0))
        vtxData[clr:clr + 4] = clrData
    boMdlVtxClrPreview(vtxData, 0x18, 0x1C)

    rapi.rpgBindPositionBuffer(vtxData, noesis.RPGEODATA_FLOAT, 0x1C)
    rapi.rpgBindUV1BufferOfs(vtxData, noesis.RPGEODATA_FLOAT, 0x1C, 0x10)
    rapi.rpgBindColorBufferOfs(vtxData, noesis.RPGEODATA_UBYTE, 0x1C, 0x18, 4)

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

def boMdlParseTrack(mdl, mdlVer, mdlSystem, mdlOffset, subCount, unitIdx, mdlType=None, grpOffset=None, matList=None):
    # mdlType for streamed is reserved for LOD if is int? (maybe)
    for sub in range(subCount):
        mdlOffset += 0x40  # The first 0x40 bytes of each model header are some floats before actual info data starts
        #if (unitIdx, sub) in {(0, 9), (1, 4), (2, 4), (3, 4)}: continue  # Debug: for model renders, skipping cubes
        mdlName = "unit_{:03}_sub_".format(unitIdx) if mdlType is None else "{}_grp_{:03}_mdl_{:03}_sub_".format(mdlType, unitIdx, sub)
        if mdlSystem == BoPS2:  # matList needed only for PS2 line geometry
            boMdlPS2Track(mdl, mdlVer, mdlOffset, mdlName, grpOffset, matList)
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
            rapi.rpgSetTransform(NoeMat43(((1, 0, 0), (0, 1, 0), (0, 0, 1), (0, 0, sub * 8))))
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
    texHeader = tex.readBytes(0x8)
    if texEndian == NOE_BIGENDIAN:
        return BoXbox360
    if texHeader.startswith(b"\x01\x00\x04\x00"):
        return BoXbox
    if texHeader == bytes(0x8):
        return BoPSP
    if texHeader.startswith(bytes(0x4)):
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
        tex = BoBitStream(tex)
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
    bmpOffset = tex.readPtr(texOffset)
    palOffset = tex.readPtr(texOffset)
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
    palOffset = tex.readPtr(texOffset)
    texWidth = tex.readUInt()
    texHeight = tex.readUInt()
    bitDepth = tex.readUInt()
    tex.seek(texOffset + 0x38)
    bmpOffset = tex.readPtr(texOffset)
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
    bmpOffset = tex.readPtr(texOffset)
    tex.seek(texOffset + 0xA0)
    palOffset = tex.readPtr(texOffset)

    if BoDebug:
        print("\nPlayStation Portable arena texture detected!"
            + "\nTexture name: {}".format(texName)
            + "\nTexture offset: 0x{:X}".format(texOffset + 16)
            + "\nTexture data offset: 0x{:X}".format(bmpOffset + 16)
            + "\nTexture dimensions: {} x {}".format(texWidth, texHeight)
            + "\nTexture bit depth: {}".format(bitDepth)
            + "\nPalette data offset: 0x{:X}".format(palOffset + 16))

    tex.seek(bmpOffset)
    if texFmt == 0x2:
        texData = tex.readBytes(texWidth * texHeight // 2)
    elif texFmt == 0x3:
        texData = tex.readBytes(texWidth * texHeight)

    tex.seek(palOffset)
    palData = boTexPalRead(tex, bitDepth)

    texData = rapi.imageUntwiddlePSP(texData, texWidth, texHeight, bitDepth)
    texData = rapi.imageDecodeRawPal(texData, palData, texWidth, texHeight, bitDepth, "R8G8B8A8")
    texList.append(NoeTexture(texName, texWidth, texHeight, texData, noesis.NOESISTEX_RGBA32))

def boTexXbox(tex, texList, texOffset, texName):
    tex.seek(texOffset + 0x4)
    bmpOffset = tex.readPtr(texOffset)
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

    if texFmt == 0xB:
        texData = rapi.imageFromMortonOrder(tex.readBytes(texWidth * texHeight), texWidth, texHeight, 1)
        tex.seek(texOffset + 0x14)
        for pal in range(palCount):
            palOffset = tex.readPtr(texOffset)
            curPalOffset = tex.getOffset()
            tex.seek(palOffset)
            if not tex.readBytes(0x4) in {b"\x01\x00\x03\x00", b"\x01\x00\x03\xC0"}:
                noesis.doException(BoExcFmt + "Invalid palette header!")
            palDataOffset = tex.readPtr(texOffset)

            if BoDebug:
                print("Palette {} offset: 0x{:X}".format(pal + 1, palOffset)
                    + "\nPalette {} data offset: 0x{:X}".format(pal + 1, palDataOffset))

            tex.seek(palDataOffset)
            palData = boTexPalRead(tex, bitDepth)
            texPalData = rapi.imageDecodeRawPal(texData, palData, texWidth, texHeight, 8, "B8G8R8A8")
            texList.append(NoeTexture(boSetPalName(texName, palCount, pal), texWidth, texHeight, texPalData, noesis.NOESISTEX_RGBA32))
            tex.seek(curPalOffset)
        return

    elif texFmt == 0xC:
        texFmt = noesis.NOESISTEX_DXT1
        texData = tex.readBytes(wPad * hPad // 2)
    elif texFmt == 0xE:
        texFmt = noesis.NOESISTEX_DXT3
        texData = tex.readBytes(wPad * hPad)
    elif texFmt == 0xF:
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
    texData = boTexFixWidth(tex, texWidth, 256, texHeight) if texFmt == 0x2 and texWidth < 256 else tex.readBytes(texSize - 0x1000)

    if texFmt == 0x2:
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
    arcEndian = NOE_LITTLEENDIAN if arc.readBytes(0x8) == G_TEXDIC else NOE_BIGENDIAN
    arc.setEndian(arcEndian)

    texCount = arc.readUInt()
    offStart = arc.readPtr(startOffset)
    arc.seek(offStart)
    for tex in range(texCount):
        texNum = arc.readUInt64()
        texOffset = arc.readPtr(startOffset)
        curOffset = arc.getOffset() + 0x4
        boTexParse(arc, arcEndian, texList, texOffset)
        if BoDebug:
            print("Texture {} of {}".format(texNum, texCount))
        arc.seek(curOffset)

def boArcMdlBxv(data, mdlList):
    rapi.processCommands("-texnorepfn")
    arc = BoBitStream(boDecZlib(data) if data.startswith(b"\x78\xDA") else data)
    texList = list()

    arcVer, arcEndian = boGetVerEndian(arc)

    arc.seek(0x60)
    if arcVer < 0x20:
        texOffset = arc.readPtr()
        boTexParse(arc, arcEndian, texList, texOffset)
        arcSystem = boTexGetSystem(arc, arcEndian, texOffset)

    else:  # Xbox 360 only
        arcSystem = BoXbox360
        for tex in range(19):
            texOffset = arc.readPtr()
            if texOffset:
                curTexOffset = arc.getOffset()
                arc.seek(texOffset + 0x48)
                if arc.readUInt() != 0x2:
                    # Non-paletted texture
                    boTexParse(arc, arcEndian, texList, texOffset)

                else:
                    texName = boTexGetName(arc, arcEndian, texOffset)
                    arc.seek(curTexOffset)
                    for pal in range(19 - tex):
                        palOffset = arc.readPtr()
                        if palOffset:
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

    # this is debug/test stuff, do not use
    rapi.rpgCreateContext()
    matList = list()

    if arcEndian == NOE_BIGENDIAN:
        rapi.rpgSetOption(noesis.RPGOPT_BIGENDIAN, True)

    matName = BoMatName.format(0)
    mat = NoeMaterial(matName, texList[0].name)
    mat.setFlags(noesis.NMATFLAG_TWOSIDED)
    mat.setDefaultBlend(False)
    rapi.rpgSetMaterial(matName)
    matList.append(mat)

    # TODO: split in its own boMdlParseVehicle(), this is just a temporary test thing
    if arcSystem == BoPS2:
        arc.seek(0xC if arcVer <= 0x17 else 0x8)
        mdlParts = arc.readUByte()
        mdlWheels = arc.readUByte()
        if arcVer <= 0x17:
            mdlLodMin = arc.readUShort()
            mdlLodMax = arc.readUShort()
        else:
            mdlLodMin = arc.readUByte()
            mdlLodMax = arc.readUByte()

        # 0x50 for Xbox
        arc.seek(0x4C + mdlLodMax * 0x4)
        lodOffset = arc.readPtr()

        # TEMP: 1x body, 6x/8x parts, 3x wheels
        for idx in range(4 + (6 if arcVer <= 0x17 else 8)):
            arc.seek(lodOffset + idx * 0x4)
            hdrOffset = arc.readPtr(lodOffset)
            if hdrOffset:
                arc.seek(hdrOffset + 0xC)
                vifStart = arc.readPtr(hdrOffset + 0xC)
                vifFull = arc.readPtr(hdrOffset + 0xC)
                rapi.rpgSetName(str(idx))
                boMdlPS2(arc, vifStart, vifFull)

        #rapi.rpgSetName("lod")
        #boMdlPS2(arc, 0x67B80, 0x0)
        #boMdlPS2(arc, 0x67600, 0x67980)

    try:
        mdl = rapi.rpgConstructModel()
    except:
        mdl = NoeModel()
    mdl.setModelMaterials(NoeModelMaterials(texList, matList))
    mdlList.append(mdl)
    return True

def boArcMdlDatStatic(data, mdlList):
    #rapi.setPreviewOption("setAngOfs", "0 -60 120")  # 0 -60 120 # 0 -240 60
    rapi.processCommands("-texnorepfn")  # -rotate 0 15 0 # 0 -15 0
    arc = BoBitStream(boDecZlib(data) if data.startswith(b"\x78\xDA") else data)
    texList = list()

    arcVer, arcEndian = boGetVerEndian(arc)

    if arcVer <= 0x25:  # B3 demo & pre-alpha US_C4
        arc.seek(0x14)
        texCount = arc.readUInt()
    else:
        arc.seek(0x16)
        texCount = arc.readUShort()
    texArrayOffset = arc.readPtr()

    texName = dict()
    for tex in range(texCount):
        arc.seek(texArrayOffset + 0x4 * tex)
        texOffset = arc.readPtr()
        boTexParse(arc, arcEndian, texList, texOffset)
        texName[texOffset] = boTexGetName(arc, arcEndian, texOffset)

        if BoDebug:
            print("Texture {} of {}".format(tex + 1, texCount))

    arcSystem = boTexGetSystem(arc, arcEndian, texOffset)

    if not BoModels:
        boSetDummyMdl(mdlList, texList)
        return True

    rapi.rpgCreateContext()
    matList = list()

    if arcEndian == NOE_BIGENDIAN:
        rapi.rpgSetOption(noesis.RPGOPT_BIGENDIAN, True)

    arc.seek(0x8)
    matOffset = arc.readPtr()
    matCount = arc.readUShort()
    matAnimCount = arc.readUShort()
    matAnimOffset = arc.readPtr()

    # Materials (may be moved into its own function loop, idk)
    arc.seek(matAnimOffset)
    matAnimIdx = [arc.readUShort() for idx in range(matAnimCount)]

    arc.seek(matOffset)
    for idx in range(matCount):
        mat = NoeMaterial(BoMatName.format(idx), "")
        mat.setMetal(0, 0)  # For some reason set to 1 by default in Noesis

        matType = arc.readUInt()  # Render type (normal, wireframe, use alpha specular etc.)
        arc.seek(matOffset + 0xC)  # Two floats, don't seem to have any effect in-game, unused?
        texPtrOffset = arc.readPtr(matOffset)
        if texPtrOffset:
            arc.seek(texPtrOffset)
            texOffset = arc.readPtr(matOffset)
            mat.setTexture(texName.get(texOffset))

        if idx in matAnimIdx:
            arc.seek(matOffset + 0x10)
            # how many textures to cycle ahead from the current one
            matAnimCurIdx = arc.readByte()  # should always be 0 by default
            matAnimMaxIdx = arc.readByte()
            arc.seek(matOffset + 0x14)  # 0x12 is set to 1 if texcycle reaches the last index
            # how long to wait after reaching the end of texcycle, or how fast to uv scroll
            matAnimLength = arc.readFloat()
            # set to -(matAnimLength) when texcycle is running, 0, then the same value
            matAnimUnk = arc.readFloat()
            matAnimTick = arc.readFloat()  # counter for how many anim ticks have passed idk

        # Texture rendering parameters
        matFlags = int()
        if arcSystem == BoPS2:
            arc.seek(matOffset + 0x20)
            matInfoAlpha = arc.readUInt()  # 0x20
            matInfo = arc.readUShort()  # 0x24
            if matInfo & 0x0020 or matType in {0x4, 0x5}:
                matFlags |= noesis.NMATFLAG_TWOSIDED
            #if matInfo & 0x0018:  # makes water show through?  also reflect heavily on cars?
            #if matInfo & 0x0400:  # makes props show through?
            #if matInfo & 0x0200:  # use uv scrolling
            matInfo = arc.readUByte()   # 0x26  # also color related like matAlpha?
            #if matInfo & 0x04:  # draw mesh with the stuff below?
            #if matInfo & 0x44:  # use original alpha
            #if matInfo & 0x80:  # full black texture?
            if matInfo == 0x64:  # 0x24 | 0x44 (0x64)  # override texture alpha
                #matAlpha = arc.readUByte() * 2  # 0x27
                #if matAlpha == 0x100:
                #    matAlpha -= 1
                if matInfoAlpha & 0xFF != 0xD:
                    mat.setDefaultBlend(False)
                    #mat.setBlendMode(noesis.NOEBLEND_ONE, noesis.NOEBLEND_SRC_ALPHA)
                    #mat.setBlendMode("GL_ONE", "GL_SRC_ALPHA")
                #mat.setDiffuseColor((1, 1, 1, matAlpha / 255))
            #if matType == 0x3:
            #    mat.setSkipRender(True)
            mat.setUserData(b"GEO_LINE", repr(matType == 0x3).encode())

        elif arcSystem == BoPSP:
            #if matType == 0x2:  # skip render?
            arc.seek(matOffset + 0x24)
            matInfo = arc.readUShort()
            # Legends has some screwed up materials and sets these flags from previous ones???
            if matInfo & 0x0020 or matType in {0x8, 0x9}:
                matFlags |= noesis.NMATFLAG_TWOSIDED
            #matInfo & 0x0010 only sometimes applies???
            if not matInfo & 0x0011:
                mat.setDefaultBlend(False)
            #if matInfo & 0x0200:  # use uv scrolling

        else:  # Xbox, Xbox 360?  not yet parsed properly
            arc.seek(matOffset + 0x24)
            matAlphaTest = arc.readUByte() / 100  # Xbox
            matBlend2 = arc.readUByte()

            if not 0x2 <= matType <= 0x6:
                mat.setDefaultBlend(False)
            #else:
            #    mat.setAlphaTest(matAlphaTest)
            #if matType == 0x2:
                #mat.setTexture(None)
                #mat.setEnvTexture(texName.get(texOffset))

        matOffset = arc.seek(matOffset + 0x28)
        mat.setFlags(matFlags)
        matList.append(mat)

    # Static Models
    arc.seek(0x1C)
    mdlCount = [arc.readUShort() for mdl in range(4)]

    for mdl, mdlType in enumerate(("backdrop", "chevron", "water", "reflection")):
        arc.seek(0x24 + mdl * 4)
        grpOffset = arc.readPtr()
        arc.seek(grpOffset)
        for grp in range(mdlCount[mdl]):
            grpOffset = arc.getOffset()
            subCount = arc.readUShort()
            arc.seek(0x2, 1)
            mdlOffset = arc.readPtr(grpOffset)
            boMdlParseTrack(arc, arcVer, arcSystem, mdlOffset, subCount, grp, mdlType, grpOffset, matList)
            arc.seek(grpOffset + 0x8)

            if BoDebug:
                print("Model {} of {} ({})".format(grp + 1, mdlCount[mdl], mdlType))

    # Everything beyond this point has 0x70 bytes of nothing on PSP

    # Props & Instances
    # not a fan of relative seeks for readability, to be redone (maybe)
    arc.seek(0x34)
    if arcSystem == BoPSP:
        arc.seek(0x70, 1)
    instCount = arc.readUShort()
    propCount = arc.readUShort()
    instOffset = arc.readPtr()
    propOffset = arc.readPtr()
    if arcVer >= 0x30:
        if propCount != 0:
            noesis.doException("Invalid State! Expected 0 for old props in Static version {:02X}, got {}".format(arcVer, propCount))
        propCount = arc.readUInt()
        if arcSystem == BoXbox360:
            arc.seek(0x4, 1)  # unk
        arc.seek(0x4, 1)  # also unk
    propSpawns = arc.readUInt()
    if arcVer < 0x30:
        # B3/Legends props only
        propUnkOffset = arc.readPtr()  # bytearray, same length as propCount
        propMatOffset = arc.readPtr()
        propPtrOffset = arc.readPtr()
        propUnkOffset = arc.readPtr()  # animated blinking lights?
        propNum = 0

    instLodPtr = {
        BoPS2: 0x88,
        BoPSP: 0x88 if arcVer == 0x27 else 0x168,
        BoXbox: 0x98,
        BoXbox360: 0xA8
    }.get(arcSystem)

    # probably just have to call with a specific index and scale/transform params
    #boMdlParsePropInst(arc, arcVer, arcSystem, instOffset, instCount, "inst")
    #boMdlParsePropInst(arc, arcVer, arcSystem, propOffset, propCount, "prop")

    propFile = os.path.join(os.path.split(rapi.getInputName())[0], "PropInst.dat")
    if arcVer >= 0x30 and os.path.exists(propFile) and os.path.getsize(propFile):
        data = rapi.loadIntoByteArray(propFile)
        if boChkDatPropInst(data):
            prop = BoBitStream(data)
            boGetVerEndian(prop)  # just to override endianness

            prop.seek(0x8)
            propIdxOffset = prop.readPtr()
            propMatOffset = prop.readPtr()

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
        mdl = BoBitStream(rapi.loadIntoByteArray(streamFile))
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
        unitOffset = arc.readPtr()

        for unit in range(unitCount):
            arc.seek(unitOffset + 0x10 * unit)
            subOffset = arc.readPtr() + 0x10
            lodOffset = arc.readPtr() + 0x10
            subSize = arc.readUInt()
            lodSize = arc.readUInt()

            if subSize:
                boMdlParseTrack(mdl, arcVer, arcSystem, subOffset, 1, unit, matList=matList)

            # material array is nonexistent and instead inherited from above(?)
            # the data below also contains collisions and vehicle lighting data
            if lodSize:
                #boMdlParseTrack(mdl, arcVer, arcSystem, lodOffset, 1, unit, matList=matList)

                instDataOffset = lodOffset + instLodPtr

                mdl.seek(instDataOffset)
                instIdxOffset = mdl.readPtr(instDataOffset)
                instPtrOffset = mdl.readPtr(instDataOffset)
                # only in PS2 Dominator?
                #animIdxOffset = mdl.readPtr(instDataOffset)
                #animPtrOffset = mdl.readPtr(instDataOffset)

                instNum = 0
                for idx in range(instCount):
                    mdl.seek(instIdxOffset + idx)
                    instIdxCount = mdl.readUByte()
                    mdl.seek(instPtrOffset + 0x4 * idx)
                    instMatOffset = mdl.readPtr(instDataOffset)

                    for inst in range(instIdxCount):
                        instName = "unit_{:03}_inst_{:03}_mdl".format(unit, instNum)
                        mdl.seek(instMatOffset + 0x40 * inst)
                        rapi.rpgSetTransform(NoeMat44.fromBytes(mdl.readBytes(0x40)).toMat43())
                        boMdlParsePropInst(arc, arcVer, arcSystem, instOffset, instCount, instName, idx)
                        instNum += 1

            # for B3/Legends streamed props are set in static.dat, maybe should be loaded outside of here?
            if arcVer < 0x30:
                propIdx = 0
                arc.seek(propPtrOffset + 0x4 * unit)
                propIdxOffset = arc.readPtr()
                for idx in range(propCount):
                    arc.seek(propIdxOffset + idx)
                    propIdxCount = arc.readUByte()

                    for prop in range(propIdxCount):
                        arc.seek(propMatOffset + 0x40 * propNum)
                        propName = "unit_{:03}_prop_{:03}_mdl".format(unit, propIdx)
                        rapi.rpgSetTransform(NoeMat44.fromBytes(arc.readBytes(0x40)).toMat43())
                        boMdlParsePropInst(arc, arcVer, arcSystem, propOffset, propCount, propName, idx)
                        propIdx += 1
                        propNum += 1

            rapi.rpgSetTransform(None)

            if BoDebug:
                print("Unit {} of {}".format(unit + 1, unitCount))

    try:
        mdl = rapi.rpgConstructModel()
    except:
        mdl = NoeModel()
    mdl.setModelMaterials(NoeModelMaterials(texList, matList))
    mdlList.append(mdl)
    return True

def boArcTexDatEnviro(data, texList):
    rapi.processCommands("-texnorepfn")
    arc = BoBitStream(data)

    arc.seek(0xB8)
    arcEndian = NOE_BIGENDIAN if arc.readBytes(0x4) == b"\x45\x44\x00\x03" else NOE_LITTLEENDIAN
    arc.setEndian(arcEndian)

    arcSize = arc.getSize()
    arc.seek(0x98)
    while True:
        texOffset = arc.readPtr()
        if not 0xB0 <= texOffset <= arcSize:
            break
        curTexOffset = arc.getOffset()
        boTexParse(arc, arcEndian, texList, texOffset)
        arc.seek(curTexOffset)
    return True

def boArcTexBinFE(data, texList):
    rapi.processCommands("-texnorepfn -fulltexpath")
    arc = BoBitStream(data)

    arcEndian = NOE_LITTLEENDIAN if arc.readBytes(0x8) == G_MOVIEARRAY else NOE_BIGENDIAN
    arc.setEndian(arcEndian)

    dirCount = arc.readUInt()
    dirOffset = arc.readPtr()

    arc.seek(dirOffset)
    for dir in range(dirCount):
        dirInfoOffset = arc.readPtr()
        curHdrOffset = arc.getOffset()

        arc.seek(dirInfoOffset)
        dirNameOffset = arc.readPtr()
        dirDataOffset = arc.readPtr()
        arc.seek(dirNameOffset)
        dirName = arc.readString()

        arc.seek(dirDataOffset + 0x4)
        texCount = arc.readUInt()

        #boPrepExportPath(dirName)

        if texCount:
            boPrepExportPath(dirName)

            texArrayOffset = arc.readPtr(dirDataOffset)
            aptDataOffset = arc.readPtr(dirDataOffset)
            aptConstOffset = arc.readPtr(dirDataOffset)

            arc.seek(texArrayOffset)
            texOffset = [arc.readPtr(dirDataOffset) for tex in range(texCount)]
            texName = [boTexGetName(arc, arcEndian, tex) for tex in texOffset]
            texArray = dict(zip(texName, texOffset))

            boGetTexAptIndex(arc, aptDataOffset, int(texName[0][11:]) + 1 if texName[0].startswith("TexturePage") else int(texName[0]))
            for name in range(texCount):
                texNameOffset = arc.readPtr(aptDataOffset)
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
    arc = BoBitStream(data)

    txdCount = arc.readUInt64()
    arcAlign = boCalcAlign(txdCount * 0x10 + 0x8, 0x800)
    for txd in range(txdCount):
        txdName = boDecGtID(arc.readUInt64())
        txdSize = arc.readUInt()
        txdOffset = arc.readPtr() + arcAlign
        curOffset = arc.getOffset()
        boArcTxdParse(arc, texList, txdOffset)
        if BoDebug:
            print("Texture dictionary name: {}".format(txdName)
                + "\nTexture dictionary offset: 0x{:X}".format(txdOffset))
        arc.seek(curOffset)
    return True

def boArcTexBinFont(data, texList):
    rapi.processCommands("-texnorepfn")
    arc = BoBitStream(data)

    arcEndian = NOE_LITTLEENDIAN
    fontMagic = arc.readBytes(0x4)
    if fontMagic in {b"v1.4", b"4.1v"}:
        if fontMagic == b"v1.4":
            arcEndian = NOE_BIGENDIAN
            arc.setEndian(arcEndian)
        texOffset = arc.readPtr()
        boTexParse(arc, arcEndian, texList, texOffset)
    else:
        arc.seek(0x0)
        fontName = arc.readString()
        arc.seek(0x70)
        texOffset = arc.readPtr()
        boTexParse(arc, arcEndian, texList, texOffset, texExtra=fontName)
    return True

def boArcTexTxd(data, texList):
    rapi.processCommands("-texnorepfn")
    arc = BoBitStream(data)
    boArcTxdParse(arc, texList)
    return True

def boArcTexArena(data, texList):
    rapi.processCommands("-texnorepfn -fulltexpath")
    arc = BoBitStream(data[16:])

    arenaName = arc.readString()
    arc.seek(0x40)
    texOffset = arc.readPtr()

    if arenaName.lower().endswith(".msh"):  # Texture
        boTexPSPArena(arc, texList, 0x0)

    elif texOffset != 0:  # Font
        boTexPSPArena(arc, texList, texOffset, fontName=arenaName)

    else:  # Frontend
        arc.seek(0x80)
        aptDataOffset = arc.readPtr()
        aptConstOffset = arc.readPtr()
        unkPtrOffset = arc.readPtr()
        texPtrOffset = arc.readPtr()

        arc.seek(texPtrOffset)
        texCount = arc.readUInt()
        if texCount != 0:
            texArrayOffset = arc.readPtr()

            # If the first texture index isn't 1, there are no texture names stored in Apt Data.
            if arc.readUInt() == 1:
                boGetTexAptIndex(arc, aptDataOffset, 1)
                texNameOffset = arc.readPtr()
                if texNameOffset < texArrayOffset:
                    arc.seek(-0x4, 1)

                    for tex in range(texCount):
                        texNameOffset = arc.readPtr(aptDataOffset)
                        texNameIndex = arc.readUInt()
                        curAptOffset = arc.getOffset()

                        arc.seek(texNameOffset)
                        texName = arc.readString()
                        arc.seek(texArrayOffset)
                        texOffsetIndex = arc.readUInt()
                        texOffset = arc.readPtr()
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
                texOffset = arc.readPtr()
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
        if chk.read(0xC) != b"FX1?\x03" + bytes(0x7):
            return False
        if isChk:
            return True

    print("Loading archive parts...")
    arc = [BoBitStream(rapi.loadIntoByteArray(fileName))]

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
        arc.append(BoBitStream(rapi.loadIntoByteArray(fileName)))

    for sub in range(fileCount):
        nameOffset = arc[0].readPtr(nameData)
        fileSize = arc[0].readUInt()
        fileOffset = arc[0].readPtr() * 0x800
        if arcSize != fileLen:
            arcIdx = arc[0].readUByte()
            arc[0].seek(0x3, 1)
        else:
            arc[0].seek(0x18, 1)
        curArcPos = arc[0].getOffset()

        arc[0].seek(nameOffset)
        fileName = arc[0].readString()
        arc[arcIdx].seek(fileOffset)
        rapi.exportArchiveFile(fileName, arc[arcIdx].readBytes(fileSize))

        if BoDebug:
            print("\nFXP archive file detected! (Version 3)"
                + "\nFile name: {}".format(fileName)
                + "\nFile name offset: 0x{:X}".format(nameOffset)
                + "\nFile size: 0x{:X}".format(fileSize)
                + "\nFile offset: 0x{:X}".format(fileOffset)
                + "\nArchive part index: {}".format(arcIdx)
                + "\nFile {} of {}".format(sub + 1, fileCount))
        else:
            print("Extracted", fileName)
        arc[0].seek(curArcPos)
    return True

def nfsArcMdlTmm(data, mdlList):
    rapi.rpgCreateContext()
    arc = BoBitStream(data[0x50:])
    matList = list()

    mdlOffset = arc.readPtr()
    arc.seek(0x8)
    mdlSize = arc.readUInt()  # this is actually a pointer to the end but lmao
    arc.seek(0x18)
    vtxCount = arc.readUInt()

    mat = NoeMaterial("mat0", "")
    mat.setFlags(noesis.NMATFLAG_TWOSIDED, 1)
    matList.append(mat)

    rapi.rpgSetMaterial("mat0")

    arc.seek(mdlOffset)
    vtxData = arc.readBytes(mdlSize)
    rapi.rpgBindPositionBuffer(vtxData, noesis.RPGEODATA_FLOAT, 0xC)
    rapi.rpgCommitTriangles(None, noesis.RPGEODATA_USHORT, vtxCount, noesis.RPGEO_TRIANGLE_STRIP)

    mdl = rapi.rpgConstructModel()
    mdl.setModelMaterials(NoeModelMaterials(list(), matList))
    mdlList.append(mdl)
    return True

def blkArcTexDb(data, texList):
    rapi.processCommands("-texnorepfn")
    arc = BoBitStream(data)

    arcVer = arc.readUInt()
    if arcVer != 4:
        arc.seek(0x1C)
    txdOffset = arc.readPtr()
    boArcTxdParse(arc, texList, txdOffset)
    return True

def blkArcTexBinGlob(data, texList):
    rapi.processCommands("-texnorepfn")
    arc = BoBitStream(data)

    arc.seek(0x4)
    txdOffset = arc.readPtr()
    boArcTxdParse(arc, texList, txdOffset)
    return True

def blkArcTexBinGuns(data, texList):
    rapi.processCommands("-texnorepfn")
    arc = BoBitStream(data)

    txdOffset = arc.readPtr()
    boArcTxdParse(arc, texList, txdOffset)
    return True

def blkArcTexBinLevel(data, texList):
    rapi.processCommands("-texnorepfn")
    arc = BoBitStream(data)

    chkVer = arc.readUInt()
    arc.seek({
        0xA: 0x2BC,
        0x11: 0x390
    }.get(chkVer))
    txdOffset = arc.readPtr()
    boArcTxdParse(arc, texList, txdOffset)
    return True

def blkArcTexBinStLevel(data, texList):
    rapi.processCommands("-texnorepfn")
    arc = BoBitStream(data)

    arc.seek(0xC)
    hdrOffset = arc.readPtr()
    arc.seek(0x4)
    txdOffset = arc.readPtr(hdrOffset)
    boArcTxdParse(arc, texList, txdOffset)
    return True

def blkArcTexBinStUnit(data, texList):
    rapi.processCommands("-texnorepfn")
    arc = BoBitStream(data)

    arc.seek(0x8)
    hdrOffset = arc.readPtr()
    arc.seek(hdrOffset + 0x1C)
    txdOffset = arc.readPtr(hdrOffset)
    boArcTxdParse(arc, texList, txdOffset)
    return True

def blkArcTexBinUnit(data, texList):
    rapi.processCommands("-texnorepfn")
    arc = BoBitStream(data)

    arcVer = arc.readUInt()
    if arcVer == 0xC:
        arc.seek(0x18)
    elif 0x16 <= arcVer <= 0x18:
        arc.seek(0x24)
    txdOffset = arc.readPtr()
    boArcTxdParse(arc, texList, txdOffset)
    return True
