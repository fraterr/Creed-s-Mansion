# Creed's Mansion

A small static site about role-playing games, the romhacks that grow out of them, and
whatever else earns a room in the house.

Live at **https://fraterr.github.io/Creed-s-Mansion/**
(enable GitHub Pages under *Settings → Pages → Deploy from a branch → `main` / root*
if the site is not up yet).

## What's here

```
index.html                                   the mansion's front door
games/shining-force/                         the Shining Force room
games/shining-force/turn-queue-mod/          write-up for the Turn Queue & Tactics romhack
assets/style.css                             the whole theme, one file
assets/img/                                  screenshots (captured from an emulator)
assets/fonts/                                the game's dialogue typeface, traced to a webfont
downloads/                                   the IPS patch
```

No build step, no framework, no tracking. Plain HTML and one stylesheet: clone it, open
`index.html` in a browser, and what you see is what ships.

The body text is set in `SF Dialogue`, a webfont built for this site by tracing the
16x14 bitmaps of the Mega Drive variable-width font into outlines. One source pixel maps
to one CSS pixel at `font-size: 14px`, which is why the text is pixel-exact at that size.

## The Shining Force patch

`downloads/ShiningForce_TurnQueue_v13.ips` applies to **Shining Force (USA)** for the Sega
Mega Drive / Genesis — 1,572,864 bytes, MD5 `4b4acbe75ff7aaeb534ab78ed95910d1`. It adds a
visible turn-order bar, a difficulty choice at New Game, EXP overflow on level-up, and
per-character kill/death counters.

The patch is built as a set of same-size hooks against
[SF1DISASM](https://github.com/hasseily/SF1DISASM); the assembly diff is available on
request and will land here in a later commit.

**No ROM is distributed in this repository, and none will be.** Bring your own copy of a
game you own.

## Licence and credits

Site content and the romhack source are mine to share. Shining Force is © SEGA / Camelot
Software Planning; this is an unaffiliated fan project that claims no rights over the
original game. The patch is built on the work of the SF1DISASM disassembly community.
