"""
Pale Meridian — chill harmonious synth dreamscape FLP.

Clone Project_5 (Sakura, Autogun, Morphine, choir, FX) like White Armor.
Eb major · 76 BPM · long sustained voicings · gentle voice-leading.

FL Studio 24 → 60-byte playlist items.
"""
from __future__ import annotations

import struct
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

NOTE = struct.Struct("<iHH iHH b B b b b b b b")  # 24
CLIP60 = struct.Struct("<I H H I H H 2s H 4s I I 28s")
CLIP_EXTRA = b"\x01" + b"\x00" * 27
BAR = 384
BPM = 76

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

TEMPLATE = Path(
    r"C:\Users\scott\Documents\Image-Line\FL Studio\Projects\Project_5\Project_5.flp"
)
OUT_DIR = Path(__file__).resolve().parent / "out"
OUT_FLP = OUT_DIR / "pale_meridian.flp"
SONG_TITLE = "Pale Meridian"
PROJECTS = (
    Path.home()
    / "Documents"
    / "Image-Line"
    / "FL Studio"
    / "Projects"
    / "pale_meridian"
    / "pale_meridian.flp"
)

SAKURA = 0
AUTOGUN = 1
MORPHINE = 2
REESE = 3
SAKURA_HI = 4
SAKURA_MID = 5
LEAD = 6
CHOIR = 7
FX = 8

USED = {SAKURA, AUTOGUN, MORPHINE, REESE, SAKURA_HI, SAKURA_MID, LEAD, CHOIR, FX}

CHANNEL_NAMES = {
    SAKURA: "Warm Pad",
    AUTOGUN: "Star Dust",
    MORPHINE: "Deep Bloom",
    REESE: "Soft Root",
    SAKURA_HI: "Glass Halo",
    SAKURA_MID: "Veil",
    LEAD: "Dream Lead",
    CHOIR: "Air Choir",
    FX: "Horizon FX",
}

TR_PAD = 1
TR_DEEP = 2
TR_SHIMMER = 3
TR_LEAD = 4
TR_CHOIR = 5
TR_SUB = 6
TR_FX = 7

TRACK_RENAMES = {
    1: "Pads",
    2: "Deep",
    3: "Shimmer",
    4: "Lead",
    5: "Choir",
    6: "Sub",
    7: "FX",
}

# Eb major — lush, consonant dreamscape palette
Eb2, F2, G2, Ab2, Bb2 = 39, 41, 43, 44, 46
Eb3, F3, G3, Ab3, Bb3, C4 = 51, 53, 55, 56, 58, 60
Eb4, F4, G4, Ab4, Bb4, C5, Eb5 = 63, 65, 67, 68, 70, 72, 75
D4 = 62  # passing only in lead, resolves


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


def n(pos: int, key: int, length: int, rack: int, vel: int = 72) -> bytes:
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
    return CLIP60.pack(
        position,
        0x5000,
        0x5000 + pattern,
        length,
        500 - track_iid,
        0,
        b"\x78\x00",
        0x8040,
        b"@d\x80\x80",
        0xFFFFFFFF,
        0xFFFFFFFF,
        CLIP_EXTRA,
    )


def join(hits: list[tuple]) -> bytes:
    return b"".join(n(*h) for h in hits)


def chord(start: int, length: int, layers: list[tuple[int, int, int]]) -> list[tuple]:
    """(key, rack, vel) → note hits at start."""
    return [(start, key, length, rack, vel) for key, rack, vel in layers]


# ---------------------------------------------------------------------------
# Composition — Pale Meridian @ 76 BPM
# Progression: Eb → Ab → Cm → Bb (I–IV–vi–V), voice-led, all consonant
# ---------------------------------------------------------------------------


def pat_pad_bed_a() -> bytes:
    """PAT 1 — 8-bar main pad bed with smooth voice-leading."""
    hits: list[tuple] = []

    # Eb maj — root bed
    hits += chord(
        0,
        780,
        [
            (Eb3, SAKURA, 52),
            (G3, SAKURA, 46),
            (Bb3, SAKURA, 42),
            (Eb2, MORPHINE, 38),
            (Bb2, MORPHINE, 34),
            (Eb4, SAKURA_HI, 28),
            (G4, CHOIR, 24),
            (Bb4, CHOIR, 22),
        ],
    )

    # Ab maj — keep Eb as common tone
    hits += chord(
        768,
        780,
        [
            (Ab2, MORPHINE, 36),
            (Ab3, SAKURA, 50),
            (C4, SAKURA, 44),
            (Eb4, SAKURA, 40),
            (Eb4, SAKURA_HI, 26),
            (Ab4, CHOIR, 24),
            (C5, CHOIR, 20),
        ],
    )

    # Cm — soft minor color, still warm
    hits += chord(
        1536,
        780,
        [
            (C4, SAKURA, 48),
            (Eb4, SAKURA, 44),
            (G4, SAKURA, 40),
            (G2, MORPHINE, 34),
            (Eb3, MORPHINE, 32),
            (G4, SAKURA_MID, 26),
            (Eb4, CHOIR, 22),
            (G4, CHOIR, 20),
        ],
    )

    # Bb maj — lift before loop
    hits += chord(
        2304,
        780,
        [
            (Bb2, MORPHINE, 36),
            (Bb3, SAKURA, 50),
            (D4, SAKURA, 44),
            (F4, SAKURA, 40),
            (Bb4, SAKURA_HI, 28),
            (D4, CHOIR, 22),
            (F4, CHOIR, 20),
        ],
    )
    return join(hits)


def pat_pad_bed_b() -> bytes:
    """PAT 2 — 8-bar alternate bed (thinner mid, more glass)."""
    hits: list[tuple] = []
    sections = [
        (
            0,
            [
                (Eb3, SAKURA_MID, 44),
                (G3, SAKURA, 40),
                (Bb3, SAKURA_HI, 32),
                (Eb2, MORPHINE, 30),
                (G3, CHOIR, 22),
            ],
        ),
        (
            768,
            [
                (Ab3, SAKURA_MID, 42),
                (C4, SAKURA, 38),
                (Eb4, SAKURA_HI, 30),
                (Ab2, MORPHINE, 28),
                (C4, CHOIR, 20),
            ],
        ),
        (
            1536,
            [
                (G3, SAKURA_MID, 40),
                (Bb3, SAKURA, 36),
                (Eb4, SAKURA_HI, 28),
                (G2, MORPHINE, 26),
                (Bb3, CHOIR, 18),
            ],
        ),
        (
            2304,
            [
                (F3, SAKURA_MID, 42),
                (Ab3, SAKURA, 38),
                (Bb3, SAKURA_HI, 30),
                (Bb2, MORPHINE, 28),
                (F3, CHOIR, 20),
            ],
        ),
    ]
    for start, layers in sections:
        for key, rack, vel in layers:
            hits.append((start, key, 780, rack, vel))
    return join(hits)


def pat_lead() -> bytes:
    """PAT 3 — 8-bar singing lead (Eb pentatonic, long notes, soft arc)."""
    melody = [
        (0, G4, 420, 58),
        (432, Ab4, 360, 62),
        (864, Bb4, 480, 68),
        (1440, G4, 300, 58),
        (1824, F4, 360, 64),
        (2256, Eb4, 420, 60),
        (2736, G4, 360, 66),
        (3168, Eb4, 540, 62),
    ]
    return join((p, k, ln, LEAD, v) for p, k, ln, v in melody)


def pat_lead_b() -> bytes:
    """PAT 4 — 8-bar higher answer phrase (peak section)."""
    melody = [
        (0, Bb4, 360, 70),
        (384, C5, 420, 74),
        (864, Bb4, 300, 68),
        (1200, Ab4, 360, 72),
        (1632, G4, 480, 76),
        (2208, Ab4, 300, 70),
        (2592, Bb4, 360, 74),
        (3024, Eb5, 600, 72),
    ]
    return join((p, k, ln, LEAD, v) for p, k, ln, v in melody)


def pat_shimmer() -> bytes:
    """PAT 5 — 4-bar star-dust pulse (very soft, on chord tones)."""
    hits = []
    tones = (Bb4, G4, Eb5, Bb4)
    for bar in range(4):
        base = bar * BAR
        for i, key in enumerate(tones):
            hits.append((base + i * 96, key, 84, AUTOGUN, 22 + (i % 2) * 3))
    return join(hits)


def pat_sub() -> bytes:
    """PAT 6 — 8-bar root shadow (follows progression)."""
    return join(
        [
            (0, Eb2, 740, REESE, 38),
            (768, Ab2, 740, REESE, 36),
            (1536, G2, 740, REESE, 34),
            (2304, Bb2, 740, REESE, 36),
        ]
    )


def pat_choir_wash() -> bytes:
    """PAT 7 — 8-bar sustained choir wash (pure chord tones)."""
    hits: list[tuple] = []
    for start, keys in (
        (0, [(G4, 24), (Bb4, 22), (Eb5, 18)]),
        (768, [(C5, 22), (Eb5, 20), (Ab4, 18)]),
        (1536, [(Eb4, 22), (G4, 20), (Bb4, 18)]),
        (2304, [(F4, 22), (Ab4, 20), (Bb4, 18)]),
    ):
        for key, vel in keys:
            hits.append((start, key, 780, CHOIR, vel))
    return join(hits)


def pat_fx_swell() -> bytes:
    """PAT 8 — 2-bar horizon swell."""
    return join(
        [
            (0, G4, 540, FX, 48),
            (144, Bb4, 480, FX, 38),
            (288, Eb5, 420, FX, 32),
            (432, G4, 360, FX, 26),
        ]
    )


def pat_peak() -> bytes:
    """PAT 9 — 8-bar full bloom (pads + choir + lead fragments + shimmer)."""
    hits: list[tuple] = []
    # sustained Eb-major wash
    for key, rack, vel in (
        (Eb3, SAKURA, 54),
        (G3, SAKURA, 48),
        (Bb3, SAKURA, 44),
        (Eb4, SAKURA_HI, 34),
        (Eb2, MORPHINE, 40),
        (G3, CHOIR, 28),
        (Bb3, CHOIR, 26),
        (Eb4, CHOIR, 24),
        (G4, CHOIR, 22),
    ):
        hits.append((0, key, 8 * BAR - 24, rack, vel))
    # lead fragments — pentatonic, lyrical
    for p, k, ln, v in (
        (480, Ab4, 300, 72),
        (960, Bb4, 360, 76),
        (1440, C5, 420, 78),
        (2016, Bb4, 300, 74),
        (2400, G4, 480, 76),
        (2976, Eb4, 540, 70),
    ):
        hits.append((p, k, ln, LEAD, v))
    # gentle shimmer every 2 bars
    for bar in (0, 2, 4, 6):
        hits.append((bar * BAR, Bb4, 72, AUTOGUN, 24))
        hits.append((bar * BAR + 192, G4, 72, AUTOGUN, 22))
    return join(hits)


def pat_outro() -> bytes:
    """PAT 10 — 8-bar dissolve into silence."""
    hits: list[tuple] = []
    fade = [
        (0, [(Eb3, SAKURA, 36), (G3, CHOIR, 18), (Eb2, MORPHINE, 26)]),
        (768, [(Ab3, SAKURA, 28), (Eb4, CHOIR, 14)]),
        (1536, [(G3, SAKURA_MID, 22), (Bb3, SAKURA_HI, 14)]),
        (2304, [(Eb3, SAKURA, 16), (Eb2, MORPHINE, 12)]),
    ]
    for start, layers in fade:
        for key, rack, vel in layers:
            hits.append((start, key, 720, rack, vel))
    hits.append((0, Bb4, 960, FX, 24))
    hits.append((768, G4, 720, FX, 18))
    return join(hits)


PATTERN_NOTES = {
    1: pat_pad_bed_a,
    2: pat_pad_bed_b,
    3: pat_lead,
    4: pat_lead_b,
    5: pat_shimmer,
    6: pat_sub,
    7: pat_choir_wash,
    8: pat_fx_swell,
    9: pat_peak,
    10: pat_outro,
}

PATTERN_NAMES = {
    1: "Pad Bed A",
    2: "Pad Bed B",
    3: "Dream Lead",
    4: "Lead Bloom",
    5: "Star Dust",
    6: "Soft Root",
    7: "Choir Wash",
    8: "Horizon FX",
    9: "Full Bloom",
    10: "Dissolve",
}


def build_playlist() -> bytes:
    """~72 bars @ 76 BPM ≈ 3:47 — mist → bed → voice → bloom → dissolve."""
    clips: list[bytes] = []

    def add(pat: int, start: float, length: float, track: int) -> None:
        clips.append(pack_clip(pat, start, length, track))

    # 0–12 mist (pads only, very sparse)
    add(1, 0, 12, TR_PAD)
    add(8, 0, 4, TR_FX)
    add(6, 8, 4, TR_SUB)

    # 12–24 bed unfolds
    add(1, 12, 12, TR_PAD)
    add(6, 12, 12, TR_SUB)
    add(5, 12, 12, TR_SHIMMER)
    add(7, 16, 8, TR_CHOIR)

    # 24–36 voice enters
    add(2, 24, 12, TR_PAD)
    add(3, 24, 12, TR_LEAD)
    add(5, 24, 12, TR_SHIMMER)
    add(6, 24, 12, TR_SUB)
    add(7, 24, 12, TR_CHOIR)
    add(8, 34, 2, TR_FX)

    # 36–48 lift
    add(2, 36, 12, TR_PAD)
    add(3, 36, 6, TR_LEAD)
    add(4, 42, 6, TR_LEAD)
    add(5, 36, 12, TR_SHIMMER)
    add(6, 36, 12, TR_SUB)
    add(7, 36, 12, TR_CHOIR)

    # 48–60 peak bloom
    add(9, 48, 12, TR_PAD)
    add(4, 48, 12, TR_LEAD)
    add(5, 48, 12, TR_SHIMMER)
    add(6, 48, 12, TR_SUB)
    add(7, 48, 12, TR_CHOIR)
    add(8, 48, 2, TR_FX)
    add(8, 54, 2, TR_FX)

    # 60–72 afterglow → dissolve
    add(1, 60, 6, TR_PAD)
    add(3, 60, 6, TR_LEAD)
    add(5, 60, 6, TR_SHIMMER)
    add(6, 60, 6, TR_SUB)
    add(10, 66, 6, TR_PAD)
    add(8, 66, 2, TR_FX)

    return b"".join(clips)


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


def enable_track(payload: bytes) -> bytes:
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
            out.append((238, enable_track(payload)))
            continue

        if eid == 239 and last_track_iid in TRACK_RENAMES:
            out.append((239, utf16_encode(TRACK_RENAMES[last_track_iid])))
            last_track_iid = None
            continue

        if eid == 203 and current_chan in CHANNEL_NAMES and current_chan not in chan_named:
            out.append((203, utf16_encode(CHANNEL_NAMES[current_chan])))
            chan_named.add(current_chan)
            continue

        if eid == 22 and current_chan in USED:
            out.append((22, struct.pack("<b", 0)))
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
    _h, events = read_flp(path)
    problems: list[str] = []
    pat = None
    pat_notes: dict[int, int] = {}
    playlist_clips = 0
    tempo = None

    for eid, p in events:
        if eid == 156 and len(p) >= 4:
            tempo = struct.unpack("<I", p[:4])[0] / 1000.0
        elif eid == 65:
            pat = struct.unpack("<H", p)[0]
        elif eid == 224 and pat is not None:
            pat_notes[pat] = len(p) // 24
            for i in range(len(p) // 24):
                flags = NOTE.unpack_from(p, i * 24)[1]
                if flags & 0x0008:
                    problems.append(f"slide in pat{pat}")
        elif eid == 233:
            if len(p) % 60:
                problems.append(f"playlist not 60-byte aligned ({len(p)})")
            playlist_clips = len(p) // 60
            for i in range(playlist_clips):
                raw = p[i * 60 : (i + 1) * 60]
                _, _, idx, length, tr, _, _, flags, _, _, _, _ = CLIP60.unpack(raw)
                if idx < 0x5000:
                    problems.append(f"clip#{i} bare index")
                if flags & 0x2000:
                    problems.append(f"clip#{i} muted")
                track = 500 - tr
                if track not in (TR_PAD, TR_DEEP, TR_SHIMMER, TR_LEAD, TR_CHOIR, TR_SUB, TR_FX):
                    problems.append(f"clip#{i} unexpected track {track}")
                if length < BAR // 2:
                    problems.append(f"clip#{i} tiny length")
        elif eid == 238 and len(p) >= 13:
            iid = struct.unpack_from("<I", p, 0)[0]
            if iid <= 10 and p[12] != 1:
                problems.append(f"track {iid} disabled")
        elif eid == 203:
            name = utf16_decode(p)
            if any(m in name for m in MISSING_VSTS):
                problems.append(f"VST left: {name}")

    print(f"  tempo: {tempo} BPM")
    if tempo != float(BPM):
        problems.append(f"tempo {tempo} != {BPM}")
    print(f"  playlist clips: {playlist_clips} (60-byte)")
    for pn in sorted(PATTERN_NOTES):
        c = pat_notes.get(pn, 0)
        print(f"  pat{pn:2d} {PATTERN_NAMES[pn]:16s} notes={c}")
        if c == 0:
            problems.append(f"empty pat {pn}")

    if problems:
        print("PROBLEMS:")
        for pr in problems:
            print(" -", pr)
        raise SystemExit(1)
    print("VERIFY OK — open in Song mode")


def main() -> None:
    if not TEMPLATE.exists():
        raise SystemExit(f"Missing template: {TEMPLATE}")

    header, events = read_flp(TEMPLATE)
    patched = patch_project(events)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    write_flp(OUT_FLP, header, patched)
    print(f"Wrote {OUT_FLP} ({OUT_FLP.stat().st_size:,} bytes)")
    verify(OUT_FLP)

    PROJECTS.parent.mkdir(parents=True, exist_ok=True)
    PROJECTS.write_bytes(OUT_FLP.read_bytes())
    print(f"Copied → {PROJECTS}")


if __name__ == "__main__":
    main()
