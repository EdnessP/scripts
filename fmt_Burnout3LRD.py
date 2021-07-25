# Written by Edness
boVer = "v0.5"
boDate = "2021-07-25"
boDebug = 0

from inc_noesis import *
import noewin

def registerNoesisTypes():
    handleBxv = noesis.register("Burnout 3T, BLeg, BRev, BDom",".bgv;.btv")
    noesis.setHandlerTypeCheck(handleBxv,boToolCheckTypeBxv)
    noesis.setHandlerLoadRGBA(handleBxv,boToolGetTexBxv)
    #noesis.setHandlerLoadModel(handleBxv,boToolGetMdlBxv)

    handleBinFE = noesis.register("Burnout Rev, BDom, Black FE",".bin")
    noesis.setHandlerTypeCheck(handleBinFE,boToolCheckTypeBinFE)
    noesis.setHandlerLoadRGBA(handleBinFE,boToolGetTexBinFE)

    handleBinOther = noesis.register("Burnout 3T, BLeg, BRev, BDom Font & Loadsc",".bin")
    noesis.setHandlerTypeCheck(handleBinOther,boToolCheckTypeBinOther)
    noesis.setHandlerLoadRGBA(handleBinOther,boToolGetTexBinOther)

    handleTxd = noesis.register("Burnout 3T, BLeg, BRev, BDom",".txd")
    noesis.setHandlerTypeCheck(handleTxd,boToolCheckTypeTxd)
    noesis.setHandlerLoadRGBA(handleTxd,boToolGetTexTxd)

    handleDatEnv = noesis.register("Burnout 3T, BLeg, BRev, BDom Enviro",".dat")
    noesis.setHandlerTypeCheck(handleDatEnv,boToolCheckTypeDatEnviro)
    noesis.setHandlerLoadRGBA(handleDatEnv,boToolGetTexDatEnviro)

    handleDatStat = noesis.register("Burnout 3T, BLeg, BRev, BDom Static",".dat")
    noesis.setHandlerTypeCheck(handleDatStat,boToolCheckTypeDatStatic)
    noesis.setHandlerLoadRGBA(handleDatStat,boToolGetTexDatStatic)
    #noesis.setHandlerLoadModel(handleDatStat,boToolGetMdlDatStatic)

    handleArena = noesis.register("Burnout Dom PSP",".arena")
    noesis.setHandlerTypeCheck(handleArena,boToolCheckTypeArena)
    noesis.setHandlerLoadRGBA(handleArena,boToolGetTexArena)

    if boDebug:
        noesis.logPopup()
    return 1

def boToolCheckTypeBxv(data):
    bs = NoeBitStream(data)
    fileVer = bs.readUInt()
    if fileVer >= 0x14 and fileVer <= 0x1F or fileVer == 0x25000000:
        return 1 # B3 - Dom
    cmpCheck = int(hex(fileVer)[-4:],16)
    if cmpCheck == 0xDA78 or cmpCheck == 0x9C78 or cmpCheck == 0x5C78 or cmpCheck == 0x0178:
        return 1 # Rev360 zlib'd, though only 78DA should be used
    return 0

def boToolCheckTypeBinFE(data):
    bs = NoeBitStream(data)
    magic = bs.readUInt64()
    if magic == 0x9592E53726307940 or magic == 0x4079302637E59295: # MOVIEARRAY GtID
        return 1
    return 0

def boToolCheckTypeBinOther(data):
    bs = NoeBitStream(data)
    texCount = bs.readUInt64()
    fontMagic = int(hex(texCount)[-8:],16)
    #print(hex(texCount),hex(fontMagic))
    if texCount < 60 and texCount != 0: # B3/BL loadscrn, unreliable?
        return 1
    elif fontMagic == 0x76312E34 or fontMagic == 0x342E3176: # v1.4
        return 1 # Rev font file
    #bs.seek(0)
    #bs.readString()
    bs.seek(0x70) # Dom PS2 font file
    texOffset = bs.readUInt()
    if texOffset < len(data)//2:
        bs.seek(texOffset)
        if bs.readUInt64() == 0x000025000000000:
            return 1
    return 0

def boToolCheckTypeArena(data):
    bs = NoeBitStream(data)
    if bs.readUInt() == 0x6F6B654E: # Neko
        return 1
    return 0

def boToolCheckTypeTxd(data):
    bs = NoeBitStream(data)
    magic = bs.readUInt64()
    if magic == 0xBCDEED81543C0000 or magic == 0x00003C5481EDDEBC: # TEXDIC GtID
        return 1
    return 0

def boToolCheckTypeDatStatic(data):
    bs = NoeBitStream(data)
    fileVer = bs.readUInt()
    fileSize = bs.readUInt()
    if fileVer >= 0x21 and fileVer <= 0x3E or fileVer == 0x3C000000:
        if fileSize == len(data) or fileSize == 0:
            return 1 # B3 - Dom
    cmpCheck = int(hex(fileVer)[-4:],16)
    #print(hex(fileVer),hex(cmpCheck))
    if cmpCheck == 0xDA78 or cmpCheck == 0x9C78 or cmpCheck == 0x5C78 or cmpCheck == 0x0178:
        return 1 # Rev360 zlib'd
    return 0

def boToolCheckTypeDatEnviro(data):
    bs = NoeBitStream(data)
    bs.seek(0xA8)
    someId = bs.readUInt()
    fileSize = bs.readUInt()
    if (fileSize == len(data) or fileSize == 0) and someId == 0x45440002: # ps2 & xbox
        return 1
    bs.seek(0xB8)
    if bs.readUInt() == 0x03004445 and bs.readUInt() == 0: # 360 rev
        return 1
    bs.seek(0x1C8)
    if bs.readUInt() == 0x45440003 and bs.readUInt() == len(data): # psp leg
        return 1
    bs.seek(0x1D8)
    if bs.readUInt() == 0x45440004 and bs.readUInt() == len(data): # psp dom
        return 1
    return 0

# FUNCTION LIST FOR KEEPNG TRACK
#   boToolPlatformCheck
#   boToolSetSystem
#   boToolLockSystem
#   boToolCloseWindow
#   boToolSetup
#   boToolDecZlib
#   boToolPadAlign
#   boToolGetFirstTexIndex
#   boToolGetTexTxd
#   boToolTxdParse
#   boToolGetTexBinFE
#   boToolGetTexBinOther
#   boToolGetTexArena
#   boToolGetTexArenaAlt
#   boToolGetTexDatEnviro
#   boToolGetTexDatStatic
#   boToolGetTexBxv
#   boToolTexParse
#   boToolPS2Tex
#   boToolPS2AlphaFix
#   boToolCvt4bitTo8bit
#   boToolPSPTex
#   boToolPSPArenaTex
#   boToolXboxTex
#   boTool360Tex
#   boToolPalCount

def boToolPlatformCheck():
    boWindow = noewin.NoeUserWindow("Burnout Tool","BOToolWindowClass",406,253) # 400x224?
    boWindowRect = noewin.getNoesisWindowRect()
    boWindow.x = boWindowRect[0]+384
    boWindow.y = boWindowRect[1]+256
    if boWindow.createWindow():
        boWindow.setFont("Segoe UI",12) # linux/wine will default to Arial
        boWindow.createStatic("Please select which platform this file is from:",16,16,250,16)
        boWindow.createCheckBox("PlayStation 2",32,40,90,16,boToolSetSystem)
        boWindow.createCheckBox("PlayStation Portable",32,58,130,16,boToolSetSystem)
        boWindow.createCheckBox("Xbox",32,76,45,16,boToolSetSystem)
        boWindow.createCheckBox("Xbox 360",32,94,72,16,boToolSetSystem)
        boWindow.createCheckBox("Remember your current choice?",16,120,195,16,boToolLockSystem)
        boWindow.createButton("OK",288,96,96,32,boToolCloseWindow)
        boWindow.createStatic("(Until Noesis is restarted or reloaded with Alt+T+R.)",32,138,336,16)
        boWindow.createStatic("—————————————————————————————————",2,152,396,16)
        boWindow.createStatic("This plugin is brought to you by the Burnout Modding community.\ndiscord.gg/8zxbb4x",16,167,368,32)
        boWindow.createStatic(boVer+"  –  Written by Edness  –  ("+boDate+")",32,200,336,16)
        global boSystem
        try: boSystem
        except NameError: pass
        else:
            boSystem += 100
            boToolSetSystem(boWindow,boSystem,boSystem,0)
        boWindow.doModal()

def boToolSetSystem(boWindow,cID,wParam,lParam):
    global boSystem
    checkBoxPS2 = boWindow.getControlById(101)
    checkBoxPSP = boWindow.getControlById(102)
    checkBoxXbx = boWindow.getControlById(103)
    checkBox360 = boWindow.getControlById(104)
    # tfw no radio buttons
    if cID == 101:
        boSystem = 1
        checkBoxPS2.setChecked(1)
        checkBoxPSP.setChecked(0)
        checkBoxXbx.setChecked(0)
        checkBox360.setChecked(0)
    elif cID == 102:
        boSystem = 2
        checkBoxPS2.setChecked(0)
        checkBoxPSP.setChecked(1)
        checkBoxXbx.setChecked(0)
        checkBox360.setChecked(0)
    elif cID == 103:
        boSystem = 3
        checkBoxPS2.setChecked(0)
        checkBoxPSP.setChecked(0)
        checkBoxXbx.setChecked(1)
        checkBox360.setChecked(0)
    elif cID == 104:
        boSystem = 4
        checkBoxPS2.setChecked(0)
        checkBoxPSP.setChecked(0)
        checkBoxXbx.setChecked(0)
        checkBox360.setChecked(1)
    return

def boToolLockSystem(boWindow,cID,wParam,lParam):
    global boSysLock
    #print(cID)
    checkBoxLck = boWindow.getControlById(cID)
    checkBoxLck.setChecked(1 if not checkBoxLck.isChecked() else 0)
    if not checkBoxLck.isChecked():
        boSysLock = 0
    else:
        boSysLock = 1
    return

def boToolCloseWindow(boWindow,cID,wParam,lParam):
    boWindow.closeWindow()
    return

def boToolSetup(data):
    global boSystem
    global boSysLock
    rapi.processCommands("-nofslwr -texnorepfn")
    try: boSysLock
    except NameError:
        boToolPlatformCheck()
    else:
        if boSysLock == 0:
            boToolPlatformCheck()
    bs = NoeBitStream(data,NOE_LITTLEENDIAN if boSystem < 4 else NOE_BIGENDIAN)
    return bs

def boToolDecZlib(bs,data):
    bs.seek(0)
    decData = bytearray()
    cmpData = bs.readBytes(len(data))
    decSize = rapi.getInflatedSize(cmpData)
    #print(hex(decSize))
    decData += rapi.decompInflate(cmpData,decSize)
    bs = NoeBitStream(decData,NOE_BIGENDIAN) # assume 360 only
    return bs

def boToolPadAlign(bs,padSize,padFrom):
    if padFrom % padSize != 0:
        bs.seek((padFrom//padSize+1)*padSize)

def boToolGetFirstTexIndex(bs,data,aptDataOffset,texList):
    bs.seek(aptDataOffset)
    aptData = bs.readString()
    boToolPadAlign(bs,4,bs.tell())
    texNameIndex = 0
    while texNameIndex != 1: # may be unreliable? (especially for psp .arenas)
        texNameIndex = bs.readUInt()
        if texNameIndex == 1:
            bs.seek(-8,1)

def boToolGetTexTxd(data,texList):
    bs = boToolSetup(data)
    boToolTxdParse(bs,data,0,texList)
    return 1

def boToolTxdParse(bs,data,startOffset,texList):
    bs.seek(startOffset + 8)
    texCount = bs.readUInt()
    offStart = bs.readUInt()
    offStart += startOffset
    bs.seek(offStart)
    for a in range(texCount):
        texNum = bs.readUInt64()
        texOffset = bs.readUInt()
        texOffset += startOffset
        bs.seek(4,1)
        curOffset = bs.tell()
        if boDebug:
            print("DEBUG1:",hex(curOffset),hex(texOffset),texNum,"/",texCount)
        boToolTexParse(bs,data,texOffset,0,texList,0)
        bs.seek(curOffset)

def boToolGetTexBinFE(data,texList):
    bs = boToolSetup(data)

    bs.seek(8)
    dirCount = bs.readUInt()
    dirOffset = bs.readUInt()
    bs.seek(dirOffset)
    for b in range(dirCount):
        dirInfoOffset = bs.readUInt()
        curHdrOffset = bs.tell()
        bs.seek(dirInfoOffset)

        dirNameOffset = bs.readUInt()
        dirDataOffset = bs.readUInt()
        bs.seek(dirNameOffset)
        dirName = bs.readString()
        bs.seek(dirDataOffset)

        bs.seek(4,1)
        texCount = bs.readUInt()
        if texCount != 0:
            #if rapi.noesisIsExporting():
                #expDir = os.path.split(rapi.getOutputName())
                #os.chdir(expDir[0])
                #if not os.path.exists(dirName):
                    #os.makedirs(dirName)

            texArrayOffset = bs.readUInt()
            aptDataOffset = bs.readUInt()
            aptConstOffset = bs.readUInt()
            texArrayOffset += dirDataOffset
            aptDataOffset += dirDataOffset
            aptConstOffset += dirDataOffset

            boToolGetFirstTexIndex(bs,data,aptDataOffset,texList)
            for c in range(texCount):
                texNameOffset = bs.readUInt()
                texNameIndex = bs.readUInt()
                curAptOffset = bs.tell()
                bs.seek(texNameOffset + aptDataOffset)
                texName = bs.readString()
                texNameWDir = dirName+" - "+texName
                bs.seek(texArrayOffset)
                for d in range(texCount):
                    texOffset = bs.readUInt()
                    texOffset += dirDataOffset
                    curTexPtrOffset = bs.tell()
                    bs.seek(texOffset)
                    if boSystem == 1:
                        bs.seek(0xA8,1)
                    elif boSystem == 3:
                        bs.seek(0x44,1)
                    texNameChk = bs.readString()
                    if texNameChk == str(texNameIndex) or texNameChk[11:] == str(texNameIndex-1):
                        boToolTexParse(bs,data,texOffset,0,texList,texNameWDir)
                        #if rapi.noesisIsExporting():
                            #curDir = expDir[0] + "\\" + texName + expDir[1]
                            #movDir = expDir[0] + "\\" + dirName + "\\" + texName + expDir[1]
                            #print(curDir," -> ",movDir)
                            #os.rename(curDir,movDir)
                    bs.seek(curTexPtrOffset)

                if boDebug:
                    print("DEBUG3:",hex(dirDataOffset),dirName+"\\"+texName,texNameIndex,"/",texCount)
                bs.seek(curAptOffset)
        bs.seek(curHdrOffset)
    return 1

def boToolGetTexBinOther(data,texList):
    bs = boToolSetup(data)

    txdCount = bs.readUInt()
    texOffset = bs.readUInt()
    if texOffset == 0:
        # assume B3/BL loadscrn
        for e in range(txdCount):
            txdNameGtID = bs.readUInt64() # GtID decompression in py when
            txdSize = bs.readUInt()
            txdOffset = bs.readUInt()
            txdOffset += 0x800 # aligned to 0x800 but never long enough to be elsewhere?
            curOffset = bs.tell()
            boToolTxdParse(bs,data,txdOffset,texList)
            bs.seek(curOffset)
    elif txdCount == 0x76312E34: # v1.4
        # assume Rev font file
        boToolTexParse(bs,data,texOffset,0,texList,0)
    else:
        # assume Dom PS2 font file
        bs.seek(0)
        fontName = bs.readString()
        bs.seek(0x70)
        texOffset = bs.readUInt()
        boToolTexParse(bs,data,texOffset,fontName,texList,1)
    return 1

def boToolGetTexArena(data,texList):
    bs = NoeBitStream(data)
    rapi.processCommands("-nofslwr -texnorepfn")
    # special case scenario where the platform selection is ignored

    bs.seek(0x10)
    arenaName = bs.readString()
    bs.seek(0x50)
    texOffset = bs.readUInt()
    if texOffset != 0:
        texOffset += 16
        boToolPSPArenaTex(bs,data,texOffset,0,arenaName,texList)
    else:
        bs.seek(0x90)
        aptDataOffset = bs.readUInt()
        aptConstOffset = bs.readUInt()
        unkPtrOffset = bs.readUInt() # anims?
        texPtrOffset = bs.readUInt()
        aptDataOffset += 16
        aptConstOffset += 16
        unkPtrOffset += 16
        texPtrOffset += 16

        bs.seek(texPtrOffset)
        texCount = bs.readUInt()
        if texCount != 0:
            texArrayOffset = bs.readUInt()
            texArrayOffset += 16
            if bs.readUInt() == 1:
                boToolGetFirstTexIndex(bs,data,aptDataOffset,texList)
                texNameOffset = bs.readUInt()
                if texNameOffset < texArrayOffset:
                    bs.seek(-4,1)
                    for f in range(texCount):
                        texNameOffset = bs.readUInt()
                        texNameIndex = bs.readUInt()
                        curAptOffset = bs.tell()
                        bs.seek(texNameOffset + aptDataOffset)
                        texName = bs.readString()
                        bs.seek(texArrayOffset)
                        texOffsetIndex = bs.readUInt()
                        texOffset = bs.readUInt()
                        texOffset += 16
                        #if texNameIndex == texOffsetIndex:
                        texArrayOffset = bs.tell()
                        boToolPSPArenaTex(bs,data,texOffset,texName,0,texList)
                        bs.seek(curAptOffset)
                    return 1
            boToolGetTexArenaAlt(bs,data,texArrayOffset,texCount,texList)
    return 1

def boToolGetTexArenaAlt(bs,data,texArrayOffset,texCount,texList):
    bs.seek(texArrayOffset)
    for g in range(texCount):
        texOffsetIndex = bs.readUInt()
        texOffset = bs.readUInt()
        texOffset += 16
        texArrayOffset = bs.tell()
        boToolPSPArenaTex(bs,data,texOffset,0,0,texList)
        bs.seek(texArrayOffset)

def boToolGetTexDatEnviro(data,texList):
    bs = boToolSetup(data)

    bs.seek(0x98)
    while True:
        texOffset = bs.readUInt()
        if texOffset < 0x100 or texOffset >= len(data):
            break
        curTexOffset = bs.tell()
        boToolTexParse(bs,data,texOffset,0,texList,0)
        bs.seek(curTexOffset)
    return 1

def boToolGetTexDatStatic(data,texList):
    bs = boToolSetup(data)

    fileVer = bs.readUByte()
    if fileVer == 0x78:
        bs = boToolDecZlib(bs,data)

    if fileVer < 0x26: # B3 demo
        bs.seek(0x14)
        texCount = bs.readUInt()
    else:
        bs.seek(0x16)
        texCount = bs.readUShort()
    texArrayOffset = bs.readUInt()
    bs.seek(texArrayOffset)
    for h in range(texCount):
        texOffset = bs.readUInt()
        curTexOffset = bs.tell()
        boToolTexParse(bs,data,texOffset,0,texList,0)
        bs.seek(curTexOffset)
    return 1

def boToolGetTexBxv(data,texList):
    bs = boToolSetup(data)

    fileVer = bs.readUByte()
    if fileVer != 0 and fileVer != 0x78: # zlib
        bs.seek(0x60)
        texOffset = bs.readUInt()
        boToolTexParse(bs,data,texOffset,0,texList,0)
    else:
        if fileVer == 0x78:
            bs = boToolDecZlib(bs,data)

        # i hate this whole section
        bs.seek(0x60)
        for i in range(19): # i think?
            texOffset = bs.readUInt()
            if texOffset != 0:
                curTexOffset = bs.tell()
                bs.seek(texOffset + 0x48)
                if bs.readUInt() != 2:
                    boToolTexParse(bs,data,texOffset,0,texList,0)
                else: # search through the array for matching filenames (palette)
                    bs.seek(texOffset)
                    texName = bs.readString()
                    bs.seek(0x60)
                    for j in range(19): # i think? pt2
                        palOffset = bs.readUInt()
                        if palOffset != 0:
                            curPalOffset = bs.tell()
                            bs.seek(palOffset)
                            palName = bs.readString()
                            bs.seek(palOffset + 0x48)
                            #print(hex(curPalOffset))
                            if palName == texName and bs.readUInt() == 0x86:
                                boToolTexParse(bs,data,texOffset,palOffset,texList,0)
                                bs.seek(curPalOffset - 4)
                                bs.writeUInt(0)
                                # to avoid being picked up by the tex scanner
                            bs.seek(curPalOffset)
                bs.seek(curTexOffset)
    return 1

def boToolTexParse(bs,data,texOffset,fontNameOrPalOffset,texList,texName):
    bs.seek(texOffset)
    if boSystem == 1:
        boToolPS2Tex(bs,data,texOffset,fontNameOrPalOffset,texList,texName)
    elif boSystem == 2:
        boToolPSPTex(bs,data,texOffset,texList)
    elif boSystem == 3:
        boToolXboxTex(bs,data,texOffset,fontNameOrPalOffset,texList,texName)
    elif boSystem == 4:
        boTool360Tex(bs,data,texOffset,fontNameOrPalOffset,texList,texName)

def boToolPS2Tex(bs,data,texOffset,fontName,texList,texName):
    bs.seek(4,1)
    bmpOffset = bs.readUInt()
    palOffset = bs.readUInt()
    texWidth = bs.readUInt()
    texHeight = bs.readUInt()
    bitDepth = bs.readUInt()
    bs.seek(0xB,1)
    texFmt = bs.readUByte()
    # other stuff, unnecessary
    bs.seek(0x7C,1)
    palCount = bs.readUByte()
    bs.seek(0x7,1)
    if texName == 0:
        texName = bs.readString()
    elif texName == 1:
        texName = bs.readString()
        texName += " ("+fontName+")"

    #bs.seek(bmpOffset-0x30)
    #texWidthDiv = bs.readUInt()
    #texHeightDiv = bs.readUInt()

    if boDebug:
        print("DEBUG2:",hex(bmpOffset+texOffset),hex(palOffset+texOffset),texWidth,texHeight,bitDepth,hex(texFmt),palCount,texName)
        #if texWidth != texWidthDiv*2 or texHeight != texHeightDiv*2:
            #print("SOMETHING DOESN'T MATCH HERE!",texWidth,"x",texHeight,"vs",texWidthDiv*2,"x",texHeightDiv*2)

    texData = list()
    bs.seek(bmpOffset + texOffset)

    if bitDepth == 4:
        if texWidth == 8:
            texWidth = 16
            texName += " (Crop to 8px width)"
        if texWidth == 16:
            for m in range(texHeight//2):
                boToolCvt4bitTo8bit(bs,data,16,texData)
                bs.seek(16,1)
        else:
            texBytes = texWidth*texHeight//2
            boToolCvt4bitTo8bit(bs,data,texBytes,texData)
    elif bitDepth == 8:
        texData = bs.readBytes(texWidth*texHeight)
    elif bitDepth == 24:
        if texWidth == 1:
            texWidth = 8
            texName += " (Crop to 1px width)"
            #for n in range(texHeight):
                #texData.extend(bs.readBytes(3))
                #bs.seek(21,1)
        texData = bs.readBytes(texWidth*texHeight*3)
    elif bitDepth == 32:
        texBytes = texWidth*texHeight
        boToolPS2AlphaFix(bs,data,texBytes,texData)
    texData = bytes(texData)

    if bitDepth <= 8:
        texData = rapi.imageUntwiddlePS2(texData,texWidth,texHeight,8)

        bs.seek(palOffset + texOffset)
        if palCount == 1:
            palData = list()
            if bitDepth == 8:
                palColors = 256
            elif bitDepth == 4:
                palColors = 16
            boToolPS2AlphaFix(bs,data,palColors,palData)
            palData = bytes(palData)
            texData = rapi.imageDecodeRawPal(texData,palData,texWidth,texHeight,8,"R8G8B8A8",noesis.DECODEFLAG_PS2SHIFT if bitDepth != 4 else noesis.NOESISTEX_UNKNOWN) # ??

        else:
            # interleaved & grouped palette splitter; supports up to 8
            palData0 = list()
            palData1 = list()
            palData2 = list()
            palData3 = list()
            palData4 = list()
            palData5 = list()
            palData6 = list()
            palData7 = list()
            for o in range(16):
                boToolPS2AlphaFix(bs,data,16,palData0)
                boToolPS2AlphaFix(bs,data,16,palData1)
                if palCount == 3 or palCount >= 5:
                    boToolPS2AlphaFix(bs,data,16,palData2)
                if palCount >= 7:
                    boToolPS2AlphaFix(bs,data,16,palData3)
            for p in range(16):
                if palCount >= 4:
                    boToolPS2AlphaFix(bs,data,16,palData4)
                    boToolPS2AlphaFix(bs,data,16,palData5)
                if palCount >= 5:
                    boToolPS2AlphaFix(bs,data,16,palData6)
                if palCount >= 7:
                    boToolPS2AlphaFix(bs,data,16,palData7)
            palData0 = bytes(palData0)
            palData1 = bytes(palData1)
            palData2 = bytes(palData2)
            palData3 = bytes(palData3)
            palData4 = bytes(palData4)
            palData5 = bytes(palData5)
            palData6 = bytes(palData6)
            palData7 = bytes(palData7)

            nameCount = 1
            boToolPalCount(data,nameCount,texName,texWidth,texHeight,texData,palData0,texList)
            nameCount += 1
            boToolPalCount(data,nameCount,texName,texWidth,texHeight,texData,palData1,texList)
            nameCount += 1
            if palCount == 3 or palCount >= 5:
                boToolPalCount(data,nameCount,texName,texWidth,texHeight,texData,palData2,texList)
                nameCount += 1
            if palCount >= 7:
                boToolPalCount(data,nameCount,texName,texWidth,texHeight,texData,palData3,texList)
                nameCount += 1
            if palCount >= 4:
                boToolPalCount(data,nameCount,texName,texWidth,texHeight,texData,palData4,texList)
                nameCount += 1
                boToolPalCount(data,nameCount,texName,texWidth,texHeight,texData,palData5,texList)
                nameCount += 1
            if palCount >= 6:
                boToolPalCount(data,nameCount,texName,texWidth,texHeight,texData,palData6,texList)
                nameCount += 1
            if palCount == 8:
                boToolPalCount(data,nameCount,texName,texWidth,texHeight,texData,palData7,texList)
                nameCount += 1
            return
    texList.append(NoeTexture(texName,texWidth,texHeight,texData,noesis.NOESISTEX_RGBA32 if bitDepth != 24 else noesis.NOESISTEX_RGB24))

def boToolPS2AlphaFix(bs,data,rColors,rData):
    for q in range(rColors):
        rData.extend(bs.readBytes(3))
        rAlpha = bs.readUByte()
        rAlpha *= 2
        if rAlpha == 0x100:
            rAlpha -= 1
        rData.append(rAlpha)

def boToolCvt4bitTo8bit(bs,data,rSize,rData):
    for r in range(rSize):
        rData.append(bs.readBits(4))
        rData.append(bs.readBits(4))

def boToolPSPTex(bs,data,texOffset,texList):
    bs.seek(8,1)
    palOffset = bs.readUInt()
    texWidth = bs.readUInt()
    texHeight = bs.readUInt()
    bitDepth = bs.readUInt()
    bs.seek(0x20,1)
    bmpOffset = bs.readUInt()
    bs.seek(0x74,1)
    palCount = bs.readUByte()
    bs.seek(-0x25,1)
    texName = bs.readString()

    if boDebug:
        print("DEBUG5:",hex(bmpOffset+texOffset),hex(palOffset+texOffset),texWidth,texHeight,bitDepth,palCount,texName)

    bs.seek(bmpOffset + texOffset)
    if bitDepth == 4:
        texData = bs.readBytes(texWidth*texHeight//2)
    elif bitDepth == 8:
        texData = bs.readBytes(texWidth*texHeight)
    elif bitDepth == 32:
        texData = bs.readBytes(texWidth*texHeight*4)
    else:
        print("HEY!!!!!!!!!",bitDepth)

    if bitDepth <= 8:
        bs.seek(palOffset + texOffset)
        texData = rapi.imageUntwiddlePSP(texData,texWidth,texHeight,bitDepth)
        if palCount ==1:
            if bitDepth == 8:
                palData = bs.readBytes(0x400)
            elif bitDepth == 4:
                palData = bs.readBytes(0x40)
            texData = rapi.imageDecodeRawPal(texData,palData,texWidth,texHeight,bitDepth,"R8G8B8A8")
        elif bitDepth == 8 and palCount > 1:
            nameCount = 1
            for s in range(palCount):
                palData = bs.readBytes(0x400)
                boToolPalCount(data,nameCount,texName,texWidth,texHeight,texData,palData,texList)
                nameCount += 1
            return
    texList.append(NoeTexture(texName,texWidth,texHeight,texData,noesis.NOESISTEX_RGBA32))

def boToolPSPArenaTex(bs,data,texOffset,texName,arenaName,texList):
    if arenaName != 0:
        texName = bs.readString()
        texName += " ("+arenaName+")"
    if texName == 0:
        texName = bs.readString()
    bs.seek(texOffset + 0x40)
    palCount = bs.readUByte()
    bs.seek(3,1)
    texWidth = bs.readUShort()
    texHeight = bs.readUShort()
    texFmt = bs.readUByte()
    if texFmt == 2:
        bitDepth = 4
    elif texFmt == 3:
        bitDepth = 8
    else:
        print("STOP RIGHT THERE!",texFmt)
    bs.seek(0x37,1)
    bmpOffset = bs.readUInt()
    bs.seek(0x1C,1)
    palOffset = bs.readUInt()
    if boDebug:
        print("DEBUG6:",hex(bmpOffset+texOffset),hex(palOffset+texOffset),texWidth,texHeight,palCount,texName)

    bs.seek(bmpOffset + texOffset)
    if texFmt == 2:
        texData = bs.readBytes(texWidth*texHeight//2)
        palData = bs.readBytes(0x40)
    elif texFmt == 3:
        texData = bs.readBytes(texWidth*texHeight)
        palData = bs.readBytes(0x400)

    texData = rapi.imageUntwiddlePSP(texData,texWidth,texHeight,bitDepth)
    texData = rapi.imageDecodeRawPal(texData,palData,texWidth,texHeight,bitDepth,"R8G8B8A8")
    texList.append(NoeTexture(texName,texWidth,texHeight,texData,noesis.NOESISTEX_RGBA32))

def boToolXboxTex(bs,data,texOffset,fontName,texList,texName):
    bs.seek(4,1) # 40001
    bmpOffset = bs.readUInt()
    bs.seek(0x2C,1)
    texFmt = bs.readUInt()
    texWidth = bs.readUInt()
    texHeight = bs.readUInt()
    bitDepth = bs.readUInt()
    bs.seek(0x24,1)
    if bitDepth >= 4 and bitDepth <= 32:
        chkGame = 0 # B3T
    else:
        chkGame = 1 # Rev
        bs.seek(-4,1)
        bitDepth = bs.readUByte()
    bs.seek(1,1)
    palCount = bs.readUByte()

    #chkGame = bs.readUByte()
    #if chkGame == 0:
        #bs.seek(3,1) # BRev
    #else:
        #bs.seek(-1,1) # B3T

    bs.seek(-0x22,1)
    if chkGame == 1:
        bs.seek(-1,1)
    if texName == 0:
        texName = bs.readString()
    bs.seek(texOffset+bmpOffset)
    if boDebug:
        print("DEBUG7:",texWidth,texHeight,bitDepth,palCount,hex(texFmt),texName)

    if texFmt == 0xB:
        texData = bs.readBytes(texWidth*texHeight)
        texData = rapi.imageFromMortonOrder(texData,texWidth,texHeight,1)
        bs.seek(texOffset+0x14)
        nameCount = 1
        for t in range(palCount):
            palOffset = bs.readUInt()
            curPalOffset = bs.tell()
            bs.seek(texOffset+palOffset+4) # 30001
            palOffset = bs.readUInt()
            bs.seek(texOffset+palOffset)
            if bitDepth == 4:
                palData = bs.readBytes(0x40)
            elif bitDepth == 8:
                palData = bs.readBytes(0x400)
            if palCount > 1:
                boToolPalCount(data,nameCount,texName,texWidth,texHeight,texData,palData,texList)
                nameCount += 1
            else:
                texData = rapi.imageDecodeRawPal(texData,palData,texWidth,texHeight,8,"B8G8R8A8")
                texList.append(NoeTexture(texName,texWidth,texHeight,texData,noesis.NOESISTEX_RGBA32))
            bs.seek(curPalOffset)
        return

    elif texFmt == 0xC:
        texFmt = noesis.NOESISTEX_DXT1
        texData = bs.readBytes(texWidth*texHeight//2)
    elif texFmt == 0xE:
        texFmt = noesis.NOESISTEX_DXT3
        texData = bs.readBytes(texWidth*texHeight)
    elif texFmt == 0xF:
        texFmt = noesis.NOESISTEX_DXT5
        texData = bs.readBytes(texWidth*texHeight)
    elif texFmt == 0x3A:
        texFmt = noesis.NOESISTEX_RGBA32
        texData = bs.readBytes(texWidth*texHeight*4)
        texData = rapi.imageFromMortonOrder(texData,texWidth,texHeight,4)
    else:
        print("UNKNOWN!!!",hex(texFmt))
    texList.append(NoeTexture(texName,texWidth,texHeight,texData,texFmt))

def boTool360Tex(bs,data,texOffset,palOffset,texList,texName):
    if texName == 0:
        texName = bs.readString()
        boToolPadAlign(bs,32,bs.tell())
    else:
        bs.seek(32,1)
    texWidth = bs.readUShort()
    texHeight = bs.readUShort()
    bs.seek(2,1)
    palCount = bs.readUByte()
    bs.seek(5,1)
    texSize = bs.readUInt()
    # other stuff, unnecessary
    bs.seek(0x18,1)
    texFmt = bs.readUInt()
    if boDebug:
        print("DEBUG4:",hex(texOffset),hex(palOffset),texWidth,texHeight,palCount,hex(texSize),hex(texFmt),texName)
    boToolPadAlign(bs,0x1000,bs.tell())
    if texFmt == 2 and texWidth < 256:
        # ??????????????????????????????????????????????????????????????????
        texData = list()
        for u in range(texHeight):
            texData.extend(bs.readBytes(texWidth))
            bs.seek(256-texWidth,1)
        texData = bytes(texData)
    else:
        texData = bs.readBytes(texSize - 0x1000)

    if texFmt == 2:
        bs.seek(palOffset + 0x1000)
        if palCount == 1:
            palData = bs.readBytes(0x400)
            texData = rapi.imageDecodeRawPal(texData,palData,texWidth,texHeight,8,"A8R8G8B8")
        else:
            nameCount = 1
            for v in range(palCount):
                palData = bs.readBytes(0x400)
                boToolPalCount(data,nameCount,texName,texWidth,texHeight,texData,palData,texList)
                nameCount += 1
            return
        texFmt = noesis.NOESISTEX_RGBA32
    elif texFmt == 0x52:
        texData = rapi.imageUntile360DXT(rapi.swapEndianArray(texData,2),texWidth,texHeight,8)
        texFmt = noesis.NOESISTEX_DXT1
    elif texFmt == 0x53:
        texData = rapi.imageUntile360DXT(rapi.swapEndianArray(texData,2),texWidth,texHeight,16)
        texFmt = noesis.NOESISTEX_DXT3
    elif texFmt == 0x54:
        texData = rapi.imageUntile360DXT(rapi.swapEndianArray(texData,2),texWidth,texHeight,16)
        texFmt = noesis.NOESISTEX_DXT5
    elif texFmt == 0x86:
        texData = rapi.imageUntile360Raw(texData,texWidth,texHeight,4)
        texData = rapi.imageDecodeRaw(texData,texWidth,texHeight,"A8R8G8B8")
        texFmt = noesis.NOESISTEX_RGBA32
    texList.append(NoeTexture(texName,texWidth,texHeight,texData,texFmt))

def boToolPalCount(data,nameCount,texName,texWidth,texHeight,texData,palData,texList):
    texName += " (Palette "+str(nameCount)+")"
    if boSystem == 1:
        texData = rapi.imageDecodeRawPal(texData,palData,texWidth,texHeight,8,"R8G8B8A8",noesis.DECODEFLAG_PS2SHIFT)
    elif boSystem == 2:
        texData = rapi.imageDecodeRawPal(texData,palData,texWidth,texHeight,8,"R8G8B8A8")
    elif boSystem == 3:
        texData = rapi.imageDecodeRawPal(texData,palData,texWidth,texHeight,8,"B8G8R8A8")  # rapi.imageFlipRGBA32(texData,texWidth,texHeight,0,1) ?
    elif boSystem == 4:
        texData = rapi.imageDecodeRawPal(texData,palData,texWidth,texHeight,8,"A8R8G8B8")
    texList.append(NoeTexture(texName,texWidth,texHeight,texData,noesis.NOESISTEX_RGBA32))
