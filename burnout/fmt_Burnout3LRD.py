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
#   Models:
#       WIP

# This plugin is brought to you by the Burnout Modding community.
#               burnout.wiki  |  discord.gg/8zxbb4x              

# Written by Edness   v0.6b   2021-06-23 - 2022-04-29

boDebug = False
boModels = False

from inc_noesis import *
import zlib

def registerNoesisTypes():
    handleBxv = noesis.register("Burnout 3Td, Leg, Rev, Dom, NFS Shift - Vehicles", ".bgv;.btv")
    noesis.setHandlerTypeCheck(handleBxv, boChkBxv)
    noesis.setHandlerLoadModel(handleBxv, boArcMdlBxv)

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

    ### BLACK ###

    handleBinDb = noesis.register("Black - DB", ".db")
    noesis.setHandlerTypeCheck(handleBinDb, blkChkDb)
    noesis.setHandlerLoadRGBA(handleBinDb, blkArcTexDb)

    handleBinGlob = noesis.register("Black - GlobData", ".bin")
    noesis.setHandlerTypeCheck(handleBinGlob, blkChkBinGlob)
    noesis.setHandlerLoadRGBA(handleBinGlob, blkArcTexBinGlob)

    handleBinUnit = noesis.register("Black - Unit", ".bin")
    noesis.setHandlerTypeCheck(handleBinUnit, blkChkBinUnit)
    noesis.setHandlerLoadRGBA(handleBinUnit, blkArcTexBinUnit)

    handleBinLvl = noesis.register("Black - LevelDat", ".bin")
    noesis.setHandlerTypeCheck(handleBinLvl, blkChkBinLevel)
    noesis.setHandlerLoadRGBA(handleBinLvl, blkArcTexBinLevel)

    handleBinStLvl = noesis.register("Black - StLevel", ".bin")
    noesis.setHandlerTypeCheck(handleBinStLvl, blkChkBinStLevel)
    noesis.setHandlerLoadRGBA(handleBinStLvl, blkArcTexBinStLevel)

    handleBinStUnit = noesis.register("Black - StUnit", ".bin")
    noesis.setHandlerTypeCheck(handleBinStUnit, blkChkBinStUnit)
    noesis.setHandlerLoadRGBA(handleBinStUnit, blkArcTexBinStUnit)

    handleBinGuns = noesis.register("Black - Guns", ".bin")
    noesis.setHandlerTypeCheck(handleBinGuns, blkChkBinGuns)
    noesis.setHandlerLoadRGBA(handleBinGuns, blkArcTexBinGuns)

    if boDebug:
        noesis.logPopup()
    return True

def boCalcAlign(padFrom, padTo):
    return (padFrom // padTo + 1) * padTo

def boConvToInt(data, endian):
    return int.from_bytes(data, endian)

def boDecGtID(cGtID):
    # Decompresses GtID strings
    char = " -/0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_"
    decStr = ""
    for chr in range(12):
        decStr += char[cGtID % len(char)]
        cGtID //= len(char)
    return decStr[::-1].strip()

def boDecZlib(data):
    # Not using Noesis' rapi.decompInflate() because it doesn't support partial decompression
    return zlib.decompressobj().decompress(data)

def boEncGtHash(str):
    # Calculates strings into GtHash values
    hashTable = (
        0x00000000, 0x77073096, 0xEE0E612C, 0x990951BA, 0x076DC419, 0x706AF48F, 0xE963A535, 0x9E6495A3,
        0x0EDB8832, 0x79DCB8A4, 0xE0D5E91E, 0x97D2D988, 0x09B64C2B, 0x7EB17CBD, 0xE7B82D07, 0x90BF1D91,
        0x1DB71064, 0x6AB020F2, 0xF3B97148, 0x84BE41DE, 0x1ADAD47D, 0x6DDDE4EB, 0xF4D4B551, 0x83D385C7,
        0x136C9856, 0x646BA8C0, 0xFD62F97A, 0x8A65C9EC, 0x14015C4F, 0x63066CD9, 0xFA0F3D63, 0x8D080DF5,
        0x3B6E20C8, 0x4C69105E, 0xD56041E4, 0xA2677172, 0x3C03E4D1, 0x4B04D447, 0xD20D85FD, 0xA50AB56B,
        0x35B5A8FA, 0x42B2986C, 0xDBBBC9D6, 0xACBCF940, 0x32D86CE3, 0x45DF5C75, 0xDCD60DCF, 0xABD13D59,
        0x26D930AC, 0x51DE003A, 0xC8D75180, 0xBFD06116, 0x21B4F4B5, 0x56B3C423, 0xCFBA9599, 0xB8BDA50F,
        0x2802B89E, 0x5F058808, 0xC60CD9B2, 0xB10BE924, 0x2F6F7C87, 0x58684C11, 0xC1611DAB, 0xB6662D3D,
        0x76DC4190, 0x01DB7106, 0x98D220BC, 0xEFD5102A, 0x71B18589, 0x06B6B51F, 0x9FBFE4A5, 0xE8B8D433,
        0x7807C9A2, 0x0F00F934, 0x9609A88E, 0xE10E9818, 0x7F6A0DBB, 0x086D3D2D, 0x91646C97, 0xE6635C01,
        0x6B6B51F4, 0x1C6C6162, 0x856530D8, 0xF262004E, 0x6C0695ED, 0x1B01A57B, 0x8208F4C1, 0xF50FC457,
        0x65B0D9C6, 0x12B7E950, 0x8BBEB8EA, 0xFCB9887C, 0x62DD1DDF, 0x15DA2D49, 0x8CD37CF3, 0xFBD44C65,
        0x4DB26158, 0x3AB551CE, 0xA3BC0074, 0xD4BB30E2, 0x4ADFA541, 0x3DD895D7, 0xA4D1C46D, 0xD3D6F4FB,
        0x4369E96A, 0x346ED9FC, 0xAD678846, 0xDA60B8D0, 0x44042D73, 0x33031DE5, 0xAA0A4C5F, 0xDD0D7CC9,
        0x5005713C, 0x270241AA, 0xBE0B1010, 0xC90C2086, 0x5768B525, 0x206F85B3, 0xB966D409, 0xCE61E49F,
        0x5EDEF90E, 0x29D9C998, 0xB0D09822, 0xC7D7A8B4, 0x59B33D17, 0x2EB40D81, 0xB7BD5C3B, 0xC0BA6CAD,
        0xEDB88320, 0x9ABFB3B6, 0x03B6E20C, 0x74B1D29A, 0xEAD54739, 0x9DD277AF, 0x04DB2615, 0x73DC1683,
        0xE3630B12, 0x94643B84, 0x0D6D6A3E, 0x7A6A5AA8, 0xE40ECF0B, 0x9309FF9D, 0x0A00AE27, 0x7D079EB1,
        0xF00F9344, 0x8708A3D2, 0x1E01F268, 0x6906C2FE, 0xF762575D, 0x806567CB, 0x196C3671, 0x6E6B06E7,
        0xFED41B76, 0x89D32BE0, 0x10DA7A5A, 0x67DD4ACC, 0xF9B9DF6F, 0x8EBEEFF9, 0x17B7BE43, 0x60B08ED5,
        0xD6D6A3E8, 0xA1D1937E, 0x38D8C2C4, 0x4FDFF252, 0xD1BB67F1, 0xA6BC5767, 0x3FB506DD, 0x48B2364B,
        0xD80D2BDA, 0xAF0A1B4C, 0x36034AF6, 0x41047A60, 0xDF60EFC3, 0xA867DF55, 0x316E8EEF, 0x4669BE79,
        0xCB61B38C, 0xBC66831A, 0x256FD2A0, 0x5268E236, 0xCC0C7795, 0xBB0B4703, 0x220216B9, 0x5505262F,
        0xC5BA3BBE, 0xB2BD0B28, 0x2BB45A92, 0x5CB36A04, 0xC2D7FFA7, 0xB5D0CF31, 0x2CD99E8B, 0x5BDEAE1D,
        0x9B64C2B0, 0xEC63F226, 0x756AA39C, 0x026D930A, 0x9C0906A9, 0xEB0E363F, 0x72076785, 0x05005713,
        0x95BF4A82, 0xE2B87A14, 0x7BB12BAE, 0x0CB61B38, 0x92D28E9B, 0xE5D5BE0D, 0x7CDCEFB7, 0x0BDBDF21,
        0x86D3D2D4, 0xF1D4E242, 0x68DDB3F8, 0x1FDA836E, 0x81BE16CD, 0xF6B9265B, 0x6FB077E1, 0x18B74777,
        0x88085AE6, 0xFF0F6A70, 0x66063BCA, 0x11010B5C, 0x8F659EFF, 0xF862AE69, 0x616BFFD3, 0x166CCF45,
        0xA00AE278, 0xD70DD2EE, 0x4E048354, 0x3903B3C2, 0xA7672661, 0xD06016F7, 0x4969474D, 0x3E6E77DB,
        0xAED16A4A, 0xD9D65ADC, 0x40DF0B66, 0x37D83BF0, 0xA9BCAE53, 0xDEBB9EC5, 0x47B2CF7F, 0x30B5FFE9,
        0xBDBDF21C, 0xCABAC28A, 0x53B39330, 0x24B4A3A6, 0xBAD03605, 0xCDD70693, 0x54DE5729, 0x23D967BF,
        0xB3667A2E, 0xC4614AB8, 0x5D681B02, 0x2A6F2B94, 0xB40BBE37, 0xC30C8EA1, 0x5A05DF1B, 0x2D02EF8D
    )
    cGtHash = 0xFFFFFFFF
    for chr in range(len(str)):
        cGtHash = cGtHash - ((cGtHash & 0x80000000) << 1) >> 8 & 0xFFFFFFFF ^ hashTable[ord(str[chr]) ^ cGtHash & 0xFF]
    return cGtHash

def boGetVerEndian(noe, data):
    # Expects to be a byte form int that's < 256 for version checks
    bLen = len(data) - 1
    if data.startswith(bytes(bLen)):
        noe.setEndian(NOE_BIGENDIAN)
        return "big"
    if data.endswith(bytes(bLen)):
        return "little"
    return None

def boGetTexAptIndex(arc, aptDataOffset, texIndex):
    arc.seek(aptDataOffset)
    while True:
        if arc.readUInt() == texIndex:
            arc.seek(-0x8, 1)
            break

def boSetDummyMdl(mdlList, texList):
    mdl = NoeModel()
    mdl.setModelMaterials(NoeModelMaterials(texList, list()))
    mdlList.append(mdl)

def boSetPalName(texName, palCount, palNum):
    # Used for PSP, Xbox and Xbox 360  -  PS2 has its own
    return "{} (Palette {})".format(texName, palNum + 1) if palCount > 1 else texName

# Known GtID compressed header values in Little Endian
gACTORDICTION = b"\x92\x37\x96\xA8\x73\xC0\xF8\x4D"
gANIMDICTIONA = b"\xDD\xAE\x78\x82\x08\x3C\x88\x4F"
gBNKS         = b"\x00\x00\x00\x57\xE5\x57\x5C\x55"
gCHARACTERDIC = b"\x57\xC3\x41\x63\x03\x9D\x45\x5A"
gMODELS       = b"\x00\x00\x5C\x48\xF2\x0A\x82\x95"
gMOVIEARRAY   = b"\x40\x79\x30\x26\x37\xE5\x92\x95"
gMYDICTIONARY = b"\x15\xEA\x44\x72\xE2\xA8\xF6\x96"
gRCBS         = b"\x00\x00\x00\x2F\x94\x09\xDC\xB0"
gSHAREDBNKS   = b"\xC0\xD7\x61\x81\x3C\x79\x67\xB7"
gTEXDIC       = b"\x00\x00\x3C\x54\x81\xED\xDE\xBC"
gTEXTURE      = b"\x00\x80\x9A\xDD\xB7\x4E\xDF\xBC"
gTEXTUREDICTI = b"\xD5\x64\x20\xE0\xB7\x4E\xDF\xBC"

# Global system variables
boPS2 = 1
boPSP = 2
boXbox = 3
boXbox360 = 4

# Global exception messages
boExcSys = "Couldn't determine system!"
boExcFmt = "Unsupported format! "




#   #####   ##   ##  #######   #####   ##  ##   ######  
#  ##   ##  ##   ##  ##       ##   ##  ## ##   ##       
#  ##       #######  #####    ##       ####     #####   
#  ##   ##  ##   ##  ##       ##   ##  ## ##        ##  
#   #####   ##   ##  #######   #####   ##  ##  ######   


def boChkTxd(data):
    chk = NoeBitStream(data)
    if chk.readBytes(8) in {gTEXDIC, gTEXDIC[::-1]}:
        return True
    return False

def boChkBxv(data):
    chk = NoeBitStream(data)
    chkVer = chk.readBytes(4)
    if chkVer.startswith(b"\x78\xDA"):
        chk = NoeBitStream(boDecZlib(data[:256]), NOE_BIGENDIAN)
        chkVer = chk.readBytes(4)
    chkEndian = boGetVerEndian(chk, chkVer)
    if chkEndian:
        chkVer = boConvToInt(chkVer, chkEndian)
        chkSize = chk.readUInt()
        if 0x14 <= chkVer <= 0x25 and chkSize in {0, chk.getSize()}:
            return True
    return False

def boChkDatStatic(data):
    chk = NoeBitStream(data)
    chkVer = chk.readBytes(4)
    if chkVer.startswith(b"\x78\xDA"):
        chk = NoeBitStream(boDecZlib(data[:256]), NOE_BIGENDIAN)
        chkVer = chk.readBytes(4)
    chkEndian = boGetVerEndian(chk, chkVer)
    if chkEndian:
        chkVer = boConvToInt(chkVer, chkEndian)
        chkSize = chk.readUInt()
        if 0x21 <= chkVer <= 0x3E and chkSize in {0, chk.getSize()}:
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
        if chk.readBytes(4) == chkED02 and chk.readUInt() in {0, chkSize}: # PS2 & Xbox
            return True
        chk.seek(0xB8)
        if chk.readBytes(4) == chkED03[::-1] and chk.readUInt() == 0: # Xbox 360
            return True
        chk.seek(0x1C8)
        if chk.readBytes(4) == chkED03 and chk.readUInt() == chkSize: # PSP (Legends)
            return True
        chk.seek(0x1D8)
        if chk.readBytes(4) == chkED04 and chk.readUInt() == chkSize: # PSP (Dominator)
            return True
        chk.seek(0x2D4)
        if chk.readBytes(4) == chkED04 and chk.readUInt() == chkSize: # PSP (NFS: Shift)
            return True
    return False

def boChkBinFE(data):
    chk = NoeBitStream(data)
    if chk.readBytes(8) in {gMOVIEARRAY, gMOVIEARRAY[::-1]}:
        return True
    return False

def boChkBinFont(data):
    chk = NoeBitStream(data)
    chkSize = chk.getSize()

    fontMagic = chk.readBytes(4)
    if fontMagic in {b"v1.4", b"4.1v"}:
        return True # Revenge, Black
    elif chkSize > 0x2000:
        chk.seek(0x70)
        texOffset = chk.readUInt()
        if texOffset < (chkSize // 2):
            chk.seek(texOffset)
            if chk.readBytes(8) == bytes(4) + b"\x50\x02\x00\x00":
                return True # Dominator (PS2)
    return False

def boChkBinLoad(data):
    chk = NoeBitStream(data)
    txdCount = chk.readUInt64()
    chkAlign = boCalcAlign(txdCount * 0x10 + 8, 0x800)
    if chkAlign < chk.getSize():
        chk.seek(chkAlign)
        if chk.readBytes(8) == gTEXDIC:
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
        dctOrder = (gMODELS,
                    gCHARACTERDIC,
                    gACTORDICTION,
                    gBNKS,
                    gSHAREDBNKS,
                    gRCBS)
        txdOffset = chk.readUInt()
        curChkOffset = chk.tell()
        if txdOffset < chkSize:
            chk.seek(txdOffset)
            if chk.readBytes(8) not in {gTEXDIC, gTEXTURE}:
                return False
        for gtid in dctOrder:
            chk.seek(curChkOffset)
            dctOffset = chk.readUInt()
            curChkOffset = chk.tell()
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
        if chk.readBytes(8) != gTEXDIC:
            return False
        chk.seek(dctOffset)
        if chk.readBytes(8) != gMYDICTIONARY:
            return False
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
    if chk.readBytes(8) == gTEXTUREDICTI:
    # surrounded by gMYDICTIONARY and gANIMDICTIONA 
        return True
    return False

def blkChkBinLevel(data):
    chk = NoeBitStream(data)

    if chk.getSize() > 0x500:
        chkVer = chk.readUInt()
        if chkVer == 0x0A:
            chk.seek(0x2BC) # -> 0x300
        elif chkVer == 0x11:
            chk.seek(0x390) # -> 0x400
        else: # chkVer 0x01 has no textures
            return False
        txdOffset = chk.readUInt()
        chk.seek(txdOffset)
        if chk.readBytes(8) == gTEXDIC:
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
            if chk.readBytes(8) == gTEXTURE:
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
            dctOrder = (gTEXTURE,
                        gMODELS,
                        gCHARACTERDIC,
                        gACTORDICTION,
                        gBNKS,
                        gSHAREDBNKS,
                        gRCBS)
            for gtid in dctOrder:
                dctOffset = chk.readUInt() + hdrOffset
                curChkOffset = chk.tell()
                if dctOffset > chkSize:
                    return False
                chk.seek(dctOffset)
                if chk.readBytes(8) != gtid:
                    return False
                chk.seek(curChkOffset)
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
    if chk.readBytes(8) == gTEXTURE:
        chk.seek(mdlOffset)
        if chk.readBytes(8) == gMODELS:
            return True
    return False




#  ######  #######  ##   ##  ######  ##   ##  ######   #######   ######  
#    ##    ##        ## ##     ##    ##   ##  ##   ##  ##       ##       
#    ##    #####      ###      ##    ##   ##  ######   #####     #####   
#    ##    ##        ## ##     ##    ##   ##  ##   ##  ##            ##  
#    ##    #######  ##   ##    ##     #####   ##   ##  #######  ######   


def boTexGetSystem(tex, texEndian, texOffset):
    tex.seek(texOffset)
    texHeader = tex.readBytes(8)
    if texEndian == "big":
        return boXbox360
    if texHeader.startswith(b"\x01\x00\x04\x00"):
        return boXbox
    if texHeader == bytes(8):
        return boPSP
    if texHeader.startswith(bytes(4)):
        return boPS2
    noesis.doException(boExcSys)

def boTexGetName(tex, texEndian, texOffset):
    # Used by PS2, Xbox, and Xbox 360 only
    texSystem = boTexGetSystem(tex, texEndian, texOffset)

    texSeek = {
        boPS2: 0xA8,
        boXbox: 0x44
    }.get(texSystem, 0x0)
    tex.seek(texOffset + texSeek)
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
    def boPS2Read4(rSize, rData=None):
        # Converts 4-bit data to 8-bit
        # Can be used for both existing data lists and returning new bytearrays
        ret = False
        if rData is None:
            rData = list()
            ret = True
        for byte in range(rSize):
            # Not using Noesis' tex.readBits() because it is very slow
            rByte = tex.readUByte()
            rData.extend((rByte & 0xF, rByte >> 4))
        if ret:
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

    if boDebug:
        print("\nPlayStation 2 texture detected!"
            + "\nTexture name: {}".format(texName.split(" - ")[-1])
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
        noesis.doException(boExcFmt + "{} bpp".format(bitDepth))

    if bitDepth in {4, 8}:
        texData = rapi.imageUntwiddlePS2(texData, wPad, texHeight, 8)
        # Fix-up small textures with weird buffer sizes, post-unswizzle
        if texWidth < 16:
            texData = boTexFixWidth(texData, texWidth, 16, hPad)

        tex.seek(palOffset)
        if palCount == 1:
            palData = boPS2Read32({4: 16, 8: 256}.get(bitDepth))
        else:
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

    if boDebug:
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
        noesis.doException(boExcFmt + "{} bpp".format(bitDepth))
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
        noesis.doException(boExcFmt + hex(texFmt))

    tex.seek(texOffset + 0x80)
    bmpOffset = tex.readUInt() + texOffset
    tex.seek(texOffset + 0xA0)
    palOffset = tex.readUInt() + texOffset

    if boDebug:
        print("\nPlayStation Portable arena texture detected!"
            + "\nTexture name: {}".format(texName.replace(" - ", "/"))
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

    if boDebug:
        print("\nXbox texture detected! ({}er revision)".format("New" if newFmtRev else "Old")
            + "\nTexture name: {}".format(texName.split(" - ")[-1])
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
            curPalOffset = tex.tell()
            tex.seek(palOffset)
            if not tex.readBytes(4) in {b"\x01\x00\x03\x00", b"\x01\x00\x03\xC0"}:
                noesis.doException(boExcFmt + "Invalid palette header!")
            palDataOffset = tex.readUInt() + texOffset

            if boDebug:
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
        noesis.doException(boExcFmt + hex(texFmt))

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

    if boDebug:
        print("\nXbox 360 texture detected!"
            + "\nTexture name: {}".format(texName.split(" - ")[-1])
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
        noesis.doException(boExcFmt + hex(texFmt))

    texList.append(NoeTexture(texName, texWidth, texHeight, texData, texFmt))

def boTexParse(tex, texEndian, texList, texOffset, texName=None, texExtra=None):
    texSystem = boTexGetSystem(tex, texEndian, texOffset)

    if texSystem == boPS2:
        boTexPS2(tex, texList, texOffset, texName, texExtra)
    elif texSystem == boPSP:
        boTexPSP(tex, texList, texOffset)
    elif texSystem == boXbox:
        boTexXbox(tex, texList, texOffset, texName)
    elif texSystem == boXbox360:
        boTexXbox360(tex, texList, texOffset, texName, texExtra)




#   #####   ######    #####   ##   ##  ##  ##   ##  #######   ######  
#  ##   ##  ##   ##  ##   ##  ##   ##  ##  ##   ##  ##       ##       
#  #######  ######   ##       #######  ##   ## ##   #####     #####   
#  ##   ##  ##   ##  ##   ##  ##   ##  ##   #####   ##            ##  
#  ##   ##  ##   ##   #####   ##   ##  ##    ###    #######  ######   


def boArcTxdParse(arc, texList, startOffset=0x0):
    arc.seek(startOffset)
    if arc.readBytes(8) == gTEXDIC[::-1]:
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
        curOffset = arc.tell() + 0x4
        boTexParse(arc, arcEndian, texList, texOffset)
        if boDebug:
            print("Texture {} of {}".format(texNum, texCount))
        arc.seek(curOffset)

def boArcMdlBxv(data, mdlList):
    rapi.processCommands("-texnorepfn")
    arc = NoeBitStream(data)
    matList = list()
    texList = list()

    arcVer = arc.readBytes(4)
    if arcVer.startswith(b"\x78\xDA"):
        arc = NoeBitStream(boDecZlib(data))
        arcVer = arc.readBytes(4)
    arcEndian = boGetVerEndian(arc, arcVer)
    arcVer = boConvToInt(arcVer, arcEndian)

    arc.seek(0x60)
    if arcVer < 0x20:
        texOffset = arc.readUInt()
        boTexParse(arc, arcEndian, texList, texOffset)

    else: # Xbox 360 only
        for tex in range(19):
            texOffset = arc.readUInt()
            if texOffset != 0:
                curTexOffset = arc.tell()
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
                            curPalOffset = arc.tell()
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

    if not boModels:
        boSetDummyMdl(mdlList, texList)
    return True

def boArcMdlDatStatic(data, mdlList):
    rapi.processCommands("-texnorepfn")
    arc = NoeBitStream(data)
    matList = list()
    texList = list()

    arcVer = arc.readBytes(4)
    if arcVer.startswith(b"\x78\xDA"):
        arc = NoeBitStream(boDecZlib(data))
        arcVer = arc.readBytes(4)
    arcEndian = boGetVerEndian(arc, arcVer)
    arcVer = boConvToInt(arcVer, arcEndian)

    if arcVer <= 0x25: # B3 demo
        arc.seek(0x14)
        texCount = arc.readUInt()
    else:
        arc.seek(0x16)
        texCount = arc.readUShort()
    texArrayOffset = arc.readUInt()

    arc.seek(texArrayOffset)
    for tex in range(texCount):
        texOffset = arc.readUInt()
        curTexOffset = arc.tell()
        boTexParse(arc, arcEndian, texList, texOffset)
        arc.seek(curTexOffset)

        if boDebug:
            print("Texture {} of {}".format(tex + 1, texCount))

    if not boModels:
        boSetDummyMdl(mdlList, texList)
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
        curTexOffset = arc.tell()
        boTexParse(arc, arcEndian, texList, texOffset)
        arc.seek(curTexOffset)
    return True

def boArcTexBinFE(data, texList):
    rapi.processCommands("-texnorepfn")
    arc = NoeBitStream(data)

    if arc.readBytes(8) == gMOVIEARRAY:
        arcEndian = "little"
    else:
        arc.setEndian(NOE_BIGENDIAN)
        arcEndian = "big"

    dirCount = arc.readUInt()
    dirOffset = arc.readUInt()

    arc.seek(dirOffset)
    for dir in range(dirCount):
        dirInfoOffset = arc.readUInt()
        curHdrOffset = arc.tell()

        arc.seek(dirInfoOffset)
        dirNameOffset = arc.readUInt()
        dirDataOffset = arc.readUInt()
        arc.seek(dirNameOffset)
        dirName = arc.readString()

        arc.seek(dirDataOffset + 0x4)
        texCount = arc.readUInt()
        if texCount != 0:
            texArrayOffset = arc.readUInt() + dirDataOffset
            aptDataOffset = arc.readUInt() + dirDataOffset
            aptConstOffset = arc.readUInt() + dirDataOffset

            arc.seek(texArrayOffset)
            texOffset = arc.readUInt() + dirDataOffset
            texNameChk = boTexGetName(arc, arcEndian, texOffset)
            boGetTexAptIndex(arc, aptDataOffset, int(texNameChk[11:]) + 1 if texNameChk.startswith("TexturePage") else int(texNameChk))

            for name in range(texCount):
                texNameOffset = arc.readUInt() + aptDataOffset
                texNameIndex = arc.readUInt()
                curAptOffset = arc.tell()
                arc.seek(texNameOffset)
                texName = "{} - {}".format(dirName, arc.readString())

                arc.seek(texArrayOffset)
                for tex in range(texCount):
                    texOffset = arc.readUInt() + dirDataOffset
                    curTexPtrOffset = arc.tell()

                    texNameChk = boTexGetName(arc, arcEndian, texOffset)
                    if texNameChk == str(texNameIndex) or texNameChk[11:] == str(texNameIndex - 1):
                        boTexParse(arc, arcEndian, texList, texOffset, texName=texName)
                        break
                    arc.seek(curTexPtrOffset)

                if boDebug:
                    print("Directory name: {}".format(dirName)
                        + "\nDirectory offset: 0x{:X}".format(dirDataOffset)
                        + "\nApt Data offset: 0x{:X}".format(aptDataOffset)
                        + "\nApt constant file offset: 0x{:X}".format(aptConstOffset)
                        + "\nTexture array offset: 0x{:X}".format(texArrayOffset)
                        + "\nTexture {} of {}".format(texNameIndex, texCount))

                arc.seek(curAptOffset)
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
        curOffset = arc.tell()
        boArcTxdParse(arc, texList, txdOffset)
        if boDebug:
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
    rapi.processCommands("-texnorepfn")
    arc = NoeBitStream(data[16:])

    arenaName = arc.readString()
    arc.seek(0x40)
    texOffset = arc.readUInt()

    if arenaName.lower().endswith(".msh"): # Texture
        boTexPSPArena(arc, texList, 0x0)

    elif texOffset != 0: # Font
        boTexPSPArena(arc, texList, texOffset, fontName=arenaName)

    else: # Frontend
        arc.seek(0x80)
        aptDataOffset = arc.readUInt()
        aptConstOffset = arc.readUInt()
        unkPtrOffset = arc.readUInt()
        texPtrOffset = arc.readUInt()

        arc.seek(texPtrOffset)
        texCount = arc.readUInt()
        if texCount != 0:
            texArrayOffset = arc.readUInt()

            # For various complicated reasons I won't search for the texture name if the first texture index isn't 1
            if arc.readUInt() == 1:
                boGetTexAptIndex(arc, aptDataOffset, 1)
                texNameOffset = arc.readUInt()
                if texNameOffset < texArrayOffset:
                    arc.seek(-0x4, 1)

                    for tex in range(texCount):
                        texNameOffset = arc.readUInt() + aptDataOffset
                        texNameIndex = arc.readUInt()
                        curAptOffset = arc.tell()

                        arc.seek(texNameOffset)
                        texName = arc.readString().replace("/", " - ")
                        arc.seek(texArrayOffset)
                        texOffsetIndex = arc.readUInt()
                        texOffset = arc.readUInt()
                        texArrayOffset = arc.tell()
                        boTexPSPArena(arc, texList, texOffset, texName=texName if texNameIndex == texOffsetIndex else None)

                        if boDebug:
                            print("Texture {} of {} (Index: {})".format(tex + 1, texCount, texOffsetIndex))
                        arc.seek(curAptOffset)
                    return True

            # Fallback without texture names
            arc.seek(texArrayOffset)
            for tex in range(texCount):
                texOffsetIndex = arc.readUInt()
                texOffset = arc.readUInt()
                texArrayOffset = arc.tell()
                boTexPSPArena(arc, texList, texOffset)

                if boDebug:
                    print("Texture {} of {} (Index: {})".format(tex + 1, texCount, texOffsetIndex))
                arc.seek(texArrayOffset)

        if boDebug:
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
    arc = NoeBitStream(rapi.loadIntoByteArray(fileName))

    arc.seek(0xC)
    fileCount = arc.readUInt()
    arcSize = arc.readUInt64()
    nameData = arc.readUInt()
    infoSize = arc.readUInt()
    if arcSize != fileLen:
        arcCount = arc.readUInt()
    else:
        arcIdx = 0
        arcCount = 1
    arc.seek(0x80, 1)
    nameData += arc.tell()

    arc = [arc]
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
        curArcPos = arc[0].tell()

        arc[0].seek(nameOfs)
        fileName = arc[0].readString()
        arc[arcIdx].seek(fileOfs)
        rapi.exportArchiveFile(fileName, arc[arcIdx].readBytes(fileSize))

        if boDebug:
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

def blkArcTexBinGuns(data, texList):
    rapi.processCommands("-texnorepfn")
    arc = NoeBitStream(data)

    txdOffset = arc.readUInt()
    boArcTxdParse(arc, texList, txdOffset)
    return True
