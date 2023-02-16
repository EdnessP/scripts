# PS2 Memory Card save icon Noesis plugin
# Written by Edness   v1.1dev   2022-07-19 - 2022-10-27

# INFO!  This plugin has been published incomplete as-is for now! It is
# missing proper vertex animation support, due to Noesis itself currently
# not fully supporting it.

# Model importing is also largely complete, but hasn't been tested, so
# uncomment noesis.setHandlerWriteModel and noesis.setTypeExportOptions
# and alter the  meshFmt  variable on line 174 at your own risk.

from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("PS2 Memory Card Save Icon", ".icn;.ico")  # most common extensions, rename to one of these or register
    noesis.setHandlerTypeCheck(handle, iconCheckType)                   # your own extension if your selected icon doesn't fit these
    noesis.setHandlerLoadModel(handle, iconLoadModel)
    #noesis.setHandlerWriteModel(handle, iconWriteModel)
    #noesis.setTypeExportOptions(handle, "-rotate 180 0 0")
    return True

def iconCheckType(data):
    chk = NoeBitStream(data)
    return chk.readUInt() == 0x10000

def iconLoadModel(data, mdlList):
    #rapi.setPreviewOption("setAngOfs", "0 -90 115")
    rapi.setPreviewOption("setAnimSpeed", "2")
    rapi.processCommands("-rotate 180 0 0")  # -vertclr
    rapi.rpgCreateContext()
    mdl = NoeBitStream(data)
    matList = list()
    texList = list()

    biosWarnings = ""
    # Stores warnings for various checks the PS2 does, based on research
    # I've done on the function at  002376C0  in the Europe v02.00 BIOS.

    def iconReadPos(count):
        return b"".join([noePack("f", mdl.readShort() / 4096) for i in range(count)])

    mdl.seek(0x4)
    morphCount = mdl.readUInt()
    meshFmt = mdl.readUInt()
    if mdl.readFloat() < 0:
        biosWarnings += "\n   The culling factor is less than 0!"
    vertCount = mdl.readUInt()

    if morphCount > 8:
        biosWarnings += "\n   The amount of animation morph frames is greater than 8!"
    vertCheck = {1: 1800, 2: 1650, 4: 1500, 6: 1350, 8: 1200}.get(morphCount)
    if vertCheck is None:
        biosWarnings += "\n   Invalid amount of animated morph frames! (Must be 1, 2, 4, 6, 8)"
    elif vertCount > vertCheck:
        biosWarnings += "\n   There can't be more than {} vertices with {} morph frame{}!".format(vertCheck, morphCount, "s" if morphCount > 1 else "")

    vertData = [list() for i in range(morphCount)]
    nrmData = list()
    uvData = list()
    clrData = list()
    #unkData = list()  # mdl.seek(0x2, 1) -> unkData.extend(iconReadPos(1)) ?
    for i in range(vertCount):
        for j in range(morphCount):
            vertData[j].extend(iconReadPos(3))
            mdl.seek(0x2, 1)
        nrmData.extend(iconReadPos(3))
        mdl.seek(0x2, 1)
        uvData.extend(iconReadPos(2))
        clrData.extend(mdl.readBytes(4))

    #clrAlpha = clrData[3::4]
    #if sum(clrAlpha) <= 0x80 * len(clrAlpha):
    #    for idx, alpha in enumerate(clrAlpha):
    #        alpha *= 2
    #        if alpha == 0x100: alpha -= 1
    #        clrData[idx * 4 + 3] = alpha
    #clrData[0] = 10
    #for i in clrData: print("{:02X}".format(i), end=" ")

    if not rapi.noesisIsExporting():
        clrData[3::4] = b"\xFF" * len(clrData[3::4])

    mdl.seek(0x10, 1)  # 0x4 = total length in seconds (int), 0x8 = playback speed (float)
    animCount = mdl.readUInt()
    animData = [list() for i in range(animCount)]
    for i in range(animCount):
        animIdx = mdl.readUInt()
        animForms = mdl.readUInt()
        for j in range(animForms):
            animData[i].append([mdl.readFloat(), mdl.readFloat()])

    for frame in animData: print(frame)

    if meshFmt & 0b0100:
        texName, matName = "texture0", "material0"
        if meshFmt & 0b1000:  # RLE decompression
            texData = list()
            texSize = mdl.readUInt() + mdl.getOffset()
            while mdl.getOffset() < texSize:
                rleType = mdl.readUShort()
                texData.extend(mdl.readBytes(2) * rleType if rleType < 0x8000 else mdl.readBytes(2 * (0x10000 - rleType)))
            texData = bytes(texData)
        else:
            texData = mdl.readBytes(0x8000)

        texData = rapi.imageDecodeRaw(texData, 128, 128, "R5G5B5P1")
        tex = NoeTexture(texName, 128, 128, texData)
        tex.setFlags(noesis.NTEXFLAG_WRAP_CLAMP)  # PS2-accurate wrapping
        texList.append(tex)

        rapi.rpgSetName("mesh0")
        rapi.rpgSetMaterial(matName)
        #mat = NoeMaterial(matName, texName)
        matList.append(NoeMaterial(matName, texName))

    if morphCount == 1:
        rapi.rpgBindPositionBuffer(bytes(vertData[0]), noesis.RPGEODATA_FLOAT, 12)
    else:
        timeLine = dict()
        for idx, frame in enumerate(animData):
            for time, morph in frame:
                if morph != 0.0:
                    #if time in timeLine and timeLine[time][1] > 0.0:
                    #    noesis.doException("Cannot assign multiple morphs at the same time!")
                    timeLine[time] = (idx, morph)  # round(morph, 5)
        timeLine = sorted(timeLine.items())
        print("Timeline:", timeLine)
        rapi.rpgBindPositionBuffer(bytes(vertData[timeLine.pop(0)[1][0]]), noesis.RPGEODATA_FLOAT, 12)
        if meshFmt & 0b0001 and not rapi.noesisIsExporting():
            rapi.rpgBindNormalBuffer(bytes(nrmData), noesis.RPGEODATA_FLOAT, 12)
        for time, (idx, morph) in timeLine:
            rapi.rpgFeedMorphTargetPositions(bytes(vertData[idx]), noesis.RPGEODATA_FLOAT, 12)
            rapi.rpgCommitMorphFrame(vertCount)
        rapi.rpgCommitMorphFrameSet()

    if meshFmt & 0b0001 and not rapi.noesisIsExporting():
        rapi.rpgBindNormalBuffer(bytes(nrmData), noesis.RPGEODATA_FLOAT, 12)
    rapi.rpgBindColorBuffer(bytes(clrData), noesis.RPGEODATA_UBYTE, 4, 4)
    rapi.rpgBindUV1Buffer(bytes(uvData), noesis.RPGEODATA_FLOAT, 8)
    rapi.rpgCommitTriangles(None, noesis.RPGEODATA_USHORT, vertCount, noesis.RPGEO_TRIANGLE)

    mdl = rapi.rpgConstructModel()
    mdl.setModelMaterials(NoeModelMaterials(texList, matList))
    mdlList.append(mdl)

    if biosWarnings:
        biosWarnings = "This icon may not load on a PS2 without first modifying the BIOS!\nThe following problems were detected with this icon:\n" + biosWarnings
        print("\n" + biosWarnings + "\n")
        noesis.messagePrompt(biosWarnings)
    return True

def iconWriteModel(icon, mdl):
    mesh = icon.meshes[0]  # select mesh via NoeWin?

    texData = None
    if icon.modelMats is not None:
        tex = rapi.loadExternalTex(icon.modelMats.matList[0].texName)
        if tex is not None and tex.pixelType == noesis.NOESISTEX_RGBA32:
            texData = tex.pixelData if tex.width == 128 and tex.height == 128 else rapi.imageResample(tex.pixelData, tex.width, tex.height, 128, 128)
            texData = rapi.imageEncodeRaw(texData, 128, 128, "R5G5B5P1")

    def iconWriteClr(coord):  # convert alpha byte to 0x00 - 0x80 range?
        return b"".join([round(pos * 255).to_bytes(0x1, "little") for pos in coord])

    def iconWritePos(coord):
        return b"".join([noePack("h", round(pos * 4096)) for pos in coord])

    def iconWriteRLE(int):
        return int.to_bytes(2, "little")

    def iconReadTex():
        return texData[texOffset * 2:texOffset * 2 + 2]

    meshFmt = 0b0011  # change to 0b0111 to import textures
                      # change to 0b1111 to compress it too

    mdl.writeUInt(0x10000)
    mdl.writeUInt(len(mesh.morphList) + 1)
    mdl.writeUInt(meshFmt)  # mesh params, controlled by NoeWin?
    mdl.writeFloat(0)  # culling threshold, same as above?
    mdl.writeUInt(len(mesh.indices))

    for vtx in mesh.indices:
        mdl.writeBytes(iconWritePos(mesh.positions[vtx]))
        mdl.writeUShort(0)
        for morph in mesh.morphList:
            mdl.writeBytes(iconWritePos(morph.positions[vtx]))
            mdl.writeUShort(0)
        mdl.writeBytes(iconWritePos(mesh.normals[vtx]))
        mdl.writeUShort(0)
        mdl.writeBytes(iconWritePos(mesh.uvs[vtx][:2]))
        mdl.writeBytes(iconWriteClr(mesh.colors[vtx]))

    mdl.writeUInt(1)
    mdl.writeUInt(1)  # anim length, precalc minimum from morph timeline, ->NoeWin
    mdl.writeFloat(1)  # playback speed, ->NoeWin
    mdl.writeUInt(0)

    # anim data here, this below is a placeholder
    mdl.writeUInt64(1)
    mdl.writeUInt64(1)
    mdl.writeFloat(1)

    if meshFmt & 0b0100 and texData is not None:
        if meshFmt & 0b1000:  # RLE compression
            texOffset = 0
            texDataCmp = list()
            while texOffset < 0x4000:
                clr = iconReadTex()
                texOffset += 1
                texRead = 1
                if iconReadTex() == clr:
                    while iconReadTex() == clr:
                        texOffset += 1
                        texRead += 1
                    texDataCmp.extend(iconWriteRLE(texRead))
                    texDataCmp.extend(clr)
                else:
                    texDataCopy = list()
                    while iconReadTex() != clr:
                        texDataCopy.extend(clr)
                        clr = iconReadTex()
                        texOffset += 1
                        texRead += 1
                    texOffset -= 1
                    texRead -= 1
                    texDataCmp.extend(iconWriteRLE(0x10000 - texRead))
                    texDataCmp.extend(texDataCopy)
            mdl.writeUInt(len(texDataCmp))
            texData = bytes(texDataCmp)
        mdl.writeBytes(texData)
    return True
