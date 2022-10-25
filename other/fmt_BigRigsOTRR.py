# Written by Edness   v1.0   2022-10-25

USE_MAT_COLOR = False  # Material colors, these seem to not be used by the game

from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("Big Rigs: Over the Road Racing", ".sco")
    noesis.setHandlerTypeCheck(handle, brCheckSco)
    noesis.setHandlerLoadModel(handle, brLoadModelSco)
    return True

UV_PLACEHOLDER = b"\xFF" * 16

def brCheckSco(data):
    return data.lstrip().startswith(b"[ObjectBegin]")

def brCheckMat(data):
    return data.lstrip().startswith(b"[MaterialBegin]")

def brReadCoord(ln):
    ln = ln.split()
    return noePack("fff", float(ln[0]), float(ln[1]), float(ln[2]))

def brReadEntry(ln):
    return ln.split("=", 1).pop().strip()

def brLoadTexture(texName, texList):
    #texLoad = rapi.loadExternalTex(os.path.join(os.path.split(rapi.getInputName())[0], os.path.splitext(texName)[0]))
    texLoad = rapi.loadExternalTex(texName)
    if texLoad is not None:
        texLoad.name = texName
        for tex in texList:
            if tex.name == texName:
                break
        else:
            texList.append(texLoad)
        return texName

def brLoadModelSco(data, mdlList):  #, runFirst=True
    #rapi.setPreviewOption("setAngOfs", "0 -60 100")
    #rapi.processCommands("-flipax 3 -rotate 0 5 0")  # -flipax 1 -rotate 0 -5 0 # -flipax 3 -rotate 0 5 0 #
    rapi.processCommands("-flipax 1")  # -fulltexpath
    rapi.rpgCreateContext()
    matList = list()
    texList = list()


    #####   MATERIAL READ   #####
    matPath = os.path.splitext(rapi.getInputName())[0].split("_", -1).pop(0) + ".mat"  # No in-file material filename, seems consistent
    if not os.path.exists(matPath): matPath = os.path.join(os.path.split(rapi.getInputName())[0], "Room.mat")  # "Fallback" for levels

    if os.path.exists(matPath):
        matData = rapi.loadIntoByteArray(matPath)

        if brCheckMat(matData):
            for ln in noeStrFromBytes(matData).splitlines():
                if "[MaterialBegin]" in ln:
                    #mat = NoeMaterial()  # Can't set material name afterwards with native methods; assuming Name is always 1st
                    #getFlags1, getFlags2 = 0, 0
                    matColor = [1.0, 1.0, 1.0, 1.0]
                    matRead = True

                elif "[MaterialEnd]" in ln:
                    #mat.setFlags(getFlags1)
                    #mat.setFlags2(getFlags2)
                    mat.setDiffuseColor(NoeVec4(matColor))
                    matList.append(mat)
                    matRead = False

                elif matRead:
                    if ln.startswith("Name"):
                        mat = NoeMaterial(brReadEntry(ln), None)

                    elif ln.startswith("Texture"):
                        #getFlags1 |= noesis.NMATFLAG_DIFFUSE_UV1
                        mat.setTexture(brLoadTexture(brReadEntry(ln), texList))

                    elif ln.startswith("AlphaMask"):
                        #getFlags2 |= noesis.NMATFLAG2_OPACITY_UV1
                        mat.setOpacityTexture(brLoadTexture(brReadEntry(ln), texList))

                    elif ln.startswith("NormalMap"):
                        #getFlags1 |= noesis.NMATFLAG_NORMAL_UV1
                        mat.setNormalTexture(brLoadTexture(brReadEntry(ln), texList))

                    elif ln.startswith("EnvMap"):
                        mat.setEnvTexture(brLoadTexture(brReadEntry(ln), texList))

                    #elif ln.startswith("EnvPower"):
                    #    brReadEntry(ln)  # ???

                    elif ln.startswith("Color24"):
                        if USE_MAT_COLOR:
                            clrData = brReadEntry(ln).split()
                            for idx in range(3):  # Not sure if this is used?
                                matColor[idx] = int(clrData[idx]) / 255

                    elif ln.startswith("Opacity"):
                        clrData = brReadEntry(ln)
                        matColor[3] = int(clrData) / 255

                    #elif ln.startswith("Flags"):
                    #    mat.setFlags()  # brReadEntry(ln)

                    elif ln.strip():
                        print("Unimplemented (MatLocal):", ln)

                elif ln.strip():
                    print("Unimplemented (MatGlobal):", ln)


    #####   MODEL READ   #####
    for ln in noeStrFromBytes(data).splitlines():
        if "[ObjectBegin]" in ln:
            vertData = list()
            faceData = dict()
            vertCount = False
            faceCount = False
            mdlRead = True

        elif "[ObjectEnd]" in ln:
            rapi.rpgBindPositionBuffer(b"".join(vertData), noesis.RPGEODATA_FLOAT, 12)
            rapi.rpgBindUV1Buffer(b"".join(uvData).replace(UV_PLACEHOLDER, bytes(16)), noesis.RPGEODATA_DOUBLE, 16)
            for mat in faceData:
                rapi.rpgSetMaterial(mat)
                rapi.rpgSetName("_".join((mdlName, mat)))
                rapi.rpgCommitTriangles(b"".join(faceData[mat]), noesis.RPGEODATA_INT, len(faceData[mat]), noesis.RPGEO_TRIANGLE)

            mdl = rapi.rpgConstructModel()
            mdl.setModelMaterials(NoeModelMaterials(texList, matList))
            mdlList.append(mdl)
            mdlRead = False

        elif mdlRead:
            if vertCount:
                vertCount -= 1
                vertData.append(brReadCoord(ln))
                #if not vertCount:
                #    rapi.rpgBindPositionBuffer(b"".join(vertData), noesis.RPGEODATA_FLOAT, 12)

            elif faceCount:
                faceCount -= 1
                ln = ln.split()
                faceLine = int(ln.pop(0))  # Always 3 lol
                faces = [0 for f in range(faceLine)]
                for f in range(faceLine):
                    faces[f] = int(ln.pop(0))

                matName = ln.pop(0)
                if matName not in faceData:
                    faceData[matName] = list()

                for f in range(faceLine):
                    #uvData[faces[v]] = noePack("<dd", float(ln.pop(0)), float(ln.pop(0)))
                    uv = noePack("dd", float(ln.pop(0)), float(ln.pop(0)))
                    if uvData[faces[f]] == UV_PLACEHOLDER:
                        uvData[faces[f]] = uv
                    elif uvData[faces[f]] != uv:
                        #print("UV mismatch - uvidx:{}, existing:{}, current:{}".format(faces[v], noeUnpack("<dd", uvData[faces[v]]), noeUnpack("<dd", uv)))
                        for rel in uvReloc[faces[f]]:
                            if uvData[rel] == uv:
                                faces[f] = rel
                                break
                        else:
                            uvReloc[faces[f]].append(len(uvData))
                            vertData.append(vertData[faces[f]])
                            faces[f] = len(uvData)
                            uvData.append(uv)

                    faceData[matName].append(faces[f].to_bytes(4, "little"))

                #if not faceCount:
                #   # moved to [ObjectEnd] handler

            elif ln.startswith("Name"):
                mdlName = brReadEntry(ln)

            elif ln.startswith("CentralPoint"):
                mdlCenter = brReadCoord(brReadEntry(ln))

            elif ln.startswith("Verts"):
                vertCount = int(brReadEntry(ln))
                uvReloc = [list() for v in range(vertCount)]
                uvData = [UV_PLACEHOLDER for v in range(vertCount)]

            elif ln.startswith("Faces"):
                faceCount = int(brReadEntry(ln))

            elif ln.strip():
                print("Unimplemented (MdlLocal):", ln)

        elif ln.strip():
            print("Unimplemented (MdlGlobal):", ln)

    #if runFirst:  # Used it for model render ultrashots whenever batch load wasn't cooperating
    #    brLoadModelSco(rapi.loadIntoByteArray(r"Y:\BigRigsInstall\2003-10-23\Carz\Data\Cars\Z350\Z350_W1.sco"), mdlList, False)
    #    brLoadModelSco(rapi.loadIntoByteArray(r"Y:\BigRigsInstall\2003-10-23\Carz\Data\Cars\Z350\Z350_W2.sco"), mdlList, False)
    #    brLoadModelSco(rapi.loadIntoByteArray(r"Y:\BigRigsInstall\2003-10-23\Carz\Data\Cars\Z350\Z350_W3.sco"), mdlList, False)
    #    brLoadModelSco(rapi.loadIntoByteArray(r"Y:\BigRigsInstall\2003-10-23\Carz\Data\Cars\Z350\Z350_W4.sco"), mdlList, False)

    return True
