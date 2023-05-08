# Written by Edness   v1.0b   2023-05-07 - 2023-05-08

# Textures require the following plugins to be installed
#  * lib_zq_nintendo_tex   (Author: Zheneq)
#  * fmt_wii_tpl           (Author: Zheneq)

# Models will automatically load textures from a .TXD if
# the .DFF and .TXD names are identical. Otherwise it'll
# search for any supported image format in the folder.

# Brought to you by the Bully Modding community
#             discord.gg/Xbrr72EsvK            

# TODO:
#   Bones, animations
#   Some potential material issues? (moped.dff)
#   Better day/night vertex color toggle
#   Model default rotation check, if possible

from inc_noesis import *

try:
    import lib_zq_nintendo_tex
    import fmt_wii_tpl as tpl
    BseTextures = True
except ImportError:
    BseTextures = False

BseDebug = False
BseNightColors = False  # Toggle to use night-time vertex color lighting

def registerNoesisTypes():
    handleDff = noesis.register("Bully: Scholarship Edition [Wii]", ".dff")
    noesis.setHandlerTypeCheck(handleDff, bseChkDff)
    noesis.setHandlerLoadModel(handleDff, bseMdlDff)

    if BseTextures:
        handleTxd = noesis.register("Bully: Scholarship Edition [Wii]", ".txd")
        noesis.setHandlerTypeCheck(handleTxd, bseChkTxd)
        noesis.setHandlerLoadRGBA(handleTxd, bseTexTxd)

    if BseDebug:
        noesis.logPopup()
    return True

BseTexSuffix = "(Scaled to Alpha)"
BseExcDataFmt = "Unhandled data format 0x{:02X}!"

def bseChkDff(data):
    chk = NoeBitStream(data, NOE_BIGENDIAN)
    if chk.readBytes(0x4) == b"CLMP" and chk.readUInt() == 0x1 and chk.readUInt() <= chk.getSize():
        return True  # Can't do == for the size check because of 0x800 alignment
    return False

def bseChkTxd(data):
    chk = NoeBitStream(data, NOE_BIGENDIAN)
    if chk.readBytes(0x4) == b"TDCT" and chk.readUInt() == 0x1 and chk.readUInt() <= chk.getSize():
        return True  # Same as above for not using == in the size integer check
    return False

def bseGetPtrs(noe):
    noe.seek(0xC)
    ptrOffset = noe.readUInt()
    if noe.readUInt() != ptrOffset:
        noesis.doException("Pointer list offset mismatch!")
    ptrCount = noe.readUInt()
    noe.seek(ptrOffset)
    return [noe.readUInt() for x in range(ptrCount)]

def bseReadPtr(noe, ptrList):
    ptrOffset = noe.getOffset()
    ptr = noe.readUInt()
    if not ptr:
        return 0
    if ptrOffset not in ptrList:
        noesis.doException("Attempted to read an unindexed pointer!")
    ptrList.remove(ptrOffset)
    return ptr

class BseMdlParseChunk:
    def __init__(self, mdl, dataInfo, mdlInfo):
        if dataInfo == mdlInfo:
            self.offset = mdlInfo
            self.count = 0
            return

        mdl.seek(dataInfo)
        self.offset = mdl.readUInt() + mdlInfo
        self.count = mdl.readUShort()
        self.fmt = mdl.readUByte()
        self.elems = mdl.readUByte()

        if self.offset == mdlInfo:
            return

        mdl.seek(self.offset)
        if self.fmt & 0xF0 == 0x30:  # shorts, usually 14-bit for verts/normals and 11-bit for uvs
            self.stride = self.elems * 0x4
            self.data = list()
            dataBits = (1 << (self.fmt & 0xF)) - 1
            for i in range(self.count):
                dataTmp = [x / dataBits for x in noeUnpack(">{}h".format(self.elems), mdl.readBytes(self.elems * 0x2))]
                self.data.append(noePack(">{}f".format(self.elems), *dataTmp))

        elif self.fmt == 0x20:  # bytes (1 x BGR-888) padded?
            if self.elems != 3:
                noesis.doException("Unhandled data format 0x20 element size!")
            self.stride = 0x4
            self.data = [rapi.imageDecodeRaw(mdl.readBytes(0x4), 1, 1, "B8G8R8P8") for x in range(self.count)]

        elif self.fmt == 0x40:  # floats
            self.stride = self.elems * 0x4
            self.data = [mdl.readBytes(self.stride) for x in range(self.count)]

        elif self.fmt == 0x50:  # bytes (2 x BGR-565)
            if self.elems != 4:
                noesis.doException("Unhandled data format 0x20 element size!")
            self.stride = 0x8
            self.data = [rapi.imageDecodeRaw(rapi.swapEndianArray(mdl.readBytes(self.elems), 2), 2, 1, "B5G6R5") for x in range(self.count)]

        else:
            noesis.doException(BseExcDataFmt.format(self.fmt))

def bseMdlHeader(data):
    mdl = NoeBitStream(data, NOE_BIGENDIAN)
    if mdl.readUInt() != 0x007B7960:
        noesis.doException("Invalid header identifier!")

    mdl.seek(0x10)
    mdl.seek(mdl.readUInt())
    if BseDebug:
        print(mdl.readString())

def bseMdlMain(data, texNames):
    rapi.rpgClearBufferBinds()
    mdl = NoeBitStream(data, NOE_BIGENDIAN)
    if mdl.readUInt() != 0x00B749E0:
        noesis.doException("Invalid mesh identifier!")

    def readIdx(dataFmt):
        if not dataFmt:
            return -1
        return mdl.readUShort() if dataFmt == 0b11 else mdl.readUByte()

    # these are usually chained back to back, but just in case
    mdl.seek(0x10)
    hdrOffset = mdl.readUInt()
    # should have a size check, empty models would cut off here
    mdl.seek(hdrOffset)
    mdlInfo = mdl.readUInt()
    nameOffset = mdl.readUInt()
    mdl.seek(nameOffset)
    mdlName = mdl.readString()
    if BseDebug:
        print(mdlName)

    mdl.seek(mdlInfo)
    vtxInfo = mdl.readUInt() + mdlInfo
    clrInfo = mdl.readUInt() + mdlInfo
    uvsInfo = mdl.readUInt() + mdlInfo
    nrmInfo = mdl.readUInt() + mdlInfo
    idxInfo = mdl.readUInt() + mdlInfo

    vtx = BseMdlParseChunk(mdl, vtxInfo, mdlInfo)
    clr = BseMdlParseChunk(mdl, clrInfo, mdlInfo)
    uvs = BseMdlParseChunk(mdl, uvsInfo, mdlInfo)
    nrm = BseMdlParseChunk(mdl, nrmInfo, mdlInfo)

    mdl.seek(idxInfo)
    idxOffset = mdl.readUInt() + mdlInfo  # 1st submesh offset
    idxUnk = mdl.readUInt() + mdlInfo  # goes to after the header
    idxCount = mdl.readUShort() - 2

    #print("{} vtxCount,   {} nrmCount,   {} clrCount,   {} uvCount".format(vtx.count, nrm.count, clr.count, uvs.count))
    matIdx = 0
    subIdx = 0
    for i in range(idxCount):
        unkReloc = list()
        vtxReloc = list()
        nrmReloc = list()
        clrReloc = list()
        uvsReloc = list()
        mdl.seek(idxInfo + 0x30)
        idxLayout = mdl.readUInt()
        #print(" ".join(["{:02b}".format(faceLayout >> x * 2 & 0x3) for x in range(8)][::-1]))

        if idxLayout & ~0x3FFF:  # 0xFFFFC000
            noesis.doException("Unhandled vertex element layout {:04X}!".format(idxLayout))

        idxFmt = [idxLayout >> x & 0x3 for x in range(0, 14, 2)]
        unk1Fmt, vtxFmt, nrmFmt, clrFmtDay, clrFmtNight, uvsFmt, unk2Fmt = idxFmt

        #unk1Fmt     = idxLayout >>  0 & 0x3
        #vertFmt     = idxLayout >>  2 & 0x3
        #nrmFmt      = idxLayout >>  4 & 0x3
        #clrFmtDay   = idxLayout >>  6 & 0x3
        #clrFmtNight = idxLayout >>  8 & 0x3
        #uvFmt       = idxLayout >> 10 & 0x3
        #unk2Fmt     = idxLayout >> 12 & 0x3

        mdl.seek(idxInfo + 0x34 + i * 0x10)
        idxOffset = mdl.readUInt() + mdlInfo
        idxSize = mdl.readUInt()
        idxMaterial = mdl.readUByte()
        #if idxMaterial not in {0x1, 0x5}:
        #    noesis.doException("Unhandled submesh material parameter!")
        if idxOffset == mdlInfo:
            continue
        mdl.seek(idxOffset)
        idxFmt = mdl.readUByte()
        if idxFmt != 0x90:
            noesis.doException(BseExcDataFmt.format(idxFmt))
        idxElems = mdl.readUShort()

        for j in range(idxElems):
            #faceData.append(readIdx(vertCount))
            #if not clrCount: mdl.readUByte()

            readIdx(unk1Fmt)

            vtxReloc.extend(vtx.data[readIdx(vtxFmt)])
            nrmIdx = readIdx(nrmFmt)
            if nrmIdx != -1 and nrm.offset != mdlInfo:
                nrmReloc.extend(nrm.data[nrmIdx])
            clrIdxDay = readIdx(clrFmtDay)
            if not BseNightColors and clrIdxDay != -1:
                clrReloc.extend(clr.data[clrIdxDay])
            clrIdxNight = readIdx(clrFmtNight)
            if BseNightColors and clrIdxNight != -1:
                clrReloc.extend(clr.data[clrIdxNight])
            uvsIdx = readIdx(uvsFmt)
            if uvsIdx != -1:
                uvsReloc.extend(uvs.data[uvsIdx])

            readIdx(unk2Fmt)

            #if not vertReloc[vertIdx]:
            #    vertReloc[vertIdx].append(faceRead)
            #    faceReloc.append(vertIdx)
            #elif vertReloc[vertIdx] != faceRead:
            #    for rel in vertReloc
            #else:
            #    faceReloc.append(vertIdx)

        vtxReloc = bytes(vtxReloc)
        nrmReloc = bytes(nrmReloc)
        clrReloc = bytes(clrReloc)
        uvsReloc = bytes(uvsReloc)
        rapi.rpgSetName("_".join((mdlName, "{:03}".format(subIdx))) if subIdx else mdlName)
        #rapi.rpgSetMaterial(texNames[subIdx] if subIdx < len(texNames) else "")
        rapi.rpgSetMaterial(texNames[matIdx])
        if idxMaterial == 0x1:  # this isn't exactly correct but it works in 99% cases
            matIdx += 1
        subIdx += 1

        #faceData = noePack(">{}h".format(len(faceReloc)), *faceData)
        rapi.rpgBindPositionBuffer(vtxReloc, noesis.RPGEODATA_FLOAT, vtx.stride)
        if nrmReloc:
            rapi.rpgBindNormalBuffer(nrmReloc, noesis.RPGEODATA_FLOAT, nrm.stride)
            #rapi.rpgBindNormalBufferOfs(nrmReloc, noesis.RPGEODATA_SHORT, nrmSize, nrmOffset - vertOffset)
        if clrReloc:
            rapi.rpgBindColorBufferOfs(clrReloc, noesis.RPGEODATA_UBYTE, clr.stride, 0x0 if not BseNightColors else 0x4, 4)
        if uvsReloc:
            rapi.rpgBindUV1Buffer(uvsReloc, noesis.RPGEODATA_FLOAT, uvs.stride)
        rapi.rpgCommitTriangles(None, noesis.RPGEODATA_USHORT, idxElems, noesis.RPGEO_TRIANGLE)

    if not nrm.count or nrm.offset == mdlInfo:
        rapi.rpgSmoothNormals()

    return clrFmtNight

def bseMdlDff(data, mdlList):
    rapi.rpgCreateContext()
    rapi.rpgSetOption(noesis.RPGOPT_BIGENDIAN, True)
    rapi.rpgSetOption(noesis.RPGOPT_TRIWINDBACKWARD, True)
    rapi.setPreviewOption("setAngOfs", "0 -90 90")  # 0 -90 90 # 0 -120 145 # 0 60 -145 #
    rapi.processCommands("-rotate 90 0 0")
    mdl = NoeBitStream(data, NOE_BIGENDIAN)

    ptrList = bseGetPtrs(mdl)
    def readPtr():
        return bseReadPtr(mdl, ptrList)

    boneList = list()
    matList = list()
    texList = list()

    mdl.seek(0x20)
    mdlHeader = readPtr()
    # Repeated twice;  mdlHeader  has two pointers back to here too
    # Intended to be something like TDCT's  nextOffset/prevOffset?

    mdl.seek(mdlHeader + 0x8)
    blkOffset = readPtr()

    texLoaded = dict()
    txdFile = os.path.splitext(rapi.getInputName())[0] + ".txd"
    if BseTextures and os.path.exists(txdFile):
        txdData = rapi.loadIntoByteArray(txdFile)
        if bseChkTxd(txdData):
            bseTexTxd(txdData, texList)
            for idx, tex in enumerate(texList):
                if tex.name not in texLoaded:
                    if not tex.name.endswith(BseTexSuffix):
                        texLoaded[tex.name] = idx
                else:
                    noesis.doException("Duplicate texture names!")

    # Originally I thought the section pointers weren't consistent, might be redone
    def bseMdlRecurse(blkOffset, **kwArgs):
        mdl.seek(blkOffset)
        mdlHeader = mdl.readUInt()

        if mdlHeader == 0x1 << 24:
            if BseDebug:
                print("Reading 1 {:08X}".format(blkOffset))
            boneOffset = readPtr()
            mdl.seek(blkOffset + 0x18)
            mdlOffset = readPtr()

            bseMdlRecurse(boneOffset, boneIdx=0)  # -> 4
            bseMdlRecurse(mdlOffset)  # -> 2

        elif mdlHeader == 0x2 << 24:
            if BseDebug:
                print("Reading 2 {:08X}".format(blkOffset))
            nextOffset = readPtr()
            prevOffset = readPtr()
            boneOffset = readPtr()
            mdlOffset = readPtr()

            #bseMdlRecurse(boneOffset) # -> 4, partial?
            bseMdlRecurse(mdlOffset)   # -> 3
            bseMdlRecurse(nextOffset)  # -> 2

        elif mdlHeader == 0x3 << 24:
            texNames = list()
            texPtrOffset = readPtr()
            texCount = mdl.readUInt()
            for i in range(texCount):
                mdl.seek(texPtrOffset + 0xC * i)
                texNameOffset = readPtr()
                matParam = mdl.readUByte()  # is loaded in RAM?
                matColor = NoeVec4([mdl.readUByte() / 0xFF for x in range(4)])

                mdl.seek(texNameOffset)
                texName = mdl.readString()
                texNames.append(texName)
                mat = NoeMaterial(texName, texName)
                mat.setFlags(noesis.NMATFLAG_TWOSIDED)
                mat.setDiffuseColor(NoeVec4((1, 1, 1, matColor[3])))
                #mat.setDiffuseColor(matColor)  # only Alpha works?
                matList.append(mat)
                #matList.append(NoeMaterial(texName, texName))
            if BseDebug:
                print("Reading 3 {:08X}".format(blkOffset), ", ".join(texNames))

            #mdl.seek(blkOffset + 0x3C)
            #mdlBias = NoeVec3.fromBytes(mdl.readBytes(0xC), NOE_BIGENDIAN)
            #mdlScale = NoeVec3.fromBytes(mdl.readBytes(0xC), NOE_BIGENDIAN)
            #rapi.rpgSetPosScaleBias(mdlScale, mdlBias)

            # These are treated as individual files like the textures, but unlike
            # those being plain TPLs with the identifier  0x0020AF30,  I haven't
            # found any source for these identifiers  0x007B7960  and  0x00B749E0
            # being a standard Wii data format.
            mdl.seek(blkOffset + 0x64)
            hdrSize = mdl.readUInt()
            hdrOffset = readPtr()  # -> 0x7B7960
            mdlSize = mdl.readUInt()
            mdlOffset = readPtr()  # -> 0xB749E0
            unkSize = mdl.readUInt()
            unkOffset = readPtr()  # anim?

            mdl.seek(hdrOffset)
            hdrData = mdl.readBytes(hdrSize)
            if BseDebug:
                print("Reading hdr {:08X} ({:08X} bytes)".format(hdrOffset, hdrSize), end=" ")
            bseMdlHeader(hdrData)

            mdl.seek(mdlOffset)
            mdlData = mdl.readBytes(mdlSize)
            if BseDebug:
                print("Reading mdl {:08X} ({:08X} bytes)".format(mdlOffset, mdlSize), end=" ")
            bseMdlMain(mdlData, texNames)
            #for i in range(2):
            #    bseMdlMain(mdlData, texNames, bool(i))
            #    msh = rapi.rpgConstructModel()
            #    msh.setModelMaterials(NoeModelMaterials(texList, matList))
            #    mdlList.append(msh)

            mdl.seek(unkOffset)
            unkData = mdl.readBytes(unkSize)
            if BseDebug:
                print("Reading unk {:08X} ({:08X} bytes)".format(unkOffset, unkSize))

        elif mdlHeader == 0x4 << 24:
            mdl.seek(blkOffset + 0x14)
            boneLeft = readPtr()
            boneRight = readPtr()
            mdl.seek(blkOffset + 0x20)
            # The rightmost values of each matrix are uninitialised values,
            # all of which are dropped in the conversion to a 4x3 matrix.
            boneMat = NoeMat44.fromBytes(mdl.readBytes(0x40), NOE_BIGENDIAN).toMat43() \
                    * NoeMat44.fromBytes(mdl.readBytes(0x40), NOE_BIGENDIAN).toMat43()
            mdl.seek(blkOffset + 0xAC)
            boneName = mdl.readString()
            boneIdx = kwArgs.get("boneIdx")
            if boneIdx is None:
                boneIdx = boneList[-1].index + 1
            boneList.append(NoeBone(boneIdx, boneName, boneMat, kwArgs.get("bonePrev")))
            if BseDebug:
                print("Reading 4 {:08X}".format(blkOffset), boneName)
            if boneLeft:
                bseMdlRecurse(boneLeft, bonePrev=boneName)
            if boneRight:
                bseMdlRecurse(boneRight, bonePrev=boneName)

        elif mdlHeader != 0xFF:  # end block?
            if BseDebug:
                print("Reading Fail {:08X}".format(blkOffset))
            noesis.doException("Unexpected model identifier {:02X}!".format(mdlHeader))

    bseMdlRecurse(blkOffset)

    #mdl = NoeModel()
    #rapi.rpgOptimize()
    #rapi.rpgSmoothNormals()
    mdl = rapi.rpgConstructModel()
    mdl.setModelMaterials(NoeModelMaterials(texList, matList))
    #mdl.setBones(boneList)  # broken currently
    mdlList.append(mdl)
    return True

def bseTexTxd(data, texList):
    rapi.processCommands("-texnorepfn")
    tex = NoeBitStream(data, NOE_BIGENDIAN)

    ptrList = bseGetPtrs(tex)
    def readPtr():
        return bseReadPtr(tex, ptrList)

    tex.seek(0x26)
    texCount = tex.readUShort()
    nextOffset = readPtr()
    prevOffset = readPtr()

    for i in range(texCount):
        texOffset = nextOffset

        # 0x8C bytes for each entry
        tex.setEndian(NOE_BIGENDIAN)
        tex.seek(texOffset)
        nextOffset = readPtr()
        prevOffset = readPtr()
        texName = tex.readString()
        # 0x20 bytes for the name, but 0x60 byte buffer total?

        tex.seek(texOffset + 0x80)
        tplOffset = readPtr()

        tex.setEndian(NOE_LITTLEENDIAN)
        tex.seek(texOffset + 0x88)
        tplSize = tex.readUInt()

        tex.seek(tplOffset)
        tplData = tex.readBytes(tplSize)
        # For some reason this keeps returning None
        #texData = rapi.loadTexByHandler(tplData, ".tpl")

        if tpl.noepyCheckType(tplData):
            tmpList = list()
            tpl.noepyLoadRGBA(tplData, tmpList)

            if len(tmpList) == 2:
                if set(tmpList[0].pixelData[3::4]) != {0xFF}:
                    noesis.doException("Unexpected alpha channel data!")

                alphaData = tmpList[1].pixelData
                rgbSize = (tmpList[0].width, tmpList[0].height)
                alphaSize = (tmpList[1].width, tmpList[1].height)
                if rgbSize != alphaSize:
                    # Alternate texture that preserves the original Alpha data by scaling RGB data
                    rgbData = rapi.imageResample(tmpList[0].pixelData, rgbSize[0], rgbSize[1], alphaSize[0], alphaSize[1])
                    tmpList[1].name = " ".join((texName, BseTexSuffix))
                    rgbData[3::4] = alphaData[0::4]  # use R channel
                    tmpList[1].pixelData = rgbData
                    texList.append(tmpList[1])

                    # Chained unpacks don't work like this in Python 3.2.1 :weary:
                    #alphaData = rapi.imageResample(tmpList[1].pixelData, *alphaSize, *rgbSize)
                    alphaData = rapi.imageResample(alphaData, alphaSize[0], alphaSize[1], rgbSize[0], rgbSize[1])
                tmpList[0].pixelData[3::4] = alphaData[0::4]  # use R channel

                # The alpha mask RGB has very slight deviations from compression
                # artifacts.  Might be worth calculating the greyscale average?
                #if tmpList[1].pixelData[0::4] != tmpList[1].pixelData[1::4]\
                #or tmpList[1].pixelData[1::4] != tmpList[1].pixelData[2::4]:
                #    noesis.doException("Unexpected alpha mask data!")

            elif len(tmpList) != 1:
                noesis.doException("Unexpected texture amount!")

            tmpList[0].name = texName
            texList.append(tmpList[0])

        else:
            noesis.doException("Failed to load texture!")

        if BseDebug:
            print("\nWii texture detected!"
                + "\nTexture name: {}".format(texName)
                + "\nTexture header offset: 0x{:X}".format(texOffset)
                + "\nTexture data offset: 0x{:X}".format(tplOffset)
                + "\nTexture data size: 0x{:X}".format(tplSize)
                + "\nTexture color dimensions: {} x {}".format(texList[-1].width, texList[-1].height)
                +("\nTexture alpha dimensions: {} x {}".format(*alphaSize) if len(tmpList) == 2 else "")
                + "\nTexture {} of {}".format(i + 1, texCount))

    return True
