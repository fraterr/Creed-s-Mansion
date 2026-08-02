#!/usr/bin/env python3
"""
sf2-mithril.py — Shining Force II mithril weapon predictor.

Everything in this file was read out of the US ROM of Shining Force II
(MD5 6473b1505334ef5620d13191c18251fe) and is reproduced here so you can
check it against your own copy:

    $001600   the 16-bit LCG   seed = (seed * 13 + 7) mod 65536
                               value = floor(seed * range / 65536)
    $FFDEA4   the seed, in work RAM
    $021EDA   the routine that picks the mithril weapon
    $021F62   class -> group table
    $021F92   group -> four (probability, item ID) pairs
    $FFF7A8   the queue of weapons the smith is currently forging

Usage
    python3 sf2-mithril.py 0x44BE                 what you get from this seed
    python3 sf2-mithril.py 0x44BE MMNK            ...for a Master Monk
    python3 sf2-mithril.py 0x44BE HERO --frames 120
    python3 sf2-mithril.py --odds                 exhaustive odds over all seeds

Read the seed from $FFDEA4 with your emulator's RAM watch while the smith's
text box is open. It advances one step per frame while the box waits for you
to press a button, so "wait n more frames before confirming" means "advance
the seed n more steps".

Public domain. Creed's Mansion — https://fraterr.github.io/Creed-s-Mansion/
"""

import sys
from collections import Counter

MASK = 0xFFFF

ITEMS = {
    0x1E: "Misty Knuckles", 0x1F: "Giant Knuckles",
    0x28: "Heat Axe", 0x29: "Atlas Axe", 0x2A: "Ground Axe", 0x2B: "Rune Axe",
    0x34: "Buster Shot", 0x35: "Hyper Cannon", 0x36: "Grand Cannon",
    0x41: "Critical Sword", 0x42: "Battle Sword", 0x44: "Counter Sword",
    0x45: "Levanter",
    0x50: "Valkyrie", 0x51: "Holy Lance", 0x52: "Mist Javelin", 0x53: "Halberd",
    0x5F: "Great Rod", 0x60: "Supply Staff", 0x61: "Holy Staff",
    0x62: "Freeze Staff", 0x63: "Goddess Staff", 0x64: "Mystery Staff",
    0x6B: "Katana", 0x6C: "Ninja Katana", 0x6D: "Gisarme",
}

# group index -> the classes that map to it, exactly as at ROM $021F62
GROUP_CLASSES = {
    0: ["HERO", "BDBT"],
    1: ["PLDN", "PGNT"],
    2: ["GLDT"],
    3: ["WIZ", "SORC"],
    4: ["VICR"],
    5: ["SNIP", "BRGN", "BWNT"],
    6: ["NINJ"],
    7: ["MMNK"],
}

# group index -> four (probability parameter, item ID) pairs, ROM $021F92
GROUP_TABLE = {
    0: [(16, 0x45), (8, 0x44), (4, 0x42), (1, 0x41)],
    1: [(16, 0x51), (8, 0x53), (4, 0x52), (1, 0x50)],
    2: [(16, 0x2B), (8, 0x2A), (4, 0x29), (1, 0x28)],
    3: [(16, 0x64), (8, 0x62), (4, 0x5F), (1, 0x60)],
    4: [(16, 0x64), (8, 0x63), (4, 0x5F), (1, 0x61)],
    5: [(16, 0x36), (8, 0x36), (4, 0x35), (1, 0x34)],
    6: [(16, 0x6D), (8, 0x6C), (4, 0x6B), (1, 0x41)],
    7: [(16, 0x1F), (8, 0x1F), (4, 0x1E), (1, 0x1E)],
}

CLASS_TO_GROUP = {c: g for g, cs in GROUP_CLASSES.items() for c in cs}


def step(seed):
    """One advance of the generator at ROM $001600."""
    return (seed * 13 + 7) & MASK


def roll(seed, rng_range):
    """Returns (new_seed, value) exactly as $001600 does."""
    seed = step(seed)
    return seed, (seed * rng_range) >> 16


def choose(seed, klass=None):
    """
    Runs the routine at $021EDA. Returns (item_id, seed_after, trace).
    klass is a four-letter class label. None or an unlisted label takes the
    coin-flip branch at $021F02, exactly as the game does.
    """
    trace = []
    group = CLASS_TO_GROUP.get(klass)
    if group is None:
        before = seed
        seed, v = roll(seed, 2)
        group = 0 if v != 0 else 2
        trace.append((before, 2, v, "class not listed -> group %d" % group))
    for probability, item in GROUP_TABLE[group]:
        before = seed
        seed, v = roll(seed, probability)
        trace.append((before, probability, v, ITEMS.get(item, "$%02X" % item)))
        if v == 0:
            return item, seed, trace
    return item, seed, trace


def tier_of(seed, klass):
    """Which of the four table entries this seed lands on, 0 = best."""
    group = CLASS_TO_GROUP.get(klass)
    if group is None:
        seed, v = roll(seed, 2)
        group = 0 if v != 0 else 2
    for i, (probability, _item) in enumerate(GROUP_TABLE[group]):
        seed, v = roll(seed, probability)
        if v == 0:
            return i
    return 3


def report(seed, klass, frames):
    group = CLASS_TO_GROUP.get(klass)
    print("seed $%04X   class %s   group %s" %
          (seed, klass or "(unlisted)",
           group if group is not None else "decided by a coin flip"))
    print()
    item, after, trace = choose(seed, klass)
    print("  what happens right now")
    for before, rng_range, value, what in trace:
        mark = "<-- taken" if value == 0 else ""
        print("    seed $%04X  Random(%2d) -> %-2d  %-16s %s"
              % (before, rng_range, value, what, mark))
    print("    result: %s   seed afterwards $%04X" %
          (ITEMS.get(item, "$%02X" % item), after))
    print()

    if group is None:
        print("  This class is not in the table, so the first roll decides")
        print("  between the sword group and the axe group before anything else.")
        print()

    best = GROUP_TABLE[group][0][1] if group is not None else None
    print("  the next %d frames of delay" % frames)
    hits = []
    s = seed
    elided = False
    for f in range(frames):
        item, _, _ = choose(s, klass)
        top = item == best
        if top:
            hits.append(f)
        if f < 24 or top:
            print("    +%-4d seed $%04X  ->  %s%s"
                  % (f, s, ITEMS.get(item, "$%02X" % item), "   TOP TIER" if top else ""))
        elif not elided:
            print("    ...")
            elided = True
        s = step(s)
    if best is not None:
        print()
        if hits:
            print("  wait %d frame(s) longer before confirming to get %s."
                  % (hits[0], ITEMS[best]))
        else:
            print("  no top-tier result within %d frames, widen the window." % frames)


def odds():
    print("Exhaustive walk over all 65536 possible seeds.")
    print()
    for g in sorted(GROUP_TABLE):
        counts = Counter()
        for s in range(0x10000):
            seed = s
            for i, (probability, item) in enumerate(GROUP_TABLE[g]):
                seed, v = roll(seed, probability)
                if v == 0:
                    counts[item] += 1
                    break
            else:
                counts[item] += 1
        print("group %d  (%s)" % (g, ", ".join(GROUP_CLASSES[g])))
        for item, n in counts.most_common():
            print("    %-16s %8.4f%%" % (ITEMS.get(item, "$%02X" % item),
                                         100.0 * n / 0x10000))
        print()


def main(argv):
    if "--odds" in argv:
        odds()
        return 0
    if len(argv) < 2:
        print(__doc__.strip())
        return 1
    seed = int(argv[1], 0) & MASK
    klass = None
    frames = 240
    rest = [a for a in argv[2:] if not a.startswith("--")]
    if rest:
        klass = rest[0].upper()
    if "--frames" in argv:
        frames = int(argv[argv.index("--frames") + 1])
    report(seed, klass, frames)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
