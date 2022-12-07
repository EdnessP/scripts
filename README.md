# NOTICE
**These scripts are now listed in a somewhat more viewable fashion on my website at [EdnessP.github.io](https://EdnessP.github.io/tools)**

 <br>

# My Scripts
This repository contains random scripts I've written at one point or another.  I've written additional info in the header for some of them just for uploading them here.  Most of them are written for QuickBMS, but there are a few Python (both regular and Noesis) scripts, and one GreaseMonkey script too.

If any problems arise, contact Edness#2203 on Discord.

If you wish to, you may also [donate to me here](https://www.paypal.com/donate/?hosted_button_id=Z4LLFEUNXXRGJ).

## Script list
<details>
<summary>bully\</summary>

- BullyAE_encryption.py &mdash; Decrypt and encrypt **Bully: Anniversary Edition** .EFF, .MTL, .WDB, and .XML files.
- BullyAE_parse.py &mdash; Convert **Bully: Anniversary Edition** files' header info strings to usable lists and dictionaries.
- BullyAEjumptable.bms &mdash; **Bully: Anniversary Edition** developer savefile archive. (jumptable.bin)
- BullyHash &mdash; Hashing functions used by **Bully** for RSTM audio and string label lookup hashes.
- BullyX360img.bms &mdash; Extract **Bully: Scholarship Edition** Wii and Xbox 360 .IMG files.
- fmt_BullyAE.py &mdash; **Bully: Anniversary Edition** Noesis plugin for textures and models.

</details>

<details>
<summary>burnout\</summary>

- BLegendsDS.bms &mdash; Decompress LZSS compressed files in **Burnout Legends** NDS.
- BurnoutCRASH_BIG.bms &mdash; **Burnout CRASH!** .BIG archives.
- BurnoutCRASH_CSVparse.py &mdash; Split **Burnout CRASH!** texture sheets using the .CSV files.
- bxv_palsplit.bms &mdash; Split and re-merge interleaved-grouped palettes from .BGV and .BTV files.
- fmt_Burnout3LRD.py &mdash; All-in-One Noesis plugin for the **Takedown**-era games (as well as **Black** and the PSP version of **NFS: Shift**).  Currently only supports textures.
- fmt_Burnout3LRD_changelog.txt &mdash; Update history for the Noesis plugin.
- fmt_BurnoutCRASH.py &mdash; **Burnout CRASH!** PS3, Xbox 360, iOS model and texture Noesis plugin.
- GtHash.py &mdash; Python reimplementation of GtHash string hashing.
- GtIDstr.py &mdash; Python reimplementation of GtID EA string compression and decompression.
- tex_Burnout1.py &mdash; **Burnout** PS2 and Xbox Noesis texture plugin.
- tex_Burnout2.py &mdash; **Burnout 2: Point of Impact** PS2 and Xbox Noesis texture plugin.
- txdscanner.bms &mdash; Extracts .TXDs from containers.  Only really needed for fonts stored in the executable.

</details>

<details>
<summary>cod\</summary>

- codfh_hash.py &mdash; **Call of Duty: Finest Hour** PS2 & Xbox filename hashing function reimplementation.
- codfh_pak_filenames.py &mdash; **Call of Duty: Finest Hour** PS2 & Xbox .PAK extractor with filename support.
- codfhpak.bms &mdash; **Call of Duty: Finest Hour** PS2 & Xbox .PAK files.

</details>

<details>
<summary>midnight-club\</summary>

- MclHash.py &mdash; **Midnight Club 2** & **Midnight Club 3: DUB Edition** audio and string hash lookup reimplementations.
- mclub_strtbl.py &mdash; **Midnight Club 2** & **Midnight Club 3: DUB Edition** (and other earlier Angel Studios/Rockstar: San Diego) .STRTBL string table exporter and rebuilder

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
- jak1-2vagwad.bms &mdash; **Jak and Daxter: The Precursor Legacy** & **Jak II: Renegade** VAGWAD files.
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
- LingoTildeStr.py &mdash; SIA Tilde's Latvian **Lingo** string compression.
- LingoTildeWordList.txt &mdash; SIA Tilde's Latvian **Lingo** word list.
- multigim-split.bms &mdash; Split multiple GIM textures glued together, used in **Exit** PSP and possibly others.
- ms_timestamp.py &mdash; Python reimplementation of *xbexexmzpe.bms* written by jason098.
- PICparse.py &mdash; Python parser for Blu-ray **Permanent Information & Control** (PIC) binaries.
- sch-imus-strip.bms &mdash; Removes all but **BANK** and **PFSM** sections from PS2 .SCH files for vgmstream compatibility.
- tm2scanner.bms &mdash; Searches for and extracts .TM2 files in a container.
- twitchPopoutChroma &mdash; **twitch.tv** popout chat window effects for chroma keying.
- xbexexmzpe.bms &mdash; Windows, Xbox, Xbox 360 executable timestamps.

</details>

<details>
<summary>sims-console\</summary>

- todo

</details>

<details>
<summary>simpsons-game\</summary>

- TheSimpsonsGame_NewGen_LH2.py &mdash; **The Simpsons Game** (PS3, X360) .LH2 (2HCL) string file exporter and rebuilder.
- tex_TheSimpsonsGame_X360_itxd.py &mdash; **The Simpsons Game** Xbox 360 .ITXD Noesis texture plugin.
- tsg_hash.py &mdash; **The Simpsons Game** (PS3, X360) string label lookup hashing.

</details>
