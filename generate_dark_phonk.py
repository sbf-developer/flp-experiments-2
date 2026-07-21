"""
Generate a complete dark phonk .flp by cloning the factory phonk mano template
and patching notes, playlist, sample paths, routing, names, and VSTs.

Song: "Dark Phonk" — Ab minor, 130 BPM, ~64 bars (~1:58).
"""
from __future__ import annotations

import struct
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

NOTE = struct.Struct("<iHH iHH b B b b b b b b")  # 24
# Pattern-clip layout matches phonk mano template. Last 8 bytes are NOT
# real floats for pattern clips — they are uint32 (0, length). Writing
# float 0.0/0.0 makes FL show zero-width "sliver" clips in the playlist.
CLIP = struct.Struct("<I H H I H H 2s H 4s I I")  # 32 pre-FL21
BAR = 384
BEAT = 96
STEP = 24  # 16th

MISSING_VSTS = (
    "Serum",
    "VU Meter",
    "Ozone",
    "CamelCrusher",
    "OTT",
    "Radiator",
    "Kickstart",
    "Valhalla",
)

PACK = Path(
    r"C:\Program Files\Image-Line\FL Studio 2024\Data\Patches\Packs\Phonk\phonk mano"
)
TEMPLATE = PACK / "phonk mano.flp"
OUT_DIR = Path(__file__).resolve().parent / "out"
OUT_FLP = OUT_DIR / "dark_phonk.flp"

# ---------------------------------------------------------------------------
# Channels (template indices) → local factory samples + display names
# ---------------------------------------------------------------------------

SAMPLE_MAP = {
    1: "!K - Cowbell (2).wav",
    2: "Kick Mano 2.wav",
    3: "Kick Mano 2.wav",
    4: "Clap Mano.wav",
    5: "Snare Mano.wav",
    6: "Snare Mano 2.wav",
    7: "Snare Mano 3.wav",
    8: "Snare Mano 4.wav",
    9: "Snare Fill Mano.wav",
    10: "Snare Fill Mano 2.wav",
    11: "Snare Fill Mano 3.wav",
    12: "Snare Fill Mano 4.wav",
    13: "Snare Fill Mano 5.wav",
    14: "Crash Mano.wav",
    15: "Crash Mano 2.wav",
    16: "FX Mano.wav",
    17: "FX Mano 2.wav",
    21: "808 (2).wav",
    22: "!K - Bass (6).wav",
    24: "Slowboy, lucaf, Crazy Mano - Brazilian Phonk Mano.mp3",
    25: "Slowboy, lucaf, Crazy Mano - Brazilian Phonk Mano [vocals].wav",
    26: "Slowboy, lucaf, Crazy Mano - Brazilian Phonk Mano.mp3",
    27: "Slowboy, lucaf, Crazy Mano - Brazilian Phonk Mano.mp3",
    28: "Slowboy, lucaf, Crazy Mano - Brazilian Phonk Mano [vocals].wav",
}

CHANNEL_NAMES = {
    1: "Cowbell",
    2: "Kick",
    3: "Kick Layer",
    4: "Clap",
    5: "Snare",
    6: "Snare 2",
    7: "Snare 3",
    8: "Snare 4",
    9: "Fill 1",
    10: "Fill 2",
    11: "Fill 3",
    12: "Fill 4",
    13: "Fill 5",
    14: "Crash",
    15: "Crash 2",
    16: "FX Rise",
    17: "FX Hit",
    21: "808",
    22: "Bass Shot",
}

COWBELL = 1
KICK = 2
KICK2 = 3
CLAP = 4
SNARE = 5
SNARE2 = 6
SNARE3 = 7
SNARE4 = 8
FILL1, FILL2, FILL3, FILL4, FILL5 = 9, 10, 11, 12, 13
CRASH, CRASH2 = 14, 15
FX, FX2 = 16, 17
BASS_808, BASS_SHOT = 21, 22

USED_CHANNELS = set(CHANNEL_NAMES)

# Ab minor pitch set (MIDI) — cowbell / 808 register from template
AB2, BB2, DB3, EB3, F3, GB3, AB3, BB3, DB4, EB4 = (
    44,
    46,
    49,
    51,
    53,
    54,
    56,
    58,
    61,
    63,
)
DRUM = 60  # C5 — default sampler root for one-shots


# ---------------------------------------------------------------------------
# FLP I/O
# ---------------------------------------------------------------------------


def read_varint(data: bytes, pos: int) -> tuple[int, int]:
    size, shift = 0, 0
    while pos < len(data):
        b = data[pos]
        pos += 1
        size |= (b & 0x7F) << shift
        if not (b & 0x80):
            break
        shift += 7
    return size, pos


def write_varint(size: int) -> bytes:
    out = bytearray()
    while True:
        byte = size & 0x7F
        size >>= 7
        if size:
            byte |= 0x80
        out.append(byte)
        if not size:
            break
    return bytes(out)


def parse_events(data: bytes) -> list[tuple[int, bytes]]:
    pos = 0
    events: list[tuple[int, bytes]] = []
    while pos < len(data):
        eid = data[pos]
        pos += 1
        if eid <= 63:
            payload = data[pos : pos + 1]
            pos += 1
        elif eid <= 127:
            payload = data[pos : pos + 2]
            pos += 2
        elif eid <= 191:
            payload = data[pos : pos + 4]
            pos += 4
        else:
            length, pos = read_varint(data, pos)
            payload = data[pos : pos + length]
            pos += length
        events.append((eid, payload))
    return events


def build_events(events: list[tuple[int, bytes]]) -> bytes:
    out = bytearray()
    for eid, payload in events:
        out.append(eid)
        if eid <= 63:
            out.extend(payload[:1])
        elif eid <= 127:
            out.extend(payload[:2])
        elif eid <= 191:
            out.extend(payload[:4])
        else:
            out.extend(write_varint(len(payload)))
            out.extend(payload)
    return bytes(out)


def read_flp(path: Path) -> tuple[bytes, list[tuple[int, bytes]]]:
    raw = path.read_bytes()
    assert raw[:4] == b"FLhd" and raw[14:18] == b"FLdt"
    return raw[:14], parse_events(raw[22:])


def write_flp(path: Path, header: bytes, events: list[tuple[int, bytes]]) -> None:
    payload = build_events(events)
    path.write_bytes(bytes(header) + b"FLdt" + struct.pack("<I", len(payload)) + payload)


def utf16_decode(p: bytes) -> str:
    if p.endswith(b"\x00\x00"):
        return p[:-2].decode("utf-16-le", "replace")
    return p.decode("utf-16-le", "replace")


def utf16_encode(s: str) -> bytes:
    return s.encode("utf-16-le") + b"\x00\x00"


def n(
    pos: int,
    key: int,
    length: int = 48,
    rack: int = 0,
    vel: int = 100,
) -> bytes:
    """Pack a normal (non-slide) note."""
    return NOTE.pack(
        pos, 0x4000, rack, length, key, 0, 120, 0, 64, -128, 64, max(1, min(127, vel)), -128, -128
    )


def pack_clip(pattern: int, start_bar: float, length_bars: float, track_iid: int) -> bytes:
    """Pack a pattern playlist clip onto playlist track ``track_iid`` (1-based).

    FL stores ``track_rvidx = 500 - track_iid``. Track iid 1 in the phonk mano
    template is DISABLED+LOCKED — never place clips there.
    """
    position = int(round(start_bar * BAR))
    length = int(round(length_bars * BAR))
    return CLIP.pack(
        position,
        0x5000,
        0x5000 + pattern,
        length,
        500 - track_iid,
        0,
        b"\x78\x00",
        0x8040,  # unmuted
        b"@d\x80\x80",
        0,
        length,
    )


# Playlist track IIDs from the phonk mano template (must be enabled lanes)
TR_COWBELL = 3  # "Cowbell"
TR_BASS = 4  # "Bass & Subscribe"
TR_DRUMS = 6  # "Kick"
TR_PERC = 9  # "Snares"
TR_FX = 14  # "FX"


def join_notes(hits: list[tuple]) -> bytes:
    """hits: (pos, key, length, rack, vel)"""
    return b"".join(n(*h) for h in hits)


# ---------------------------------------------------------------------------
# Patterns — each is playable alone in PAT mode and stacks cleanly in Song
# ---------------------------------------------------------------------------
# Track layout in playlist:
#   1 cowbell  2 drums  3 808  4 percussion spice  5 impacts/FX


def pat_cowbell_a() -> bytes:
    """PAT 1 — 4-bar main cowbell hook (Ab minor)."""
    hits = [
        # bar 1 — statement
        (0, AB3, 72, COWBELL, 118),
        (72, EB3, 48, COWBELL, 92),
        (144, DB3, 72, COWBELL, 105),
        (240, AB3, 48, COWBELL, 88),
        (288, BB3, 72, COWBELL, 108),
        # bar 2 — answer down
        (384, AB3, 72, COWBELL, 116),
        (456, F3, 48, COWBELL, 90),
        (528, EB3, 72, COWBELL, 102),
        (624, DB3, 48, COWBELL, 95),
        (696, EB3, 72, COWBELL, 100),
        # bar 3 — syncopated climb
        (768, AB3, 48, COWBELL, 118),
        (840, EB3, 48, COWBELL, 88),
        (888, GB3, 48, COWBELL, 95),
        (960, F3, 72, COWBELL, 105),
        (1056, EB3, 48, COWBELL, 90),
        (1104, DB3, 72, COWBELL, 100),
        # bar 4 — resolve + pickup
        (1152, AB3, 72, COWBELL, 120),
        (1224, BB2, 48, COWBELL, 92),
        (1296, DB3, 72, COWBELL, 105),
        (1392, EB3, 48, COWBELL, 95),
        (1440, AB3, 96, COWBELL, 118),
    ]
    return join_notes(hits)


def pat_cowbell_b() -> bytes:
    """PAT 2 — 4-bar variation (higher, more aggressive — for drop)."""
    hits = [
        (0, EB4, 48, COWBELL, 120),
        (72, DB4, 48, COWBELL, 100),
        (144, AB3, 72, COWBELL, 110),
        (240, BB3, 48, COWBELL, 95),
        (288, EB4, 72, COWBELL, 115),
        (384, DB4, 48, COWBELL, 118),
        (456, BB3, 48, COWBELL, 95),
        (528, AB3, 72, COWBELL, 108),
        (624, F3, 48, COWBELL, 90),
        (672, EB3, 72, COWBELL, 100),
        (768, AB3, 48, COWBELL, 120),
        (816, BB3, 48, COWBELL, 100),
        (864, DB4, 48, COWBELL, 105),
        (912, EB4, 72, COWBELL, 118),
        (1008, DB4, 48, COWBELL, 100),
        (1056, BB3, 48, COWBELL, 95),
        (1104, AB3, 72, COWBELL, 110),
        (1152, EB4, 48, COWBELL, 122),
        (1224, DB4, 48, COWBELL, 105),
        (1296, BB3, 48, COWBELL, 100),
        (1344, AB3, 48, COWBELL, 110),
        (1392, EB3, 48, COWBELL, 95),
        (1440, AB3, 96, COWBELL, 120),
    ]
    return join_notes(hits)


def pat_drums_intro() -> bytes:
    """PAT 3 — 1-bar sparse intro (kick pulse + soft clap)."""
    return join_notes(
        [
            (0, DRUM, 60, KICK, 110),
            (0, DRUM, 48, KICK2, 70),
            (192, DRUM, 60, KICK, 95),
            (288, DRUM, 48, CLAP, 75),
        ]
    )


def pat_drums_groove() -> bytes:
    """PAT 4 — 1-bar main phonk groove (layered kick/clap/snares)."""
    hits = [
        # Kick: 1 . . and | 3 . a .
        (0, DRUM, 60, KICK, 122),
        (0, DRUM, 48, KICK2, 85),
        (144, DRUM, 36, KICK, 78),
        (192, DRUM, 60, KICK, 115),
        (192, DRUM, 48, KICK2, 75),
        (336, DRUM, 36, KICK, 72),
        # Clap on 2 + 4
        (96, DRUM, 48, CLAP, 118),
        (288, DRUM, 48, CLAP, 120),
        # Snare body under clap + ghosts
        (96, DRUM, 36, SNARE, 70),
        (288, DRUM, 48, SNARE, 100),
        (240, DRUM, 24, SNARE2, 45),
        (360, DRUM, 24, SNARE2, 55),
        # Light snare3 tick on offbeats
        (168, DRUM, 20, SNARE3, 40),
        (312, DRUM, 20, SNARE3, 48),
    ]
    return join_notes(hits)


def pat_drums_half() -> bytes:
    """PAT 5 — 1-bar half-time break groove."""
    return join_notes(
        [
            (0, DRUM, 72, KICK, 118),
            (0, DRUM, 48, KICK2, 80),
            (192, DRUM, 72, KICK, 100),
            (96, DRUM, 60, CLAP, 110),
            (96, DRUM, 48, SNARE, 85),
            (288, DRUM, 36, SNARE2, 60),
            (336, DRUM, 24, SNARE3, 50),
        ]
    )


def pat_drums_fill_a() -> bytes:
    """PAT 6 — 1-bar snare roll fill into section."""
    hits = [
        (0, DRUM, 48, KICK, 115),
        (0, DRUM, 36, KICK2, 70),
        (96, DRUM, 36, CLAP, 100),
        (96, DRUM, 36, SNARE, 80),
    ]
    # crescendo 16ths across beat 3–4 using fill samples
    fills = [FILL1, FILL2, FILL1, FILL3, FILL2, FILL4, FILL3, FILL5]
    vels = [65, 72, 78, 85, 95, 105, 115, 127]
    for i, (rack, vel) in enumerate(zip(fills, vels)):
        hits.append((192 + i * 24, DRUM, 20, rack, vel))
    hits.append((0, DRUM, 96, CRASH, 70))  # soft swell under
    return join_notes(hits)


def pat_drums_fill_b() -> bytes:
    """PAT 7 — 1-bar punchy pre-drop fill."""
    hits = [
        (0, DRUM, 48, KICK, 120),
        (48, DRUM, 24, KICK, 70),
        (96, DRUM, 36, CLAP, 110),
        (144, DRUM, 24, SNARE, 80),
        (168, DRUM, 24, SNARE2, 90),
        (192, DRUM, 24, SNARE, 95),
        (216, DRUM, 24, SNARE3, 100),
        (240, DRUM, 24, SNARE, 108),
        (264, DRUM, 24, SNARE4, 115),
        (288, DRUM, 36, CLAP, 122),
        (288, DRUM, 36, SNARE, 110),
        (336, DRUM, 24, FILL5, 127),
        (360, DRUM, 24, FILL4, 120),
        (0, DRUM, 120, FX, 90),
    ]
    return join_notes(hits)


def pat_808_verse() -> bytes:
    """PAT 8 — 4-bar verse 808 (Ab–Eb–Bb–Db walk)."""
    hits = [
        # bar 1 Ab
        (0, AB2, 168, BASS_808, 122),
        (0, AB3, 72, BASS_SHOT, 88),
        (192, AB2, 120, BASS_808, 100),
        # bar 2 Eb / Db
        (384, EB3, 168, BASS_808, 118),
        (384, EB3, 60, BASS_SHOT, 80),
        (576, DB3, 140, BASS_808, 108),
        # bar 3 Bb / Ab
        (768, BB2, 160, BASS_808, 118),
        (768, AB3, 60, BASS_SHOT, 85),
        (960, AB2, 140, BASS_808, 112),
        # bar 4 Db → Bb → Ab
        (1152, DB3, 120, BASS_808, 118),
        (1152, DB3, 60, BASS_SHOT, 88),
        (1296, BB2, 88, BASS_808, 100),
        (1392, AB2, 120, BASS_808, 122),
    ]
    return join_notes(hits)


def pat_808_drop() -> bytes:
    """PAT 9 — 4-bar drop 808 (harder, more stabs)."""
    hits = [
        # bar 1 — Ab with mid stab
        (0, AB2, 150, BASS_808, 127),
        (0, AB3, 84, BASS_SHOT, 105),
        (144, AB2, 40, BASS_808, 85),
        (192, AB3, 90, BASS_808, 112),
        (288, AB2, 72, BASS_808, 100),
        # bar 2 — low Eb
        (384, 39, 170, BASS_808, 125),  # Eb2
        (384, EB3, 72, BASS_SHOT, 95),
        (576, AB2, 140, BASS_808, 115),
        # bar 3 — Bb bounce
        (768, BB2, 150, BASS_808, 122),
        (768, AB3, 60, BASS_SHOT, 100),
        (912, DB3, 60, BASS_808, 95),
        (960, AB2, 150, BASS_808, 120),
        # bar 4 — sub Ab + walk
        (1152, 37, 170, BASS_808, 127),  # low Ab-ish
        (1152, AB2, 84, BASS_SHOT, 110),
        (1344, AB2, 88, BASS_808, 112),
        (1440, DB3, 72, BASS_808, 100),
        (1440, EB3, 48, BASS_SHOT, 90),
    ]
    return join_notes(hits)


def pat_808_break() -> bytes:
    """PAT 10 — 4-bar minimal 808 (breathing room)."""
    return join_notes(
        [
            (0, AB2, 280, BASS_808, 110),
            (384, EB3, 280, BASS_808, 100),
            (768, BB2, 280, BASS_808, 105),
            (1152, AB2, 280, BASS_808, 115),
            (0, AB3, 96, BASS_SHOT, 70),
            (1152, AB3, 96, BASS_SHOT, 75),
        ]
    )


def pat_perc_spice() -> bytes:
    """PAT 11 — 1-bar extra percussion for drop density."""
    return join_notes(
        [
            (48, DRUM, 20, SNARE4, 50),
            (120, DRUM, 20, SNARE3, 55),
            (216, DRUM, 20, SNARE4, 48),
            (264, DRUM, 20, SNARE2, 60),
            (312, DRUM, 20, SNARE3, 52),
            (348, DRUM, 18, SNARE4, 58),
        ]
    )


def pat_impact() -> bytes:
    """PAT 12 — 1-bar section impact (crash + FX)."""
    return join_notes(
        [
            (0, DRUM, 240, CRASH, 115),
            (0, DRUM, 180, CRASH2, 90),
            (0, DRUM, 192, FX, 100),
            (192, DRUM, 120, FX2, 85),
            (0, DRUM, 72, KICK, 127),
            (0, DRUM, 48, KICK2, 100),
        ]
    )


def pat_cowbell_sparse() -> bytes:
    """PAT 13 — 4-bar sparse cowbell (intro/outro)."""
    hits = [
        (0, AB3, 96, COWBELL, 100),
        (192, EB3, 72, COWBELL, 80),
        (384, DB3, 96, COWBELL, 95),
        (576, AB3, 72, COWBELL, 85),
        (768, BB3, 96, COWBELL, 100),
        (960, EB3, 72, COWBELL, 80),
        (1152, AB3, 120, COWBELL, 105),
        (1392, EB3, 72, COWBELL, 75),
    ]
    return join_notes(hits)


PATTERN_NOTES = {
    1: pat_cowbell_a,
    2: pat_cowbell_b,
    3: pat_drums_intro,
    4: pat_drums_groove,
    5: pat_drums_half,
    6: pat_drums_fill_a,
    7: pat_drums_fill_b,
    8: pat_808_verse,
    9: pat_808_drop,
    10: pat_808_break,
    11: pat_perc_spice,
    12: pat_impact,
    13: pat_cowbell_sparse,
}

PATTERN_NAMES = {
    1: "Cowbell A",
    2: "Cowbell B",
    3: "Drums Intro",
    4: "Drums Groove",
    5: "Drums Half",
    6: "Fill A",
    7: "Fill B",
    8: "808 Verse",
    9: "808 Drop",
    10: "808 Break",
    11: "Perc Spice",
    12: "Impact",
    13: "Cowbell Sparse",
}


# ---------------------------------------------------------------------------
# Arrangement — 64 bars @ 130 BPM ≈ 1:58
# ---------------------------------------------------------------------------
#
#  0–7    INTRO     sparse cowbell + intro drums → groove enters
#  8–23   VERSE     full groove + cowbell A + 808 verse
#  24–31  BREAK     half-time + sparse 808 + fill into drop
#  32–47  DROP      cowbell B + groove + spice + 808 drop
#  48–55  BRIDGE    cowbell A + half drums + 808 break
#  56–63  OUTRO     sparse + impacts fading


def build_playlist() -> bytes:
    """Long looping clips on ENABLED template playlist tracks."""
    clips: list[bytes] = []

    def add(pat: int, start: float, length: float, track: int) -> None:
        clips.append(pack_clip(pat, start, length, track))

    # ===== INTRO 0–8 =====
    add(13, 0, 4, TR_COWBELL)
    add(1, 4, 4, TR_COWBELL)
    add(3, 0, 4, TR_DRUMS)
    add(4, 4, 3, TR_DRUMS)
    add(6, 7, 1, TR_DRUMS)
    add(10, 4, 4, TR_BASS)
    add(12, 4, 1, TR_FX)

    # ===== VERSE 8–24 =====
    add(1, 8, 16, TR_COWBELL)
    add(4, 8, 15, TR_DRUMS)
    add(6, 23, 1, TR_DRUMS)
    add(8, 8, 16, TR_BASS)
    add(12, 8, 1, TR_FX)
    add(12, 16, 1, TR_FX)

    # ===== BREAK 24–32 =====
    add(13, 24, 4, TR_COWBELL)
    add(1, 28, 3, TR_COWBELL)
    add(5, 24, 6, TR_DRUMS)
    add(3, 30, 1, TR_DRUMS)
    add(7, 31, 1, TR_DRUMS)
    add(10, 24, 7, TR_BASS)
    add(12, 24, 1, TR_FX)
    add(12, 31, 1, TR_FX)

    # ===== DROP 32–48 =====
    add(2, 32, 16, TR_COWBELL)
    add(4, 32, 7, TR_DRUMS)
    add(6, 39, 1, TR_DRUMS)
    add(4, 40, 7, TR_DRUMS)
    add(7, 47, 1, TR_DRUMS)
    add(9, 32, 16, TR_BASS)
    add(11, 32, 16, TR_PERC)
    add(12, 32, 1, TR_FX)
    add(12, 40, 1, TR_FX)

    # ===== BRIDGE 48–56 =====
    add(1, 48, 4, TR_COWBELL)
    add(13, 52, 4, TR_COWBELL)
    add(5, 48, 6, TR_DRUMS)
    add(3, 54, 1, TR_DRUMS)
    add(7, 55, 1, TR_DRUMS)
    add(10, 48, 4, TR_BASS)
    add(8, 52, 3, TR_BASS)
    add(12, 48, 1, TR_FX)
    add(12, 55, 1, TR_FX)

    # ===== OUTRO 56–64 =====
    add(2, 56, 4, TR_COWBELL)
    add(13, 60, 4, TR_COWBELL)
    add(4, 56, 4, TR_DRUMS)
    add(3, 60, 3, TR_DRUMS)
    add(5, 63, 1, TR_DRUMS)
    add(9, 56, 4, TR_BASS)
    add(10, 60, 4, TR_BASS)
    add(11, 56, 4, TR_PERC)
    add(12, 56, 1, TR_FX)
    add(12, 60, 1, TR_FX)

    return b"".join(clips)


def enable_all_playlist_tracks(payload: bytes) -> bytes:
    """Force playlist track enabled + unlocked (event 238 TrackData, 66 bytes)."""
    if len(payload) < 48:
        return payload
    data = bytearray(payload)
    data[12] = 1  # enabled
    if len(data) > 21:
        data[21] = 0  # content_locked
    if len(data) > 46:
        data[46] = 0  # grouped
    if len(data) > 47:
        data[47] = 0  # locked
    return bytes(data)


# ---------------------------------------------------------------------------
# Patching
# ---------------------------------------------------------------------------


def strip_missing_vsts(events: list) -> list[tuple[int, bytes]]:
    cleaned: list[tuple[int, bytes] | None] = list(events)
    for i, (eid, p) in enumerate(events):
        if eid == 203:
            name = utf16_decode(p)
            if any(m in name for m in MISSING_VSTS):
                cleaned[i] = None
        elif eid == 213:
            if any(
                m.encode("utf-16-le") in p or m.encode("utf-8") in p
                for m in MISSING_VSTS
            ):
                cleaned[i] = None
    return [e for e in cleaned if e is not None]


def patch_project(events: list[tuple[int, bytes]]) -> list[tuple[int, bytes]]:
    events = strip_missing_vsts(events)
    out: list[tuple[int, bytes]] = []
    current_chan: int | None = None
    current_pat: int | None = None
    notes_replaced: set[int] = set()
    chan_named: set[int] = set()
    playlist_done = False
    title_done = False

    for eid, payload in events:
        if eid == 194 and not title_done:
            out.append((194, utf16_encode("Dark Phonk")))
            title_done = True
            continue

        if eid == 64:
            current_chan = struct.unpack("<H", payload)[0]
            current_pat = None
            out.append((eid, payload))
            continue

        if eid == 65:
            current_pat = struct.unpack("<H", payload)[0]
            current_chan = None
            out.append((eid, payload))
            continue

        if eid == 224:
            if current_pat in PATTERN_NOTES and current_pat not in notes_replaced:
                out.append((224, PATTERN_NOTES[current_pat]()))
                notes_replaced.add(current_pat)
            elif current_pat in PATTERN_NOTES:
                continue
            else:
                out.append((224, b""))
            continue

        if eid == 233:
            out.append((233, build_playlist()))
            playlist_done = True
            continue

        if eid == 238:  # playlist track data — unmute/unlock every lane
            out.append((238, enable_all_playlist_tracks(payload)))
            continue

        if eid == 196 and current_chan is not None:
            if current_chan in SAMPLE_MAP:
                sample_path = PACK / SAMPLE_MAP[current_chan]
                out.append((196, utf16_encode(str(sample_path))))
            else:
                out.append((eid, payload))
            continue

        if eid == 203 and current_chan is not None and current_chan in CHANNEL_NAMES:
            if current_chan not in chan_named:
                out.append((203, utf16_encode(CHANNEL_NAMES[current_chan])))
                chan_named.add(current_chan)
            else:
                out.append((eid, payload))
            continue

        if eid == 22 and current_chan is not None:
            if current_chan in USED_CHANNELS or current_chan in SAMPLE_MAP:
                out.append((22, struct.pack("<b", 0)))
            else:
                out.append((eid, payload))
            continue

        out.append((eid, payload))

    if not playlist_done:
        out.append((233, build_playlist()))

    for pat, builder in PATTERN_NOTES.items():
        if pat not in notes_replaced:
            out.append((65, struct.pack("<H", pat)))
            out.append((224, builder()))
            notes_replaced.add(pat)

    return out


def verify(path: Path) -> None:
    _header, events = read_flp(path)
    problems: list[str] = []
    chan = None
    pat = None
    pat_notes: dict[int, int] = {}
    playlist_clips = 0
    racks_used: set[int] = set()

    for eid, p in events:
        if eid == 64:
            chan = struct.unpack("<H", p)[0]
        elif eid == 65:
            pat = struct.unpack("<H", p)[0]
        elif eid == 196 and chan in USED_CHANNELS:
            sp = utf16_decode(p)
            if not Path(sp).exists():
                problems.append(f"missing sample ch{chan}: {sp}")
            else:
                print(f"  ch{chan:2d} OK  {Path(sp).name}")
        elif eid == 22 and chan in USED_CHANNELS:
            if struct.unpack("<b", p)[0] != 0:
                problems.append(f"ch{chan} not master-routed")
        elif eid == 224:
            nnotes = len(p) // 24
            if pat is not None:
                pat_notes[pat] = nnotes
            for i in range(nnotes):
                vals = NOTE.unpack_from(p, i * 24)
                if vals[1] & 0x0008:
                    problems.append(f"slide note in pat{pat} pos={vals[0]}")
                racks_used.add(vals[2])
                if vals[11] <= 0:
                    problems.append(f"zero/neg velocity pat{pat}")
        elif eid == 233:
            playlist_clips = len(p) // 32
            if len(p) % 32:
                problems.append(f"playlist size not multiple of 32 ({len(p)})")
            for i in range(playlist_clips):
                vals = CLIP.unpack_from(p, i * 32)
                idx = vals[2]
                length = vals[3]
                start_u, end_u = vals[9], vals[10]
                if idx < 0x5000:
                    problems.append(f"playlist#{i} bare index {idx}")
                else:
                    pn = idx - 0x5000
                    if pn not in PATTERN_NOTES:
                        problems.append(f"playlist#{i} refs missing pat {pn}")
                if length < BAR // 4:
                    problems.append(f"playlist#{i} tiny length {length} ticks")
                # Pattern clips: end uint must equal length (template convention)
                if end_u != length or start_u != 0:
                    problems.append(
                        f"playlist#{i} bad pattern offsets start_u={start_u} end_u={end_u} len={length}"
                    )
                if vals[7] & 0x2000:
                    problems.append(f"playlist#{i} muted flag set")
                track_iid = 500 - vals[4]
                if track_iid == 1:
                    problems.append(f"playlist#{i} on disabled track 1")
                if track_iid not in (
                    TR_COWBELL,
                    TR_BASS,
                    TR_DRUMS,
                    TR_PERC,
                    TR_FX,
                ):
                    problems.append(f"playlist#{i} unexpected track {track_iid}")
        elif eid == 238 and len(p) >= 13:
            iid = struct.unpack_from("<I", p, 0)[0]
            if iid <= 20 and p[12] != 1:
                problems.append(f"playlist track {iid} still disabled")
        elif eid == 203:
            name = utf16_decode(p)
            if any(m in name for m in MISSING_VSTS):
                problems.append(f"VST name left: {name}")
        elif eid == 213:
            for m in MISSING_VSTS:
                if m.encode("utf-8") in p or m.encode("utf-16-le") in p:
                    problems.append(f"VST state left: {m}")
                    break

    print(f"\n  playlist clips: {playlist_clips}")
    print("  patterns:")
    for pn in sorted(PATTERN_NOTES):
        count = pat_notes.get(pn, 0)
        status = "OK" if count > 0 else "EMPTY"
        print(f"    [{status}] pat{pn:2d} {PATTERN_NAMES[pn]:16s} notes={count}")
        if count == 0:
            problems.append(f"pattern {pn} empty")

    missing_racks = USED_CHANNELS - racks_used
    # vocals etc. in SAMPLE_MAP but not USED — fine
    unused_sound = {c for c in USED_CHANNELS if c not in racks_used}
    if unused_sound:
        print(f"  unused channels (ok if intentional): {sorted(unused_sound)}")

    if problems:
        print("\nPROBLEMS:")
        for pr in problems:
            print(" -", pr)
        raise SystemExit(1)
    print("\nVERIFY OK — open in Song mode")


def main() -> None:
    if not TEMPLATE.exists():
        raise SystemExit(f"Template not found: {TEMPLATE}")

    for ch, name in SAMPLE_MAP.items():
        p = PACK / name
        if ch in USED_CHANNELS and not p.exists():
            raise SystemExit(f"Required sample missing ch{ch}: {p}")

    header, events = read_flp(TEMPLATE)
    patched = patch_project(events)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    write_flp(OUT_FLP, header, patched)
    print(f"Wrote {OUT_FLP} ({OUT_FLP.stat().st_size:,} bytes)")
    verify(OUT_FLP)

    # also copy into FL Studio Projects
    projects = (
        Path.home()
        / "Documents"
        / "Image-Line"
        / "FL Studio"
        / "Projects"
        / "dark_phonk"
        / "dark_phonk.flp"
    )
    projects.parent.mkdir(parents=True, exist_ok=True)
    projects.write_bytes(OUT_FLP.read_bytes())
    print(f"Copied → {projects}")


if __name__ == "__main__":
    main()
