# Todo:
#   * Bones
#   * Remaining mesh type assignments
#       * I've only seen mshAssign 7 once so far in cube.msh
#   * Handle duplicate textures/materials (?)

#   Bully Modding community   
#    discord.gg/Xbrr72EsvK    

# Written by Edness   2022-04-08 - 2022-06-23   v1.4c

AeDebug = False

from inc_noesis import *

def registerNoesisTypes():
    handleTex = noesis.register("Bully: Anniversary Edition Textures", ".tex")
    noesis.setHandlerTypeCheck(handleTex, aeTexCheckType)
    noesis.setHandlerLoadRGBA(handleTex, aeTexLoadTexture)

    handleMsh = noesis.register("Bully: Anniversary Edition Models", ".msh")
    noesis.setHandlerTypeCheck(handleMsh, aeMshCheckType)
    noesis.setHandlerLoadModel(handleMsh, aeMshLoadModel)
    
    if AeDebug:
        noesis.logPopup()
    return True

def aeTexCheckType(data):
    chk = NoeBitStream(data)
    if chk.readUInt() == 0x7:
        chk.seek(0x8)
        if chk.readUInt() == 110:
            return True
    return False

def aeMshCheckType(data):
    chk = NoeBitStream(data)
    if 0x6 <= chk.readUInt() <= 0xC:
        chk.seek(0x8)
        if chk.readUInt() == 1337:
            return True
    return False




class AeParseHeader:
    def __init__(self, hdr):
        self.fileVer = hdr.readUInt()
        self.fileCount = hdr.readUInt() - 1
        hdr.seek(0xC)
        self.infoOffset = hdr.readUInt()

        self.fileFmt = list()
        self.fileOffset = list()
        for i in range(self.fileCount):
            self.fileFmt.append(hdr.readUInt())
            self.fileOffset.append(hdr.readUInt())

        if AeDebug:
            print("\nFile version: 0x{:X}".format(self.fileVer)
                + "\nFile amount: {}".format(self.fileCount)
                + "\nFile info offset: 0x{:X}".format(self.infoOffset))

def aeReadString(noe):
    return noeStrFromBytes(noe.readBytes(noe.readUInt()))

def aeTxtParse(txt):
    # Converts strings to a functional Python dict or list

    tryOrder = (int, float, str)
    def tryStep(name):
        for step in tryOrder:
            try:
                step(name)
                return step
            except:
                continue

    def fixEval(txt):
        def fixList(lst):
            if lst[0] == len(lst) - 1:
                lst = lst[1:]
            for itm in lst:
                if type(itm) is list:
                    itm = fixList(itm)
                elif type(itm) is dict:
                    itm = fixDict(itm)
            return lst

        def fixDict(dct):
            for i in dct:
                if type(dct[i]) is list:
                    dct[i] = fixList(dct[i])
                elif type(dct[i]) is dict:
                    dct[i] = fixDict(dct[i])
            return dct

        if type(txt) is list:
            txt = fixList(txt)
        elif type(txt) is dict:
            txt = fixDict(txt)
        return txt

    txt = txt.replace("\\", "\\\\")
    txt = txt.replace("\t", "")
    txt = txt.replace("\n", "")

    txt = txt.split(",")
    for i in range(len(txt)):
        ln = txt[i].split("=")
        for j in range(len(ln)):
            lnMain = ln[j]
            skipStart = 0
            skipEnd = len(ln[j])
            while lnMain.startswith(("{", "[")):
                lnMain = lnMain[1:]
                skipStart += 1
            while lnMain.endswith(("}", "]")):
                lnMain = lnMain[:-1]
                skipEnd -= 1
            if tryStep(lnMain) is str:
                if not lnMain.startswith(("\"", "\'")) and not lnMain.endswith(("\"", "\'")):
                    lnMain = "\"{}\"".format(lnMain)
                    if lnMain == "\"\"":
                        lnMain = "None"
                    elif lnMain.lower() == "\"true\"":
                        lnMain = "True"
                    elif lnMain.lower() == "\"false\"":
                        lnMain = "False"
            ln[j] = ln[j][:skipStart] + lnMain + ln[j][skipEnd:]
        txt[i] = ":".join(ln)
    txt = eval(",".join(txt))
    return fixEval(txt)

def aeTxtDecrypt(txt):
    # Python reimplementation of Bartlomiej Duda's  Bully_XML_Tool.cpp  script
    # see  BullyAE_encryption.py  for the standalone version

    aeKey = "6Ev2GlK1sWoCa5MfQ0pj43DH8Rzi9UnX"
    aeHash = 0x0CEB538D

    encSize = len(txt)
    decSize = (5 * encSize >> 3)
    decData = list(bytes(decSize + 1))

    case = 0
    bufIdx = 0
    for i in range(encSize):
        char = aeKey.index(txt[i])

        next = {
            4: char << 7,
            5: char << 6,
            6: char << 5,
            7: char << 4
        }.get(case, 0)

        char = {
            0: char << 3,
            1: char << 2,
            2: char << 1,
            3: char,
            4: char >> 1,
            5: char >> 2,
            6: char >> 3,
            7: char >> 4
        }.get(case)

        decData[bufIdx] |= char
        decData[bufIdx + 1] |= next

        if (case + 5) % 8 < case:
            bufIdx += 1
        case = (case + 5) % 8

    xor = 18
    for i in range(decSize):
        aeHash = 0xAB * (aeHash % 0xB1) - 2 * (aeHash // 0xB1) & 0xFFFFFFFF
        decData[i] = ((decData[i] ^ xor) + aeHash) & 0xFF
        xor += 6

    return noeStrFromBytes(bytes(decData[:-1]))

def aeTexLoadTexture(data, texList, extName=None):
    tex = NoeBitStream(data)
    hdr = AeParseHeader(tex)
    rapi.processCommands("-texnorepfn")

    tex.seek(hdr.infoOffset)
    hdrInfo = aeTxtParse(aeReadString(tex))

    texCompression = hdrInfo.get("compressondisk")
    intPath = hdrInfo.get("importfilepath")
    intName = os.path.splitext(os.path.basename(intPath))[0]
    if extName is None:
        extName = os.path.splitext(os.path.basename(rapi.getInputName()))[0]
    if extName != intName and intName != "":
        if extName.lower() == intName.lower():
            texName = intName
        else:
            texName = "{} ({})".format(extName, intName)
    else:
        texName = extName

    for i in range(hdr.fileCount):
        tex.seek(hdr.fileOffset[i])
        # partially taken, rewritten & improved upon AuraShadow's
        #  tex_BullyAnniversaryEdition_Android_iOS_tex.py  script

        texFmt = tex.readUInt()  # == hdr.fileFmt[i]  ...most of the times, at least
        texWidth = tex.readUInt()
        texHeight = tex.readUInt()
        texMips = tex.readUInt()
        texSize = tex.readUInt()
        if texCompression == True:
            decSize = tex.readUInt()
            texData = rapi.decompInflate(tex.readBytes(texSize - 4), decSize)
        else:
            texData = tex.readBytes(texSize)

        if AeDebug:
            print("\nTexture dimensions: {} x {}".format(texWidth, texHeight)
                + "\nTexture mip maps: {}".format(texMips)
                + "\nTexture offset: 0x{:X}".format(hdr.fileOffset[i])
                + "\nTexture size{}: 0x{:X}".format(" (compressed)" if texCompression else "", texSize)
                +("\nTexture size (decompressed): 0x{:X}".format(decSize) if texCompression else "")
                + "\nTexture format: 0x{:X} ({})".format(texFmt, {0: "RGBA32", 1: "RGB24", 3: "BGR16",
                                                                  4: "ABGR16", 5: "DXT1", 6: "DXT3",
                                                                  7: "DXT5", 8: "A8", 9: "PVRTC2"}.get(texFmt))
                + "\nFile format: 0x{:X}".format(hdr.fileFmt[i])
                + "\nTexture {} of {}".format(i + 1, hdr.fileCount))

        # DATA TYPES
        #  0  =  RGBA-8888
        #  1  =  RGB-888
        #  3  =  BGR-565
        #  4  =  ABGR-4444
        #  5  =  DXT1 / BC1
        #  6  =  DXT3 / BC2
        #  7  =  DXT5 / BC3
        #  8  =  A-8
        #  9  =  PVRTC2

        texType = noesis.NOESISTEX_RGBA32  # texFmt == 0, also used for 3, 4, 8, and 9
        if texFmt == 1:
            texType = noesis.NOESISTEX_RGB24
        elif texFmt == 3:
            texData = rapi.imageDecodeRaw(texData, texWidth, texHeight, "B5G6R5")
        elif texFmt == 4:
            texData = rapi.imageDecodeRaw(texData, texWidth, texHeight, "A4B4G4R4")
        elif texFmt == 5:
            texType = noesis.NOESISTEX_DXT1
        elif texFmt == 6:
            texType = noesis.NOESISTEX_DXT3
        elif texFmt == 7:
            texType = noesis.NOESISTEX_DXT5
        elif texFmt == 8:
            texData = rapi.imageDecodeRaw(texData, texWidth, texHeight, "A8")
        elif texFmt == 9:
            texData = rapi.imageDecodePVRTC(texData, texWidth, texHeight, 4, noesis.PVRTC_DECODE_PVRTC2_ROTATE_BLOCK_PAL)
        elif texFmt:
            noesis.doException("Unhandled texture format {}".format(texFmt))
        texList.append(NoeTexture(texName if hdr.fileCount == 1 else "{} (Texture {})".format(texName, i + 1), texWidth, texHeight, texData, texType))

    if AeDebug:
        if intPath:
            print("\nTexture internal name: {}".format(intPath))
    return hdr.fileCount, texName

def aeMshLoadModel(data, mdlList):
    msh = NoeBitStream(data)
    hdr = AeParseHeader(msh)
    rapi.processCommands("-rotate 90 0 0")
    rapi.rpgCreateContext()

    # DATA TYPES
    #  1  =  Two Floats
    #  2  =  Three Floats
    #  8  =  ???   bone weight/idx?
    #  9  =  ???   bone weight/idx?
    # 10  =  ???   vertex colors?
    # 11  =  Normalised 12(11?)-bit (2048)

    def mshDataParse(mshData=[]):
        if mshType == 1:
            mshData.extend(msh.readBytes(8))
        elif mshType == 2:
            mshData.extend(msh.readBytes(12))
        elif 8 <= mshType <= 10:
            msh.seek(0x4, 1)
        elif mshType == 11:
            mshData.extend(noePack("<f", msh.readShort() / 2048))
            mshData.extend(noePack("<f", msh.readShort() / 2048))
        else:
            noesis.doException("Unhandled mesh data type {}".format(mshType))

    def mshTexLoad(idx):
        texName = texNames[idx]
        texPath = basePath + texName + ".tex"
        try:
            with open(texPath, "rb") as tex:
                texCount, texName = aeTexLoadTexture(tex.read(), texList, texName)
            print("Successfully loaded {}.tex".format(texName))
            return texName + ("" if texCount < 2 else " (Texture 2)")
        except Exception as aeExc:
            print("Failed loading {}.tex: {}".format(texName, aeExc))
            return ""

    basePath = os.path.split(rapi.getInputName())[0] + "\\"
    animList = list()
    boneList = list()
    matList = list()
    texList = list()

    msh.seek(hdr.infoOffset)
    mtlCount = msh.readUInt()
    mtlNames = [aeReadString(msh) for i in range(mtlCount)]

    boneCount = msh.readUInt()
    for i in range(boneCount):
        boneName = aeReadString(msh)
        boneMat = NoeMat43.fromBytes(msh.readBytes(48))
        boneIdx = msh.readInt()
        #boneList.append(NoeBone(boneIdx, boneName, boneMat))

    msh.seek({  # the size changes depending on hdr.fileVer
        0x6: 0x1,
        0x7: 0x2,
        0x8: 0x3,
        0x9: 0x4,
        0xA: 0x4,
        0xB: 0x4,  # x2 shorts; first one being a 0x0100(?)
        0xC: 0x5,  # similar as above, but one extra byte?
        # the \x00\x01 terminator is also used after every mshInfo block
    }.get(hdr.fileVer), 1)

    # 10 floats back to back; first 6 are for the bounding box of the
    # mesh, next 3 are the middle point, unsure what the last float is.
    #mshBounds = noeUnpack("<ffffff", msh.readBytes(24))
    #mshCenter = noeUnpack("<fff", msh.readBytes(12))
    #tmpDummy = noeUnpack("<f", msh.readBytes(4))
    tmpDummy = noeUnpack("<ffffffffff", msh.readBytes(40))

    # Seems to always be the same following dict:
    #  { "physical(physicalmaterial)": None,
    #    "setups(orderedarray<collisionshapesetup>)": [] }
    hdrInfo = aeTxtParse(aeReadString(msh))

    # An empty list in all models except for the following 9 vehicles:
    # 70wagon, cargreen, dlvtruck, domestic, foreign, limo, policecar taxicab, truck
    boneInfo = aeTxtParse(aeReadString(msh))

    # Unsure
    nodeCount = msh.readUInt()
    for i in range(nodeCount):
        nodeName = aeReadString(msh)
        nodeBones = noeUnpack("<iiii", msh.readBytes(16))

    # Unsure
    animCount = msh.readUInt()
    for i in range(animCount):
        animName = aeReadString(msh)
        animBones = noeUnpack("<iiii", msh.readBytes(16))
        animMat = NoeMat43.fromBytes(msh.readBytes(48))
        #animList.append(NoeAnim())

    for i in range(hdr.fileCount):
        msh.seek(hdr.fileOffset[i])
        mshCount = msh.readUInt()

        if AeDebug:
            print("\nMesh offset: 0x{:X}".format(hdr.fileOffset[i])
                + "\nMesh format: 0x{:X}".format(hdr.fileFmt[i]))

        if not mshCount:
            continue
        for j in range(mshCount):
            mshName = aeReadString(msh)
            msh.seek(0x2, 1)
            vertCount = msh.readUInt()
            # most of the times varying amounts of null, occasionally floats
            while not vertCount or vertCount > 0xFFFF:
                vertCount = msh.readUInt()
            faceCount = msh.readUInt()

            triData = msh.readBytes(faceCount * 2)

            mshInfoCount = msh.readUInt()
            mshInfo = list()
            for k in range(mshInfoCount):
                mshInfo.append([msh.readUInt(), msh.readUInt()])
                msh.seek(0x2, 1)

            if AeDebug:
                print("\nMesh name: {}".format(mshName)
                    + "\nFaces offset: 0x{:X}".format(msh.tell() - mshInfoCount * 10 - 4 - faceCount * 2)  # lol
                    + "\nFaces amount: {} ({})".format(faceCount, faceCount // 3)
                    + "\nVertices offset: 0x{:X}".format(msh.tell())
                    + "\nVertices amount: {}".format(vertCount)
                    + "\nBlock layout: {}".format(", ".join([str(k[::-1]) for k in mshInfo]))
                    + "\nMesh {} of {}\n".format(j + 1, mshCount))

            # DATA ASSIGNMENTS
            #  0  =  Vertices
            #  1  =  
            #  2  =  
            #  3  =  Colors?
            #  4  =  UVs
            #  5  =  Normals?
            #  6  =  
            #  7  =  

            #clrData = list()
            #nrmData = list()
            vertData = list()
            uvData = [list() for k in mshInfo if k[1] == 4]
            uvIdx = 0
            for k in range(vertCount):
                for mshType, mshAssign in mshInfo:
                    if mshAssign == 0:
                        mshDataParse(vertData)
                    #elif mshAssign == 3:
                    #    mshDataParse(clrData)
                    elif mshAssign == 4:
                        mshDataParse(uvData[uvIdx % len(uvData)])
                        uvIdx += 1
                    #elif mshAssign == 5:
                    #    mshDataParse(nrmData)
                    elif 1 <= mshAssign <= 7:
                        mshDataParse()
                    else:
                        noesis.doException("Unhandled mesh data assignment {}".format(mshAssign))

            rapi.rpgBindPositionBuffer(bytes(vertData), noesis.RPGEODATA_FLOAT, 12)
            if uvData:
                for k in range(len(uvData)): 
                    rapi.rpgBindUVXBuffer(bytes(uvData[k]), noesis.RPGEODATA_FLOAT, 8, k, vertCount)
            else:
                rapi.rpgBindUV1Buffer(None, noesis.RPGEODATA_FLOAT, 8)
            #if clrData:
            #    rapi.rpgBindColorBuffer(bytes(clrData), noesis.RPGEODATA_BYTE, 3, 3)
            #if nrmData:
            #    rapi.rpgBindNormalBuffer(bytes(nrmData), noesis.RPGEODATA_FLOAT, 12)

            mshSubCount = msh.readUInt()
            for k in range(mshSubCount):
                mshSubStart = msh.readUInt() * 2
                mshSubSize = msh.readUInt()
                mtlIdx = msh.readUInt()
                msh.seek(0x4, 1)

                mtlPath = basePath + mtlNames[mtlIdx] + ".mtl"
                try:
                    with open(mtlPath, "rb") as mtl:
                        assert(mtl.read(0x2) == b"Wx")
                        mtlInfo = aeTxtParse(aeTxtDecrypt(mtl.read().decode()))
                        print("Successfully loaded {}.mtl".format(mtlNames[mtlIdx]))
                except Exception as aeExc:
                    print("Failed loading {}.mtl: {}".format(mtlNames[mtlIdx], aeExc))
                    mtlInfo = None

                if AeDebug:
                    print("\nSubmesh face start: {} ({})".format(mshSubStart // 2, mshSubStart // 6)
                        + "\nSubmesh face amount: {} ({})".format(mshSubSize, mshSubSize // 3)
                        + "\nMaterial index: {}".format(mtlIdx)
                        + "\nMaterial name: {}".format(mtlNames[mtlIdx])
                        +("\nTexture type: {}".format(mtlInfo.get("effect(effect)")) if mtlInfo else "")
                        +("\nTexture list: {}".format(", ".join(mtlInfo.get("textures(orderedarray<texture2d>)"))) if mtlInfo else "")
                        + "\nSubmesh {} of {}".format(k + 1, mshSubCount))

                rapi.rpgSetMaterial(mtlNames[mtlIdx])
                rapi.rpgSetName("{}-{} {} {}".format(j, mtlIdx, mshName, mtlNames[mtlIdx].split("mat_", 1).pop()))

                if mtlInfo is not None:
                    texType = mtlInfo.get("effect(effect)")
                    texNames = mtlInfo.get("textures(orderedarray<texture2d>)")

                    mat = NoeMaterial(mtlNames[mtlIdx], mshTexLoad(0))
                    texIdx = 1
                    if "normal" in texType:
                        # is it  setBumpTexture  or  setNormalTexture?
                        mat.setBumpTexture(mshTexLoad(1))
                        texIdx += 1
                    if "spec" in texType:
                        mat.setSpecularTexture(mshTexLoad(texIdx))
                    if mtlInfo.get("doublesided(bool)") == True:
                        mat.setFlags(noesis.NMATFLAG_TWOSIDED)
                    #if mtlInfo.get("alphatest(bool)") is not None:
                    #    mat.setAlphaTest(mtlInfo.get("alphatest(bool)"))
                    matList.append(mat)

                rapi.rpgCommitTriangles(triData[mshSubStart:][:mshSubSize * 2], noesis.RPGEODATA_USHORT, mshSubSize, noesis.RPGEO_TRIANGLE)

        #rapi.setPreviewOption("setAngOfs", "0 -90 90")
        mdl = rapi.rpgConstructModel()
        mdl.setModelMaterials(NoeModelMaterials(texList, matList))
        mdl.setBones(boneList)
        mdlList.append(mdl)
    return True
