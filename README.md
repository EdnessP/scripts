# My Scripts
This repository contains random scripts I've written at one point or another.  I've written additional info in the header for some of them just for uploading them here.  Most of them are written for QuickBMS, but there are a few Python (both regular and Noesis) scripts, and one GreaseMonkey script too.

If any problems arise, contact Edness#2203 on Discord.

## Script list
<details>
<summary>bully\</summary>

- BullyAE_encryption.py &mdash; Decrypt and encrypt **Bully: Anniversary Edition** .EFF, .MTL, .WDB, and .XML files.
- BullyAE_parse.py &mdash; Convert **Bully: Anniversary Edition** files' header info strings to usable lists and dictionaries.
- BullyAEjumptable.bms &mdash; **Bully: Anniversary Edition** developer savefile archive. (jumptable.bin)
- BullyX360img.bms &mdash; Extract **Bully: Scholarship Edition** Wii and Xbox 360 .IMG files.
- fmt_BullyAE.py &mdash; **Bully: Anniversary Edition** Noesis plugin for textures and models.

</details>

<details>
<summary>burnout\</summary>

- BLegendsDS.bms &mdash; Decompress LZSS compressed files in **Burnout Legends** NDS.
- bxv_palsplit.bms &mdash; Split and re-merge interleaved-grouped palettes from .BGV and .BTV files.
- fmt_Burnout3LRD.py &mdash; All-in-One Noesis plugin for the **Takedown**-era games (as well as **Black** and the PSP version of **NFS: Shift**).  Currently only supports textures.
- fmt_Burnout3LRD_changelog.txt &mdash; Update history for the Noesis plugin.
- GtHash.py &mdash; Python reimplementation of GtHash string hashing.
- GtIDstr.py &mdash; Python reimplementation of GtID EA string compression and decompression.
- txdscanner.bms &mdash; Extracts .TXDs from containers.  Only really needed for fonts stored in the executable.

</details>

<details>
<summary>other\</summary>

### GAME ARCHIVES

- activisionRPF.bms &mdash; **Activision Anthology** .RPF archives.
- atariGLM.bms &mdash; **Atari Anthology** .GLM archives.
- atetdbidk360.bms &mdash; **Adventure Time: Explore the Dungeon Because I Don't Know!** .PAK files.
- BombermanActZero.bms &mdash; **Bomberman: Act Zero** .DAT files.
- codfhpak.bms &mdash; **Call of Duty: Finest Hour** PS2 & Xbox .PAK files.
- cstrikeRDA.bms &mdash; **Castle Strike** .RDA archives.
- driversf-chnk.bms &mdash; **Driver: San Francisco** CHNK archives (.DNGC, .FCHUNK, .SP).
- jak1-2vagwad.bms &mdash; **Jak and Daxter: The Precursor Legacy** & **Jak II: Renegade** VAGWAD files.
- sdwww-mst.bms &mdash; **Scooby-Doo! Who's Watching Who?** .MST files.  (Has filenames unlike *sru-mst.bms*)
- sru-mst.bms &mdash; **Saints Row Undercover** .MST files.  (Has no filenames unlike *sdwww-mst.bms*)
- txbp-tm2.bms &mdash; **Yakuza 1** & **2** PS2 TXBP texture container to TM2 converter.

### GAME TEXTURES

- tex_BombermanActZero.py &mdash; **Bomberman: Act Zero** XPR2 textures extracted with the QuickBMS script.
- tex_HuneX_MF_PS2.py &mdash; PS2 Texture extraction for **HuneX** developed games.
- tex_SpongebobSurfnSkate.py &mdash; **SpongeBob's Surf & Skate Roadtrip** .XEN textures. May work on other Blitz Games archives too.
- tex_TheSimpsonsGame_X360_itxd.py &mdash; **The Simpsons Game** Xbox 360 .ITXD Noesis texture plugin.
- tex_Yakuza.py &mdash; **Yakuza** TXBP Noesis texture exporter plugin.

### MISCELLANEOUS

- 4bpp8bpp.bms &mdash; Convert 4-bit PS2 textures in a TM2 container to 8-bit.
- DVO3parser.bms &mdash; Prints **Driver: San Francisco** Wii .VO3 values.
- LingoTildeStr.py &mdash; SIA Tilde's Latvian **Lingo** string compression.
- LingoTildeWordList.txt &mdash; SIA Tilde's Latvian **Lingo** word list.
- multigim-split.bms &mdash; Split multiple GIM textures glued together, used in **Exit** PSP and possibly others.
- ms_timestamp.py &mdash; Python reimplementation of *xbexexmzpe.bms* written by jason098.
- sch-imus-strip.bms &mdash; Removes all but **BANK** and **PFSM** sections from PS2 .SCH files for vgmstream compatibility.
- TheSimpsonsGame_NewGen_LH2.py &mdash; Exports and rebuilds .LH (2HCL) string files from **The Simpsons Game** (PS3, X360).
- tm2scanner.bms &mdash; Searches for and extracts .TM2 files in a container.
- twitchPopoutChroma &mdash; **twitch.tv** popout chat window effects for chroma keying.
- xbexexmzpe.bms &mdash; Windows, Xbox, Xbox 360 executable timestamps.

</details>

<details>
<summary>sims-console\</summary>

- todo

</details>
