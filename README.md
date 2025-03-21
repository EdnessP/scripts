# NOTICE
**These scripts are now listed in a somewhat more viewable fashion on my website at [EdnessP.github.io](https://EdnessP.github.io/tools)**

 <br>

# My Scripts
This repository contains random scripts I've written at one point or another.  I've written additional info in the header for some of them just for uploading them here.  Most of them are written for QuickBMS, but there are a few Python (both regular and Noesis) scripts, and one GreaseMonkey script too.

If any problems arise, contact Edness on Discord.

If you wish to, you may also [donate to me here](https://ko-fi.com/edness).

## Script list
<details>
<summary>bully\</summary>

- BullyAE_encryption.py &mdash; Decrypt and encrypt **Bully: Anniversary Edition** .EFF, .MTL, .WDB, and .XML files.
- BullyAE_parse.py &mdash; Convert **Bully: Anniversary Edition** files' header info strings to usable lists and dictionaries.
- BullyAEjumptable.bms &mdash; **Bully: Anniversary Edition** developer savefile archive. (jumptable.bin)
- BullyHash &mdash; Hashing functions used by **Bully** for RSTM audio and string label lookup hashes. [Live version](https://ednessp.github.io/live/strings#Bully_(Canis_Canem_Edit)).
- BullyX360img.bms &mdash; Extract **Bully: Scholarship Edition** Wii and Xbox 360 .IMG files.
- fmt_BullyAE.py &mdash; **Bully: Anniversary Edition** Noesis plugin for textures and models.
- fmt_BullySE_Wii.py &mdash; **Bully: Scholarship Edition** Wii Noesis plugin for textures and models.
- lipfile_update.py &mdash; **Bully** .LIP file updater to allow for Speech.bin edits.
- string_bin.py &mdash; **Bully** .BIN file exporter and importer.

</details>

<details>
<summary>burnout\</summary>

- BLegendsDS.bms &mdash; Decompress LZSS compressed files in **Burnout Legends** NDS.
- BurnoutCRASH_BIG.bms &mdash; **Burnout CRASH!** .BIG archives.
- BurnoutCRASH_CSVparse.py &mdash; Split **Burnout CRASH!** texture sheets using the .CSV files.
- bxv_palsplit.bms &mdash; Split and re-merge interleaved-grouped palettes from .BGV and .BTV files.
- fmt_Burnout3LRD.py &mdash; All-in-One Noesis plugin for the **Takedown**-era games (as well as **Black** and the PSP version of **NFS: Shift**).
- fmt_Burnout3LRD_changelog.txt &mdash; Update history for the Noesis plugin.
- fmt_BurnoutCRASH.py &mdash; **Burnout CRASH!** PS3, Xbox 360, iOS model and texture Noesis plugin.
- GtHash.py &mdash; Python reimplementation of GtHash string hashing. [Live version](https://ednessp.github.io/live/strings#Criterion_Games).
- GtID.py &mdash; Python reimplementation of GtID EA string compression and decompression. [Live version](https://ednessp.github.io/live/strings#Criterion_Games).
- tex_Burnout1.py &mdash; **Burnout** PS2 and Xbox Noesis texture plugin.
- tex_Burnout2.py &mdash; **Burnout 2: Point of Impact** GameCube, PS2, Xbox Noesis texture plugin.
- txdscanner.bms &mdash; Extracts .TXDs from containers.  Only really needed for fonts stored in the executable.

</details>

<details>
<summary>cod\</summary>

- codfh_hash.py &mdash; **Call of Duty: Finest Hour** PS2 & Xbox filename hashing function reimplementation. [Live version](https://ednessp.github.io/live/strings#Call_of_Duty).
- codfh_pak_filenames.py &mdash; **Call of Duty: Finest Hour** PS2 & Xbox .PAK extractor with filename support.
- codfh_bigfile.bms &mdash; **Call of Duty: Finest Hour** PS2 & Xbox .BDS archive extractor.
- codfhpak.bms &mdash; **Call of Duty: Finest Hour** PS2 & Xbox .PAK files.

</details>

<details>
<summary>jak-daxter\</summary>

- jak1-2vagwad.bms &mdash; **Jak and Daxter: The Precursor Legacy** & **Jak II: Renegade** VAGWAD files.
- jak3-Xvagwad.py &mdash; **Jak 3** & **Jak X: Combat Racing** VAGWAD files.
- jak3-Xvagdir_algo.py &mdash; **Jak 3** & **Jak X: Combat Racing** filename compression function reimplementation. [Live version](https://ednessp.github.io/live/strings#Jak_&_Daxter).

</details>

<details>
<summary>midnight-club\</summary>

- dave.py &mdash; **Angel Studios** / **Rockstar San Diego** Dave archive extractor and rebuilder.
- hash_build.py &mdash; **Angel Studios** / **Rockstar San Diego** Hash archive extractor and rebuilder.
- MclHash.py &mdash; **Midnight Club 2** & **Midnight Club 3: DUB Edition** audio and string hash lookup reimplementations. [Live version](https://ednessp.github.io/live/strings#Midnight_Club).
- strtbl.py &mdash; **Angel Studios** / **Rockstar San Diego** .STRTBL string table exporter and rebuilder.
- rstm_build.py &mdash; **Rockstar San Diego** .RSM (RSTM) sound file builder.

</details>

<details>
<summary>other\</summary>

### GAME ARCHIVES

- activisionRPF.bms &mdash; **Activision Anthology** .RPF archives.
- atariGLM.bms &mdash; **Atari Anthology** .GLM archives.
- atetdbidkPAK.bms &mdash; **Adventure Time: Explore the Dungeon Because I Don't Know!** .PAK files.
- BombermanActZero.bms &mdash; **Bomberman Act:Zero** .DAT files.
- cstrikeRDA.bms &mdash; **Castle Strike** .RDA archives.
- driversf-chnk.bms &mdash; **Driver: San Francisco** CHNK archives (.DNGC, .FCHUNK, .SP).
- mst-freaky_flyers.bms &mdash; **Freaky Flyers** .MST files.  (Has 24 byte name fields and LZO1X compression)
- mst-saints_row_uc.bms &mdash; **Saints Row Undercover** .MST files.  (Has hashed filenames)
- mst-scooby_doo_www&#x200b;.bms &mdash; **Scooby-Doo! Who's Watching Who?** .MST files.  (Has 16 byte name fields)
- ready2rumbleRAT.bms &mdash; **Ready 2 Rumble Boxing** (1) and **Round 2** .RAT files.
- txbp-tm2.bms &mdash; **Yakuza 1** & **2** PS2 TXBP texture container to TM2 converter.

### GAME TEXTURES / MODELS

- fmt_BigRigsOTRR.py &mdash; **Big Rigs: Over the Road Racing** PC .SCO Noesis model plugin.
- tex_BombermanActZero.py &mdash; **Bomberman Act:Zero** XPR2 textures extracted with the QuickBMS script.
- tex_FreakyFlyers.py &mdash; **Freaky Flyers** PS2 .PTX and Xbox .XTX Noesis texture plugin.
- tex_HuneX_MF_PS2.py &mdash; PS2 Texture extraction for **HuneX** developed games.
- tex_SpongebobSurfnSkate.py &mdash; **SpongeBob's Surf & Skate Roadtrip** .XEN textures. May work on other Blitz Games archives too.
- tex_Yakuza.py &mdash; **Yakuza** TXBP Noesis texture exporter plugin.

### MISCELLANEOUS

- 4bpp8bpp.bms &mdash; Convert 4-bit PS2 textures in a TM2 container to 8-bit.
- DVO3parser.bms &mdash; Prints **Driver: San Francisco** Wii .VO3 values.
- epic_mickey_hash.py &mdash; **Epic Mickey** Wii string hashing function reimplementation. [Live version](https://ednessp.github.io/live/strings#Epic_Mickey).
- LingoTildeStr.py &mdash; SIA Tilde's Latvian **Lingo** string compression. [Live version](https://ednessp.github.io/live/strings#Lingo_(Tildes_Birojs)).
- LingoTildeWordList.txt &mdash; SIA Tilde's Latvian **Lingo** word list.
- multigim-split.bms &mdash; Split multiple GIM textures glued together, used in **Exit** PSP and possibly others.
- ms_timestamp.py &mdash; Python reimplementation of *xbexexmzpe.bms* written by jason098.
- PICparse.py &mdash; Python parser for Blu-ray **Permanent Information & Control** (PIC) binaries. [Live version](https://ednessp.github.io/live/redump#Permanent_Information_&_Control).
- sch-imus-strip.bms &mdash; Removes all but **BANK** and **PFSM** sections from PS2 .SCH files for vgmstream compatibility.
- tm2scanner.bms &mdash; Searches for and extracts .TM2 files in a container.
- TRLegendHash.py &mdash; **Tomb Raider** Wii string hashing function reimplementation. [Live version](https://ednessp.github.io/live/strings#Tomb_Raider).
- twitchPopoutChroma &mdash; **twitch.tv** popout chat window effects for chroma keying.
- xbexexmzpe.bms &mdash; Windows, Xbox, Xbox 360 executable timestamps.

</details>

<details>
<summary>ps2\</summary>

- fmt_PS2memcard.py &mdash; **PlayStation 2** Memory Card save icon Noesis importer/exporter plugin. This script has been published incomplete as-is currently, see the comments in the header for more information.
- mic_build.py &mdash; Builds **PlayStation 2** MultiStreamer .MIC and .MIH+.MIB audio files.

</details>

<details>
<summary>saints-row\</summary>

- sr2_xml_charlist.py &mdash; Converts **Saints Row 2** internal character mapping on an exported string file.

</details>

<details>
<summary>sims-console\</summary>

- Sims2PetsKeyGen.py &mdash; **The Sims 2: Pets** Unlock Code gift key generator and decoder. [Live version](https://ednessp.github.io/live/strings#The_Sims_(Console))
- tex_SimsConsole.py &mdash; **The Sims: Bustin' Out**, **The Urbz: Sims in the City**, **The Sims 2**, **The Sims 2: Pets**, **The Sims 2: Castaway** PS2 Noesis TEXTURES.ARC plugin.

</details>

<details>
<summary>simpsons-game\</summary>

- TheSimpsonsGame_NewGen_LH2.py &mdash; **The Simpsons Game** (PS3, X360) .LH2 (2HCL) string file exporter and rebuilder.
- tex_TheSimpsonsGame_X360_itxd.py &mdash; **The Simpsons Game** Xbox 360 .ITXD Noesis texture plugin.
- tsg_hash.py &mdash; **The Simpsons Game** (PS3, X360) string label lookup hashing. [Live version](https://ednessp.github.io/live/strings#The_Simpsons_Game).

</details>

<details>
<summary>strike-suit\</summary>

- SSZI_LNG.py &mdash; **Strike Suit Zero** / **Strike Suit Infinity** .LNG string file exporter and rebuilder.
- SSZI_decomp.bms &mdash; **Strike Suit Zero** / **Strike Suit Infinity** LPMC/XEMC decompressor.

</details>
