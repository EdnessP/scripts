# Written by Edness
boVer = "v0.5d"
boDate = "2021-09-13"
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

    handleArena = noesis.register("Burnout Dominator PSP",".arena")
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
    if texCount < 100 and texCount != 0 and len(data) > 0x810: # B3/BL loadscrn
        bs.seek(0x800)
        if bs.readUInt64() == 0xBCDEED81543C0000:
            return 1
    elif fontMagic == 0x76312E34 or fontMagic == 0x342E3176: # v1.4
        return 1 # Rev font file
    if len(data) > 0x200: # see boToolCheckTypeDatEnviro
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
    if len(data) > 0x300: # to not break burnout paradise .dats
        bs.seek(0xA8)
        someID = bs.readUInt()
        fileSize = bs.readUInt()
        if (fileSize == len(data) or fileSize == 0) and someID == 0x45440002: # ps2 & xbox
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
        bs.seek(0x2D4)
        if bs.readUInt() == 0x45440004 and bs.readUInt() == len(data): # psp nfs shift
            return 1
    return 0

# FUNCTION LIST FOR KEEPNG TRACK
#   boToolVersionWarning
#   boToolPlatformCheck
#   boToolSetSystem
#   boToolLockSystem
#   boToolCloseWindow
#   boToolSetup
#   boToolDecZlib
#   boToolPadAlign
#   boToolGetFirstTexIndex
#   boToolChar2UTF
#   boToolDecGtID
#   boToolGetTexName
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
#   boToolTex1pxSkip
#   boToolSmallTexCrop
#   boToolTexWidthDiv
#   boToolPalCount

def boToolVersionWarning():
    boWindow = noewin.NoeUserWindow("Warning","BOToolWarningClass",286,139) # 280x110
    boWindowRect = noewin.getNoesisWindowRect()
    boWindow.x = boWindowRect[0]+444
    boWindow.y = boWindowRect[1]+313
    if boWindow.createWindow():
        boWindow.setFont("Segoe UI",12)
        boWindow.createStatic("Outdated version detected!\nPlease update Noesis to v4.453 or newer!",16,16,248,32)
        boWindow.createButton("OK",168,62,96,32,boToolCloseWindow)
        boWindow.doModal()

def boToolPlatformCheck():
    boWindow = noewin.NoeUserWindow("Burnout Tool  –  Opening "+os.path.split(rapi.getInputName())[1],"BOToolPlatformClass",406,253) # 400x224
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
        boWindow.createStatic("This plugin is brought to you by the Burnout Modding community.\nwww.burnout.wiki  |  discord.gg/8zxbb4x",16,167,368,32)
        boWindow.createStatic(boVer+"  –  Written by Edness  –  ("+boDate+")",32,200,336,16)
        try: boSystem # check the previously selected system
        except NameError: pass
        else: boToolSetSystem(boWindow,boSystem+100,0,0)
        boWindow.doModal()

def boToolSetSystem(boWindow,cID,wParam,lParam):
    global boSystem
    boSystem = cID - 100
    checkBoxPS2 = boWindow.getControlById(101)
    checkBoxPSP = boWindow.getControlById(102)
    checkBoxXbx = boWindow.getControlById(103)
    checkBox360 = boWindow.getControlById(104)
    # tfw no radio buttons
    if cID == 101:
        checkBoxPS2.setChecked(1)
        checkBoxPSP.setChecked(0)
        checkBoxXbx.setChecked(0)
        checkBox360.setChecked(0)
    elif cID == 102:
        checkBoxPS2.setChecked(0)
        checkBoxPSP.setChecked(1)
        checkBoxXbx.setChecked(0)
        checkBox360.setChecked(0)
    elif cID == 103:
        checkBoxPS2.setChecked(0)
        checkBoxPSP.setChecked(0)
        checkBoxXbx.setChecked(1)
        checkBox360.setChecked(0)
    elif cID == 104:
        checkBoxPS2.setChecked(0)
        checkBoxPSP.setChecked(0)
        checkBoxXbx.setChecked(0)
        checkBox360.setChecked(1)

def boToolLockSystem(boWindow,cID,wParam,lParam):
    global boSysLock
    #print(cID)
    checkBoxLck = boWindow.getControlById(cID)
    checkBoxLck.setChecked(1 if not checkBoxLck.isChecked() else 0)
    if not checkBoxLck.isChecked():
        boSysLock = 0
    else:
        boSysLock = 1

def boToolCloseWindow(boWindow,cID,wParam,lParam):
    boWindow.closeWindow()

def boToolSetup(data):
    if noesis.getAPIVersion() < 78: # -nofslwr deprecated in 4.452 & 1px-24bpp preview fix in 4.453
        boToolVersionWarning()
    rapi.processCommands("-texnorepfn")
    try: boSysLock
    except NameError:
        boToolPlatformCheck()
    else: # can't elif
        if boSysLock == 0:
            boToolPlatformCheck()
    return NoeBitStream(data,NOE_LITTLEENDIAN if boSystem < 4 else NOE_BIGENDIAN)

def boToolDecZlib(bs,data):
    bs.seek(0)
    cmpData = bs.readBytes(bs.getSize())
    decData = rapi.decompInflate(cmpData,rapi.getInflatedSize(cmpData))
    return NoeBitStream(decData,NOE_BIGENDIAN) # assume 360 only

def boToolPadAlign(bs,padSize,padFrom):
    if padFrom % padSize != 0:
        bs.seek((padFrom//padSize+1)*padSize)

def boToolGetFirstTexIndex(bs,data,aptDataOffset,firstTex,texList):
    bs.seek(aptDataOffset)
    while True: # may be unreliable? (especially for psp .arenas)
        if bs.readUInt() == firstTex:
            bs.seek(-8,1)
            break

def boToolChar2UTF(cChar):
    char = {
        1: "-", 2: "/", 3: "0", 4: "1", 5: "2", 6: "3", 7: "4", 8: "5", 9: "6", 10: "7",
        11: "8", 12: "9", 13: "A", 14: "B", 15: "C", 16: "D", 17: "E", 18: "F", 19: "G", 20: "H",
        21: "I", 22: "J", 23: "K", 24: "L", 25: "M", 26: "N", 27: "O", 28: "P", 29: "Q", 30: "R",
        31: "S", 32: "T", 33: "U", 34: "V", 35: "W", 36: "X", 37: "Y", 38: "Z", 39: "_"
    }
    return char.get(cChar,"")

def boToolDecGtID(cGtID):
    decStr = ""
    for i in range(12):
        decStr += boToolChar2UTF(cGtID % 40)
        cGtID //= 40
    if boDebug:
        print("Decompressed string:",decStr[::-1])
    return decStr[::-1]

def boToolGetTexName(bs,data,texOffset):
    bs.seek(texOffset) # boSystem == 4
    if boSystem == 1:
        bs.seek(0xA8,1)
    elif boSystem == 2:
        bs.seek(0xAC,1)
    elif boSystem == 3:
        bs.seek(0x44,1)
    return bs.readString()

def boToolGetTexTxd(data,texList):
    bs = boToolSetup(data)
    boToolTxdParse(bs,data,0,texList)
    return 1

def boToolTxdParse(bs,data,startOffset,texList):
    bs.seek(startOffset + 8)
    texCount = bs.readUInt()
    offStart = bs.readUInt() + startOffset
    bs.seek(offStart)
    for a in range(texCount):
        texNum = bs.readUInt64()
        texOffset = bs.readUInt() + startOffset
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

            texArrayOffset = bs.readUInt() + dirDataOffset
            aptDataOffset = bs.readUInt() + dirDataOffset
            aptConstOffset = bs.readUInt() + dirDataOffset

            bs.seek(texArrayOffset)
            texOffset = bs.readUInt() + dirDataOffset
            boToolGetFirstTexIndex(bs,data,aptDataOffset,int(boToolGetTexName(bs,data,texOffset)),texList)
            for c in range(texCount):
                texNameOffset = bs.readUInt()
                texNameIndex = bs.readUInt()
                curAptOffset = bs.tell()
                bs.seek(texNameOffset + aptDataOffset)
                texName = bs.readString()
                texNameWDir = dirName+" - "+texName
                bs.seek(texArrayOffset)
                for d in range(texCount):
                    texOffset = bs.readUInt() + dirDataOffset
                    curTexPtrOffset = bs.tell()

                    if boToolGetTexName(bs,data,texOffset) == str(texNameIndex): # (Black) or texNameChk[11:] == str(texNameIndex-1)
                        boToolTexParse(bs,data,texOffset,0,texList,texNameWDir)
                        #if rapi.noesisIsExporting():
                            #curDir = expDir[0] + "\\" + texName + expDir[1]
                            #movDir = expDir[0] + "\\" + dirName + "\\" + texName + expDir[1]
                            #print(curDir," -> ",movDir)
                            #os.rename(curDir,movDir)
                        break
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
            txdNameGtID = boToolDecGtID(bs.readUInt64()) # check if matches texname[:12]?
            txdSize = bs.readUInt()
            txdOffset = bs.readUInt()+0x800 # aligned to 0x800 but never long enough to be elsewhere?
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
    rapi.processCommands("-texnorepfn")
    # special case scenario where the platform selection is ignored

    bs.seek(0x10)
    arenaName = bs.readString()
    bs.seek(0x50)
    texOffset = bs.readUInt()
    if arenaName[-4:] == ".msh":
        boToolPSPArenaTex(bs,data,16,arenaName,0,texList)
    elif texOffset != 0:
        boToolPSPArenaTex(bs,data,texOffset+16,0,arenaName,texList)
    else:
        bs.seek(0x90)
        aptDataOffset = bs.readUInt()+16
        aptConstOffset = bs.readUInt()+16
        unkPtrOffset = bs.readUInt()+16 # anims?
        texPtrOffset = bs.readUInt()+16

        bs.seek(texPtrOffset)
        texCount = bs.readUInt()
        if texCount != 0:
            texArrayOffset = bs.readUInt()+16
            if bs.readUInt() == 1:
                boToolGetFirstTexIndex(bs,data,aptDataOffset,1,texList)
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
                        texOffset = bs.readUInt()+16
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
        texOffset = bs.readUInt()+16
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
                                bs.writeUInt(0) # to avoid being picked up by the tex scanner
                                break
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

    if boDebug:
        print("DEBUG2:",hex(bmpOffset+texOffset),hex(palOffset+texOffset),texWidth,texHeight,bitDepth,hex(texFmt),palCount,texName)

    texData = list()
    bs.seek(bmpOffset + texOffset)

    crop = 0
    if bitDepth == 4:
        if texWidth == 2 and texHeight == 2:
            texWidth = 16
            texHeight = 4
            crop = 4
        if texWidth == 4:
            texWidth = 16
            crop = 2
        elif texWidth == 8:
            texWidth = 16
            crop = 1
        if texWidth == 16:
            for k in range(texHeight//2):
                boToolCvt4bitTo8bit(bs,data,16,texData)
                bs.seek(16,1)
        else:
            boToolCvt4bitTo8bit(bs,data,texWidth*texHeight//2,texData)
    elif bitDepth == 8:
        if texWidth == 1:
            texWidth = 16
            crop = 3
        if texWidth == 4:
            texWidth = 16
            crop = 2
        texData = bs.readBytes(texWidth*texHeight)
    elif bitDepth == 24:
        if texWidth == 1:
            boToolTex1pxSkip(bs,data,texData,texHeight,3,21)
        else:
            texData = bs.readBytes(texWidth*texHeight*3)
    elif bitDepth == 32:
        boToolPS2AlphaFix(bs,data,texWidth*texHeight,texData)
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

            bs = NoeBitStream(texData)
            if crop == 1: # janky fixes tbh
                #texData = texData[32::]
                texWidth = 8
                texData = list()
                texData = boToolTexWidthDiv(bs,data,texData,texHeight,32)
            elif crop == 2:
                texWidth = 4
                texData = boToolSmallTexCrop(bs,data,texData,texHeight,2)
            elif crop == 3:
                texWidth = 1
                texData = list()
                boToolTex1pxSkip(bs,data,texData,texHeight,4,60)
                texData = bytes(texData)
            elif crop == 4:
                texWidth = 2
                texHeight = 2
                texData = boToolSmallTexCrop(bs,data,texData,texHeight,3)
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
            for l in range(16):
                boToolPS2AlphaFix(bs,data,16,palData0)
                boToolPS2AlphaFix(bs,data,16,palData1)
                if palCount == 3 or palCount >= 5:
                    boToolPS2AlphaFix(bs,data,16,palData2)
                if palCount >= 7:
                    boToolPS2AlphaFix(bs,data,16,palData3)
            for m in range(16):
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
            return
    texList.append(NoeTexture(texName,texWidth,texHeight,texData,noesis.NOESISTEX_RGBA32 if bitDepth != 24 else noesis.NOESISTEX_RGB24))

def boToolPS2AlphaFix(bs,data,rColors,rData):
    for n in range(rColors):
        rData.extend(bs.readBytes(3))
        rAlpha = bs.readUByte()
        rAlpha *= 2
        if rAlpha == 0x100:
            rAlpha -= 1
        rData.append(rAlpha)

def boToolCvt4bitTo8bit(bs,data,rSize,rData):
    for o in range(rSize):
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
    bs.seek(0x72,1)
    if bs.readUShort() == 0:
        bs.seek(4,1) # nfs shift psp fix
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
            for p in range(palCount):
                palData = bs.readBytes(0x400)
                boToolPalCount(data,nameCount,texName,texWidth,texHeight,texData,palData,texList)
                nameCount += 1
            return
    texList.append(NoeTexture(texName,texWidth,texHeight,texData,noesis.NOESISTEX_RGBA32))

def boToolPSPArenaTex(bs,data,texOffset,texName,arenaName,texList):
    bs.seek(texOffset)
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
    elif texFmt == 3:
        texData = bs.readBytes(texWidth*texHeight)
    bs.seek(palOffset + texOffset)
    if texFmt == 2:
        palData = bs.readBytes(0x40)
    elif texFmt == 3:
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

    bs.seek(-0x22,1)
    if chkGame == 1:
        bs.seek(-1,1)
    if texName == 0:
        texName = bs.readString()
    bs.seek(texOffset+bmpOffset)
    if boDebug:
        print("DEBUG7:",texWidth,texHeight,bitDepth,palCount,hex(texFmt),texName)

    wCrop = 0
    hCrop = 0
    if texWidth < 4:
        wCrop = texWidth
        texWidth = 4
    if texHeight < 4:
        hCrop = texHeight
        texHeight = 4

    if texFmt == 0xB:
        texData = bs.readBytes(texWidth*texHeight)
        texData = rapi.imageFromMortonOrder(texData,texWidth,texHeight,1)
        bs.seek(texOffset+0x14)
        nameCount = 1
        for q in range(palCount):
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

    if wCrop: # janky fixes, the sequel.  only works with dxt
        texWidth = wCrop
    if hCrop:
        texHeight = hCrop
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

    if texFmt == 2 and texWidth == 128:
        texData = list()
        texData = boToolTexWidthDiv(bs,data,texData,texHeight,texWidth)
    else:
        texData = bs.readBytes(texSize - 0x1000)

    wCrop = 0
    hCrop = 0
    if boDebug == 2:
        if texFmt != 2 and texWidth <= 16: # assume dxt3 or dxt5
            wCrop = texWidth
            hCrop = texHeight
            texWidth = 128
            texHeight = 128

    if texFmt == 2:
        bs.seek(palOffset + 0x1000)
        if palCount == 1:
            palData = bs.readBytes(0x400)
            texData = rapi.imageDecodeRawPal(texData,palData,texWidth,texHeight,8,"A8R8G8B8")
        else:
            nameCount = 1
            for r in range(palCount):
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

    if wCrop: # janky experimental fix, not active by default
        texWidth = wCrop
        texHeight = hCrop
        bs = NoeBitStream(texData)
        texData = list()

        weirdAlign = 1
        for v in range(texHeight//4):
            bs.seek(0x1A0,1)
            texData.extend(bs.readBytes((texWidth//4)*16))
            bs.seek(0x20,1)
            if texWidth == 8:
                bs.seek(0x20,1)
            if weirdAlign == 8:
                bs.seek(0x20,1)
            weirdAlign += 1
        texData = bytes(texData)
    texList.append(NoeTexture(texName,texWidth,texHeight,texData,texFmt))

def boToolTex1pxSkip(bs,data,texData,texHeight,readSize,skipSize):
    for s in range(texHeight):
        texData.extend(bs.readBytes(readSize))
        bs.seek(skipSize,1)

def boToolSmallTexCrop(bs,data,texData,texHeight,divCount):
    divSize = 32
    for t in range(divCount):
        texData = list()
        texData = boToolTexWidthDiv(bs,data,texData,texHeight,divSize)
        bs = NoeBitStream(texData)
        divSize //= 2
    return texData

def boToolTexWidthDiv(bs,data,texData,texHeight,divSize):
    for u in range(texHeight):
        texData.extend(bs.readBytes(divSize))
        bs.seek(divSize,1)
    texData = bytes(texData)
    return texData

def boToolPalCount(data,nameCount,texName,texWidth,texHeight,texData,palData,texList):
    texName += " (Palette "+str(nameCount)+")"
    if boSystem == 1:
        texData = rapi.imageDecodeRawPal(texData,palData,texWidth,texHeight,8,"R8G8B8A8",noesis.DECODEFLAG_PS2SHIFT)
    elif boSystem == 2:
        texData = rapi.imageDecodeRawPal(texData,palData,texWidth,texHeight,8,"R8G8B8A8")
    elif boSystem == 3:
        texData = rapi.imageDecodeRawPal(texData,palData,texWidth,texHeight,8,"B8G8R8A8")
    elif boSystem == 4:
        texData = rapi.imageDecodeRawPal(texData,palData,texWidth,texHeight,8,"A8R8G8B8")
    texList.append(NoeTexture(texName,texWidth,texHeight,texData,noesis.NOESISTEX_RGBA32))
