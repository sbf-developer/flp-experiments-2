"""
White Armor — dreamscape / cold-synth ambient FLP
Clone Project_5 (Sakura, Autogun, Morphine, choir, FX) and patch notes + playlist.

FL Studio 24 → 60-byte playlist items.
"""
from __future__ import annotations

import struct
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

NOTE = struct.Struct("<iHH iHH b B b b b b b b")  # 24
# FL21+ / FL24 pattern clip (60 bytes) — matched to Project_1
CLIP60 = struct.Struct("<I H H I H H 2s H 4s I I 28s")
CLIP_EXTRA = b"\x01" + b"\x00" * 27
BAR = 384
BEAT = 96

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
OUT_FLP = OUT_DIR / "white_armor.flp"
PROJECTS = (
    Path.home()
    / "Documents"
    / "Image-Line"
    / "FL Studio"
    / "Projects"
    / "white_armor"
    / "white_armor.flp"
)

# Channel roles in Project_5
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
    SAKURA: "Pad Armor",
    AUTOGUN: "Shimmer",
    MORPHINE: "Deep Pad",
    REESE: "Soft Sub",
    SAKURA_HI: "Glass Pad",
    SAKURA_MID: "Veil Pad",
    LEAD: "White Lead",
    CHOIR: "Air Choir",
    FX: "Glass FX",
}

# Playlist lanes (all enabled in Project_5)
TR_PAD = 1
TR_DEEP = 2
TR_SHIMMER = 3
TR_LEAD = 4
TR_CHOIR = 5
TR_SUB = 6
TR_FX = 7

# D minor / cold metallic — dreamscape
D2, F2, A2, Bb2 = 38, 41, 45, 46
D3, F3, A3, Bb3, C4 = 50, 53, 57, 58, 60
D4, F4, A4, C5, D5, F5 = 62, 65, 69, 72, 74, 77


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


def n(pos: int, key: int, length: int, rack: int, vel: int = 80) -> bytes:
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


# ---------------------------------------------------------------------------
# Composition — White Armor @ ~88 BPM dreamscape
# ---------------------------------------------------------------------------


def pat_pad_bed_a() -> bytes:
    """PAT 1 — 8-bar main pad bed (Dm → Bb → F → C)."""
    hits = []
    # Dm
    for key, vel, rack in (
        (D3, 55, SAKURA),
        (F3, 48, SAKURA),
        (A3, 45, SAKURA),
        (D2, 40, MORPHINE),
        (A2, 35, MORPHINE),
        (D4, 30, SAKURA_HI),
        (A3, 28, CHOIR),
        (D4, 26, CHOIR),
        (F4, 24, CHOIR),
    ):
        hits.append((0, key, 768, rack, vel))
    # Bb
    for key, vel, rack in (
        (Bb2, 52, SAKURA),
        (D3, 46, SAKURA),
        (F3, 44, SAKURA),
        (Bb2, 38, MORPHINE),
        (F3, 28, SAKURA_HI),
        (Bb3, 26, CHOIR),
        (D4, 24, CHOIR),
    ):
        hits.append((768, key, 768, rack, vel))
    # F
    for key, vel, rack in (
        (F3, 54, SAKURA),
        (A3, 48, SAKURA),
        (C4, 42, SAKURA),
        (F2, 40, MORPHINE),
        (C4, 30, SAKURA_HI),
        (F4, 28, CHOIR),
        (A4, 24, CHOIR),
    ):
        hits.append((1536, key, 768, rack, vel))
    # C
    e3, g3, e4 = 52, 55, 64
    for key, vel, rack in (
        (C4, 50, SAKURA),
        (e3, 44, SAKURA),
        (g3, 42, SAKURA),
        (C4, 36, MORPHINE),
        (g3, 28, SAKURA_MID),
        (C5, 26, CHOIR),
        (e4, 22, CHOIR),
    ):
        hits.append((2304, key, 768, rack, vel))
    return join(hits)


def pat_pad_bed_b() -> bytes:
    """PAT 2 — 8-bar alternate bed (slightly brighter / thinner)."""
    g2, g3, e4 = 43, 55, 64
    hits = []
    prog = [
        (
            0,
            [
                (D3, SAKURA, 50),
                (A3, SAKURA_MID, 40),
                (D4, SAKURA_HI, 32),
                (D3, CHOIR, 28),
                (A3, CHOIR, 24),
                (D2, MORPHINE, 36),
            ],
        ),
        (
            768,
            [
                (F3, SAKURA, 48),
                (A3, SAKURA_MID, 38),
                (C4, SAKURA_HI, 30),
                (F3, CHOIR, 26),
                (F2, MORPHINE, 34),
            ],
        ),
        (
            1536,
            [
                (g3, SAKURA, 48),
                (Bb3, SAKURA_MID, 38),
                (D4, SAKURA_HI, 30),
                (g3, CHOIR, 26),
                (g2, MORPHINE, 34),
            ],
        ),
        (
            2304,
            [
                (A3, SAKURA, 50),
                (C4, SAKURA_MID, 40),
                (e4, SAKURA_HI, 32),
                (A3, CHOIR, 28),
                (A2, MORPHINE, 36),
            ],
        ),
    ]
    for start, layers in prog:
        for key, rack, vel in layers:
            hits.append((start, key, 768, rack, vel))
    return join(hits)


def pat_lead() -> bytes:
    """PAT 3 — 8-bar sparse white lead (sings over pads)."""
    g4 = 67
    melody = [
        (0, D4, 360, 70),
        (384, F4, 300, 65),
        (768, A4, 420, 72),
        (1248, g4, 240, 58),
        (1536, F4, 360, 68),
        (1920, D4, 300, 62),
        (2304, C5, 280, 70),
        (2688, A4, 480, 66),
    ]
    return join((p, k, ln, LEAD, v) for p, k, ln, v in melody)


def pat_shimmer() -> bytes:
    """PAT 4 — 4-bar Autogun shimmer (gentle high pulse)."""
    hits = []
    # soft 1/2-note pulses
    for bar in range(4):
        base = bar * BAR
        for i, key in enumerate((A4, D5, F5, D5)):
            hits.append((base + i * 96, key, 72, AUTOGUN, 28 + (i % 2) * 4))
    return join(hits)


def pat_sub() -> bytes:
    """PAT 5 — 8-bar soft reese / sub shadow (very low velocity)."""
    hits = [
        (0, D2, 700, REESE, 45),
        (768, Bb2, 700, REESE, 40),
        (1536, F2, 700, REESE, 42),
        (2304, C4 - 24, 700, REESE, 38),  # C2=36
    ]
    # fix C2
    hits[3] = (2304, 36, 700, REESE, 38)
    return join(hits)


def pat_fx_swell() -> bytes:
    """PAT 6 — 2-bar glass / swell FX."""
    return join(
        [
            (0, A4, 600, FX, 55),
            (192, D5, 480, FX, 40),
            (384, F5, 400, FX, 35),
        ]
    )


def pat_peak() -> bytes:
    """PAT 7 — 8-bar fuller stack (pads + lead + shimmer + choir)."""
    # Combine bed-like pads with denser choir + lead fragments
    hits = []
    # long pad wash whole 8 bars on morphine/sakura roots
    for key, rack, vel in (
        (D3, SAKURA, 58),
        (A3, SAKURA, 50),
        (D4, SAKURA_HI, 36),
        (D2, MORPHINE, 44),
        (A2, MORPHINE, 38),
        (D3, CHOIR, 34),
        (F3, CHOIR, 30),
        (A3, CHOIR, 28),
        (D4, CHOIR, 26),
    ):
        hits.append((0, key, 8 * BAR - 24, rack, vel))
    # lead phrases
    for p, k, ln, v in (
        (384, F4, 280, 74),
        (960, A4, 320, 78),
        (1536, D5, 360, 80),
        (2112, C5, 240, 70),
        (2496, A4, 480, 75),
    ):
        hits.append((p, k, ln, LEAD, v))
    # light shimmer every bar
    for bar in range(8):
        hits.append((bar * BAR, A4, 60, AUTOGUN, 26))
        hits.append((bar * BAR + 192, D5, 60, AUTOGUN, 24))
    return join(hits)


def pat_outro() -> bytes:
    """PAT 8 — 8-bar dissolve (thin pads + fading choir)."""
    hits = []
    for start, keys in (
        (0, [(D3, SAKURA, 40), (A3, CHOIR, 22), (D2, MORPHINE, 30)]),
        (768, [(F3, SAKURA, 34), (A3, CHOIR, 18)]),
        (1536, [(D3, SAKURA, 28), (D4, SAKURA_HI, 16)]),
        (2304, [(D3, SAKURA, 20), (A2, MORPHINE, 16)]),
    ):
        for key, rack, vel in keys:
            hits.append((start, key, 720, rack, vel))
    hits.append((0, A4, 900, FX, 30))
    return join(hits)


PATTERN_NOTES = {
    1: pat_pad_bed_a,
    2: pat_pad_bed_b,
    3: pat_lead,
    4: pat_shimmer,
    5: pat_sub,
    6: pat_fx_swell,
    7: pat_peak,
    8: pat_outro,
}

PATTERN_NAMES = {
    1: "Pad Bed A",
    2: "Pad Bed B",
    3: "White Lead",
    4: "Shimmer",
    5: "Soft Sub",
    6: "Glass FX",
    7: "Peak Stack",
    8: "Outro Dissolve",
}


def build_playlist() -> bytes:
    """~64 bars @ 88 BPM ≈ 2:54 — mist → bed → voice → peak → dissolve."""
    clips: list[bytes] = []

    def add(pat: int, start: float, length: float, track: int) -> None:
        clips.append(pack_clip(pat, start, length, track))

    # 0–8 mist
    add(1, 0, 8, TR_PAD)
    add(6, 0, 2, TR_FX)
    add(5, 4, 4, TR_SUB)

    # 8–16 bed
    add(1, 8, 8, TR_PAD)
    add(5, 8, 8, TR_SUB)
    add(4, 8, 8, TR_SHIMMER)

    # 16–24 voice enters
    add(2, 16, 8, TR_PAD)
    add(3, 16, 8, TR_LEAD)
    add(4, 16, 8, TR_SHIMMER)
    add(5, 16, 8, TR_SUB)
    add(6, 22, 2, TR_FX)

    # 24–32 lift
    add(2, 24, 8, TR_PAD)
    add(3, 24, 8, TR_LEAD)
    add(4, 24, 8, TR_SHIMMER)
    add(5, 24, 8, TR_SUB)

    # 32–48 peak
    add(7, 32, 16, TR_PAD)
    add(3, 32, 16, TR_LEAD)
    add(4, 32, 16, TR_SHIMMER)
    add(5, 32, 16, TR_SUB)
    add(6, 32, 2, TR_FX)
    add(6, 40, 2, TR_FX)

    # 48–56 afterglow
    add(1, 48, 8, TR_PAD)
    add(3, 48, 8, TR_LEAD)
    add(4, 48, 8, TR_SHIMMER)
    add(5, 48, 8, TR_SUB)

    # 56–64 dissolve
    add(8, 56, 8, TR_PAD)
    add(6, 56, 2, TR_FX)

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
    chan_named: set[int] = set()
    playlist_done = False
    title_done = False
    tempo_done = False

    for eid, payload in events:
        if eid == 194 and not title_done:
            out.append((194, utf16_encode("White Armor")))
            title_done = True
            continue

        # Tempo dword = BPM * 1000 → 88.000
        if eid == 156 and not tempo_done:
            out.append((156, struct.pack("<I", 88000)))
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
            out.append((238, enable_track(payload)))
            continue

        if eid == 203 and current_chan in CHANNEL_NAMES and current_chan not in chan_named:
            out.append((203, utf16_encode(CHANNEL_NAMES[current_chan])))
            chan_named.add(current_chan)
            continue

        if eid == 22 and current_chan in USED:
            out.append((22, struct.pack("<b", 0)))  # master — keep signal clean
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
    _h, events = read_flp(path)
    problems: list[str] = []
    pat = None
    pat_notes: dict[int, int] = {}
    playlist_clips = 0

    for eid, p in events:
        if eid == 65:
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
                pos, base, idx, length, tr, grp, u1, flags, u2, s, e, extra = CLIP60.unpack(raw)
                if idx < 0x5000:
                    problems.append(f"clip#{i} bare index")
                if flags & 0x2000:
                    problems.append(f"clip#{i} muted")
                track = 500 - tr
                if track < 1:
                    problems.append(f"clip#{i} bad track")
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

    print(f"  playlist clips: {playlist_clips} (60-byte)")
    for pn in sorted(PATTERN_NOTES):
        c = pat_notes.get(pn, 0)
        print(f"  pat{pn} {PATTERN_NAMES[pn]:16s} notes={c}")
        if c == 0:
            problems.append(f"empty pat {pn}")

    if problems:
        print("PROBLEMS:")
        for pr in problems:
            print(" -", pr)
        raise SystemExit(1)
    print("VERIFY OK")


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
