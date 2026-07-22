"""
Generate "Covenant Strike" — hardstyle × dark phonk .flp.

Clone-and-patch of factory phonk mano. Fixed playlist lane map (phonk mano
iid 2=Cowbell, 3=Bass, 5=Kick, 8=Snares, 13=FX — NOT the off-by-one map).

Song: F# minor, 150 BPM, 64 bars (~1:42). Clear half-time verses →
hardtekk build → hardstyle drop → ultra break → drop 2 → outro.
"""
from __future__ import annotations

import struct
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

NOTE = struct.Struct("<iHH iHH b B b b b b b b")  # 24
CLIP = struct.Struct("<I H H I H H 2s H 4s I I")  # 32 pre-FL21
BAR = 384
BPM = 150

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
OUT_FLP = OUT_DIR / "covenant_strike.flp"
SONG_TITLE = "Covenant Strike"

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

# F# minor
FS2, A2, B2, CS3, E3, FS3, A3, B3, CS4, FS4 = (
    42,
    45,
    47,
    49,
    52,
    54,
    57,
    59,
    61,
    66,
)
DRUM = 60

# phonk mano playlist lanes (verified from TrackData iid + TrackName)
# iid 1 = "Original" — disabled in template; leave empty
TR_COWBELL = 2  # Cowbell
TR_BASS = 3  # Bass & Subscribe
TR_DRUMS = 5  # Kick
TR_PERC = 8  # Snares
TR_FX = 13  # FX

TRACK_RENAMES = {
    1: "—",
    2: "Cowbell",
    3: "808 Bass",
    4: "—",
    5: "Drums",
    6: "—",
    7: "—",
    8: "Perc",
    9: "—",
    10: "—",
    11: "—",
    12: "—",
    13: "FX",
    14: "—",
}


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


def n(pos: int, key: int, length: int = 48, rack: int = 0, vel: int = 100) -> bytes:
    return NOTE.pack(
        pos,
        0x4000,
        rack,
        length,
        key,
        0,
        120,
        0,
        64,
        -128,
        64,
        max(1, min(127, vel)),
        -128,
        -128,
    )


def pack_clip(pattern: int, start_bar: float, length_bars: float, track_iid: int) -> bytes:
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
        0x8040,
        b"@d\x80\x80",
        0,
        length,
    )


def join_notes(hits: list[tuple]) -> bytes:
    return b"".join(n(*h) for h in hits)


# ---------------------------------------------------------------------------
# Patterns — sparse hooks, clear roles (no density soup)
# ---------------------------------------------------------------------------


def pat_cowbell_hook() -> bytes:
    """PAT 1 — 4-bar main hook (room between hits)."""
    return join_notes(
        [
            (0, FS3, 96, COWBELL, 118),
            (192, CS3, 72, COWBELL, 95),
            (384, A3, 96, COWBELL, 110),
            (576, B2, 72, COWBELL, 90),
            (768, FS3, 72, COWBELL, 120),
            (912, E3, 72, COWBELL, 100),
            (1056, CS3, 72, COWBELL, 95),
            (1152, FS3, 120, COWBELL, 122),
            (1392, CS4, 72, COWBELL, 105),
        ]
    )


def pat_cowbell_drop() -> bytes:
    """PAT 2 — 4-bar drop accents (not a wall — answers the kick)."""
    return join_notes(
        [
            (0, CS4, 60, COWBELL, 120),
            (192, FS3, 72, COWBELL, 108),
            (384, FS4, 60, COWBELL, 122),
            (576, CS4, 72, COWBELL, 105),
            (768, A3, 60, COWBELL, 115),
            (960, FS3, 72, COWBELL, 100),
            (1152, CS4, 60, COWBELL, 124),
            (1344, FS3, 96, COWBELL, 110),
        ]
    )


def pat_cowbell_sparse() -> bytes:
    """PAT 3 — 4-bar intro/outro."""
    return join_notes(
        [
            (0, FS3, 144, COWBELL, 90),
            (576, CS3, 120, COWBELL, 75),
            (1152, FS3, 168, COWBELL, 95),
        ]
    )


def pat_drums_intro() -> bytes:
    """PAT 4 — 1-bar soft pulse."""
    return join_notes(
        [
            (0, DRUM, 72, KICK, 100),
            (0, DRUM, 48, KICK2, 60),
            (288, DRUM, 36, CLAP, 50),
        ]
    )


def pat_drums_half() -> bytes:
    """PAT 5 — 1-bar phonk half-time (verse)."""
    return join_notes(
        [
            (0, DRUM, 84, KICK, 122),
            (0, DRUM, 48, KICK2, 85),
            (192, DRUM, 60, KICK, 100),
            (96, DRUM, 48, CLAP, 118),
            (96, DRUM, 36, SNARE, 70),
            (288, DRUM, 48, CLAP, 120),
            (288, DRUM, 48, SNARE, 90),
            (336, DRUM, 20, SNARE2, 45),
        ]
    )


def pat_drums_hardstyle() -> bytes:
    """PAT 6 — 1-bar hardstyle 4-on-floor + clap on 2/4."""
    return join_notes(
        [
            (0, DRUM, 56, KICK, 127),
            (0, DRUM, 40, KICK2, 95),
            (96, DRUM, 56, KICK, 120),
            (96, DRUM, 32, KICK2, 80),
            (192, DRUM, 56, KICK, 127),
            (192, DRUM, 40, KICK2, 90),
            (288, DRUM, 56, KICK, 120),
            (288, DRUM, 32, KICK2, 80),
            (96, DRUM, 36, CLAP, 105),
            (288, DRUM, 36, CLAP, 110),
            (288, DRUM, 28, SNARE, 75),
        ]
    )


def pat_drums_ultra() -> bytes:
    """PAT 7 — 1-bar ultra-slowed break."""
    return join_notes(
        [
            (0, DRUM, 120, KICK, 115),
            (0, DRUM, 60, KICK2, 80),
            (192, DRUM, 40, CLAP, 55),
        ]
    )


def pat_drums_build() -> bytes:
    """PAT 8 — 1-bar hardtekk roll (into drop)."""
    hits = [
        (0, DRUM, 48, KICK, 110),
        (0, DRUM, 160, FX, 100),
    ]
    fills = [FILL1, FILL2, FILL1, FILL3, FILL2, FILL4, FILL3, FILL5,
             FILL2, FILL3, FILL4, FILL5, FILL3, FILL4, FILL5, FILL5]
    vels = list(range(50, 50 + 16 * 4, 4))
    for i, (rack, vel) in enumerate(zip(fills, vels)):
        hits.append((i * 24, DRUM, 18, rack, min(127, vel)))
    return join_notes(hits)


def pat_drums_fill() -> bytes:
    """PAT 9 — 1-bar punch + crash into section."""
    return join_notes(
        [
            (0, DRUM, 48, KICK, 120),
            (96, DRUM, 36, CLAP, 105),
            (144, DRUM, 24, SNARE, 85),
            (192, DRUM, 24, SNARE2, 100),
            (216, DRUM, 24, SNARE3, 110),
            (240, DRUM, 24, SNARE, 115),
            (264, DRUM, 24, SNARE4, 120),
            (288, DRUM, 40, CLAP, 124),
            (288, DRUM, 36, SNARE, 110),
            (336, DRUM, 24, FILL5, 127),
            (0, DRUM, 200, CRASH, 110),
            (0, DRUM, 120, FX, 95),
        ]
    )


def pat_808_verse() -> bytes:
    """PAT 10 — 4-bar verse 808 (held, breathing)."""
    return join_notes(
        [
            (0, FS2, 300, BASS_808, 118),
            (0, FS3, 72, BASS_SHOT, 70),
            (384, E3, 280, BASS_808, 110),
            (768, CS3, 280, BASS_808, 112),
            (768, CS3, 60, BASS_SHOT, 75),
            (1152, B2, 200, BASS_808, 115),
            (1392, FS2, 120, BASS_808, 120),
        ]
    )


def pat_808_drop() -> bytes:
    """PAT 11 — 4-bar reverse-bass pump (locked to kick grid)."""
    return join_notes(
        [
            (0, FS2, 80, BASS_808, 127),
            (0, FS3, 48, BASS_SHOT, 100),
            (96, FS2, 70, BASS_808, 110),
            (192, FS2, 80, BASS_808, 124),
            (288, FS2, 70, BASS_808, 108),
            (384, CS3, 80, BASS_808, 127),
            (384, CS3, 48, BASS_SHOT, 95),
            (480, CS3, 70, BASS_808, 110),
            (576, E3, 80, BASS_808, 118),
            (672, B2, 70, BASS_808, 105),
            (768, FS2, 80, BASS_808, 127),
            (768, A3, 48, BASS_SHOT, 100),
            (864, FS2, 70, BASS_808, 108),
            (960, FS2, 80, BASS_808, 122),
            (1056, A2, 70, BASS_808, 100),
            (1152, 30, 90, BASS_808, 127),
            (1152, FS2, 56, BASS_SHOT, 110),
            (1296, FS2, 72, BASS_808, 118),
            (1440, CS3, 72, BASS_808, 108),
        ]
    )


def pat_808_break() -> bytes:
    """PAT 12 — 4-bar drone break."""
    return join_notes(
        [
            (0, FS2, 340, BASS_808, 100),
            (768, CS3, 340, BASS_808, 95),
        ]
    )


def pat_perc_light() -> bytes:
    """PAT 13 — 1-bar light ghosts (drops only, not continuous mush)."""
    return join_notes(
        [
            (48, DRUM, 16, SNARE3, 40),
            (168, DRUM, 16, SNARE4, 45),
            (264, DRUM, 16, SNARE2, 42),
            (348, DRUM, 16, SNARE3, 48),
        ]
    )


def pat_impact() -> bytes:
    """PAT 14 — 1-bar section hit."""
    return join_notes(
        [
            (0, DRUM, 220, CRASH, 115),
            (0, DRUM, 160, CRASH2, 85),
            (0, DRUM, 180, FX, 105),
            (0, DRUM, 72, KICK, 127),
            (0, DRUM, 48, KICK2, 100),
            (192, DRUM, 96, FX2, 80),
        ]
    )


PATTERN_NOTES = {
    1: pat_cowbell_hook,
    2: pat_cowbell_drop,
    3: pat_cowbell_sparse,
    4: pat_drums_intro,
    5: pat_drums_half,
    6: pat_drums_hardstyle,
    7: pat_drums_ultra,
    8: pat_drums_build,
    9: pat_drums_fill,
    10: pat_808_verse,
    11: pat_808_drop,
    12: pat_808_break,
    13: pat_perc_light,
    14: pat_impact,
}

PATTERN_NAMES = {
    1: "Cowbell Hook",
    2: "Cowbell Drop",
    3: "Cowbell Sparse",
    4: "Drums Intro",
    5: "Drums Half",
    6: "Drums Hardstyle",
    7: "Drums Ultra",
    8: "Build Roll",
    9: "Fill Punch",
    10: "808 Verse",
    11: "808 Drop",
    12: "808 Break",
    13: "Perc Light",
    14: "Impact",
}


# ---------------------------------------------------------------------------
# Arrangement — 64 bars @ 150 BPM ≈ 1:42
# ---------------------------------------------------------------------------
#
#  0–8    INTRO     sparse cowbell + pulse → half enters
#  8–16   VERSE     half-time + hook + held 808
#  16–24  BUILD     hook → roll into drop
#  24–40  DROP 1    hardstyle + drop cowbell + reverse 808
#  40–48  BREAK     ultra + drone
#  48–56  DROP 2    hardstyle return (shorter)
#  56–64  OUTRO     sparse fade


def build_playlist() -> bytes:
    clips: list[bytes] = []

    def add(pat: int, start: float, length: float, track: int) -> None:
        clips.append(pack_clip(pat, start, length, track))

    # ===== INTRO 0–8 =====
    add(3, 0, 4, TR_COWBELL)
    add(1, 4, 4, TR_COWBELL)
    add(4, 0, 4, TR_DRUMS)
    add(5, 4, 3, TR_DRUMS)
    add(9, 7, 1, TR_DRUMS)
    add(12, 4, 4, TR_BASS)
    add(14, 4, 1, TR_FX)

    # ===== VERSE 8–16 =====
    add(1, 8, 8, TR_COWBELL)
    add(5, 8, 7, TR_DRUMS)
    add(9, 15, 1, TR_DRUMS)
    add(10, 8, 8, TR_BASS)
    add(14, 8, 1, TR_FX)

    # ===== BUILD 16–24 =====
    add(1, 16, 4, TR_COWBELL)
    add(2, 20, 3, TR_COWBELL)
    add(5, 16, 4, TR_DRUMS)
    add(8, 20, 3, TR_DRUMS)  # hardtekk roll
    add(9, 23, 1, TR_DRUMS)
    add(10, 16, 4, TR_BASS)
    add(11, 20, 3, TR_BASS)  # bass starts pumping early
    add(14, 20, 1, TR_FX)
    add(14, 23, 1, TR_FX)

    # ===== DROP 1  24–40 =====
    add(2, 24, 16, TR_COWBELL)
    add(6, 24, 7, TR_DRUMS)
    add(9, 31, 1, TR_DRUMS)
    add(6, 32, 7, TR_DRUMS)
    add(9, 39, 1, TR_DRUMS)
    add(11, 24, 16, TR_BASS)
    add(13, 24, 8, TR_PERC)  # light ghosts first half only
    add(14, 24, 1, TR_FX)
    add(14, 32, 1, TR_FX)

    # ===== BREAK 40–48 =====
    add(3, 40, 8, TR_COWBELL)
    add(7, 40, 6, TR_DRUMS)
    add(8, 46, 1, TR_DRUMS)
    add(9, 47, 1, TR_DRUMS)
    add(12, 40, 7, TR_BASS)
    add(14, 40, 1, TR_FX)
    add(14, 47, 1, TR_FX)

    # ===== DROP 2  48–56 =====
    add(2, 48, 8, TR_COWBELL)
    add(6, 48, 7, TR_DRUMS)
    add(9, 55, 1, TR_DRUMS)
    add(11, 48, 8, TR_BASS)
    add(13, 48, 8, TR_PERC)
    add(14, 48, 1, TR_FX)

    # ===== OUTRO 56–64 =====
    add(1, 56, 4, TR_COWBELL)
    add(3, 60, 4, TR_COWBELL)
    add(5, 56, 4, TR_DRUMS)
    add(7, 60, 3, TR_DRUMS)
    add(4, 63, 1, TR_DRUMS)
    add(10, 56, 4, TR_BASS)
    add(12, 60, 4, TR_BASS)
    add(14, 56, 1, TR_FX)
    add(14, 60, 1, TR_FX)

    return b"".join(clips)


def enable_all_playlist_tracks(payload: bytes) -> bytes:
    if len(payload) < 48:
        return payload
    data = bytearray(payload)
    data[12] = 1
    if len(data) > 21:
        data[21] = 0
    if len(data) > 46:
        data[46] = 0
    if len(data) > 47:
        data[47] = 0
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
    names_replaced: set[int] = set()
    chan_named: set[int] = set()
    playlist_done = False
    title_done = False
    tempo_done = False
    last_track_iid: int | None = None

    for eid, payload in events:
        if eid == 194 and not title_done:
            out.append((194, utf16_encode(SONG_TITLE)))
            title_done = True
            continue

        if eid == 156 and not tempo_done:
            out.append((156, struct.pack("<I", BPM * 1000)))
            tempo_done = True
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

        # Pattern name (event 193)
        if eid == 193 and current_pat in PATTERN_NAMES and current_pat not in names_replaced:
            out.append((193, utf16_encode(PATTERN_NAMES[current_pat])))
            names_replaced.add(current_pat)
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

        if eid == 238:
            last_track_iid = struct.unpack_from("<I", payload, 0)[0]
            out.append((238, enable_all_playlist_tracks(payload)))
            continue

        if eid == 239 and last_track_iid in TRACK_RENAMES:
            out.append((239, utf16_encode(TRACK_RENAMES[last_track_iid])))
            last_track_iid = None
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
            if pat in PATTERN_NAMES:
                out.append((193, utf16_encode(PATTERN_NAMES[pat])))
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
    tempo = None
    track_names: dict[int, str] = {}
    last_iid = None

    for eid, p in events:
        if eid == 156 and len(p) >= 4:
            tempo = struct.unpack("<I", p[:4])[0] / 1000.0
        elif eid == 64:
            chan = struct.unpack("<H", p)[0]
        elif eid == 65:
            pat = struct.unpack("<H", p)[0]
        elif eid == 238:
            last_iid = struct.unpack_from("<I", p, 0)[0]
        elif eid == 239 and last_iid is not None:
            track_names[last_iid] = utf16_decode(p).rstrip("\x00")
            last_iid = None
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
                if end_u != length or start_u != 0:
                    problems.append(
                        f"playlist#{i} bad pattern offsets start_u={start_u} end_u={end_u} len={length}"
                    )
                if vals[7] & 0x2000:
                    problems.append(f"playlist#{i} muted flag set")
                track_iid = 500 - vals[4]
                if track_iid == 1:
                    problems.append(f"playlist#{i} on disabled track 1")
                if track_iid not in (TR_COWBELL, TR_BASS, TR_DRUMS, TR_PERC, TR_FX):
                    problems.append(f"playlist#{i} unexpected track {track_iid}")
        elif eid == 203:
            name = utf16_decode(p)
            if any(m in name for m in MISSING_VSTS):
                problems.append(f"VST name left: {name}")
        elif eid == 213:
            for m in MISSING_VSTS:
                if m.encode("utf-8") in p or m.encode("utf-16-le") in p:
                    problems.append(f"VST state left: {m}")
                    break

    print(f"\n  tempo: {tempo} BPM")
    if tempo != float(BPM):
        problems.append(f"tempo {tempo} != {BPM}")
    print("  playlist lanes:")
    for iid in (TR_COWBELL, TR_BASS, TR_DRUMS, TR_PERC, TR_FX):
        print(f"    iid {iid} → {track_names.get(iid, '?')!r}")
        if track_names.get(iid) not in (
            TRACK_RENAMES.get(iid),
            TRACK_RENAMES.get(iid, "").rstrip("\x00"),
        ):
            # allow exact rename match
            expected = TRACK_RENAMES[iid]
            got = track_names.get(iid, "")
            if got != expected:
                problems.append(f"track {iid} name {got!r} != {expected!r}")
    print(f"  playlist clips: {playlist_clips}")
    print("  patterns:")
    for pn in sorted(PATTERN_NOTES):
        count = pat_notes.get(pn, 0)
        status = "OK" if count > 0 else "EMPTY"
        print(f"    [{status}] pat{pn:2d} {PATTERN_NAMES[pn]:16s} notes={count}")
        if count == 0:
            problems.append(f"pattern {pn} empty")

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

    projects = (
        Path.home()
        / "Documents"
        / "Image-Line"
        / "FL Studio"
        / "Projects"
        / "covenant_strike"
        / "covenant_strike.flp"
    )
    projects.parent.mkdir(parents=True, exist_ok=True)
    projects.write_bytes(OUT_FLP.read_bytes())
    print(f"Copied → {projects}")


if __name__ == "__main__":
    main()
