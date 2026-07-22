"""
Glass Horizon — White Armor–type cold synth dreamscape (~1:30).

SONG_BRIEF
- Intent: cold mist → gentle warmth at peak → glass dissolve
- Template: Project_5 | 60-byte clips
- Key: D minor | BPM: 84 | Bars: 32 (~1:31)
- Progression (8): Dm → Bb → F → C  (i – VI – III – VII), voice-led
- Structure: 4 mist / 8 bed / 8 voice / 8 peak / 4 outro
- Signature: white lead over morphine/sakura wash (White Armor DNA)
"""
from __future__ import annotations

import struct
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

NOTE = struct.Struct("<iHH iHH b B b b b b b b")
CLIP60 = struct.Struct("<I H H I H H 2s H 4s I I 28s")
CLIP_EXTRA = b"\x01" + b"\x00" * 27
BAR = 384
BPM = 84
TOTAL_BARS = 32

MISSING_VSTS = (
    "Serum", "VU Meter", "Ozone", "CamelCrusher", "OTT",
    "Radiator", "Kickstart", "Valhalla",
)

TEMPLATE = Path(
    r"C:\Users\scott\Documents\Image-Line\FL Studio\Projects\Project_5\Project_5.flp"
)
OUT_DIR = Path(__file__).resolve().parent / "out"
OUT_FLP = OUT_DIR / "glass_horizon.flp"
SONG_TITLE = "Glass Horizon"
PROJECTS = (
    Path.home() / "Documents" / "Image-Line" / "FL Studio"
    / "Projects" / "glass_horizon" / "glass_horizon.flp"
)

SAKURA, AUTOGUN, MORPHINE, REESE = 0, 1, 2, 3
SAKURA_HI, SAKURA_MID, LEAD, CHOIR, FX = 4, 5, 6, 7, 8
USED = {SAKURA, AUTOGUN, MORPHINE, REESE, SAKURA_HI, SAKURA_MID, LEAD, CHOIR, FX}

CHANNEL_NAMES = {
    SAKURA: "Glass Pad",
    AUTOGUN: "Ice Shimmer",
    MORPHINE: "Deep Cold",
    REESE: "Soft Root",
    SAKURA_HI: "Frost Halo",
    SAKURA_MID: "Veil",
    LEAD: "White Lead",
    CHOIR: "Air Choir",
    FX: "Glass FX",
}

TR_PAD, TR_DEEP, TR_SHIMMER, TR_LEAD, TR_CHOIR, TR_SUB, TR_FX = 1, 2, 3, 4, 5, 6, 7
TRACK_RENAMES = {1: "Pads", 2: "Deep", 3: "Shimmer", 4: "Lead", 5: "Choir", 6: "Sub", 7: "FX"}

# D minor
D2, F2, A2, Bb2 = 38, 41, 45, 46
D3, F3, A3, Bb3, C4, G3 = 50, 53, 57, 58, 60, 55
D4, F4, G4, A4, Bb4, C5, D5, F5 = 62, 65, 67, 69, 70, 72, 74, 77


def read_varint(data: bytes, pos: int) -> tuple[int, int]:
    size, shift = 0, 0
    while pos < len(data):
        b = data[pos]; pos += 1
        size |= (b & 0x7F) << shift
        if not (b & 0x80): break
        shift += 7
    return size, pos


def write_varint(size: int) -> bytes:
    out = bytearray()
    while True:
        byte = size & 0x7F; size >>= 7
        if size: byte |= 0x80
        out.append(byte)
        if not size: break
    return bytes(out)


def parse_events(data: bytes) -> list[tuple[int, bytes]]:
    pos = 0; events = []
    while pos < len(data):
        eid = data[pos]; pos += 1
        if eid <= 63: payload = data[pos:pos+1]; pos += 1
        elif eid <= 127: payload = data[pos:pos+2]; pos += 2
        elif eid <= 191: payload = data[pos:pos+4]; pos += 4
        else:
            length, pos = read_varint(data, pos)
            payload = data[pos:pos+length]; pos += length
        events.append((eid, payload))
    return events


def build_events(events: list[tuple[int, bytes]]) -> bytes:
    out = bytearray()
    for eid, payload in events:
        out.append(eid)
        if eid <= 63: out.extend(payload[:1])
        elif eid <= 127: out.extend(payload[:2])
        elif eid <= 191: out.extend(payload[:4])
        else:
            out.extend(write_varint(len(payload))); out.extend(payload)
    return bytes(out)


def read_flp(path: Path) -> tuple[bytes, list[tuple[int, bytes]]]:
    raw = path.read_bytes()
    assert raw[:4] == b"FLhd" and raw[14:18] == b"FLdt"
    return raw[:14], parse_events(raw[22:])


def write_flp(path: Path, header: bytes, events: list[tuple[int, bytes]]) -> None:
    payload = build_events(events)
    path.write_bytes(bytes(header) + b"FLdt" + struct.pack("<I", len(payload)) + payload)


def utf16_decode(p: bytes) -> str:
    if p.endswith(b"\x00\x00"): return p[:-2].decode("utf-16-le", "replace")
    return p.decode("utf-16-le", "replace")


def utf16_encode(s: str) -> bytes:
    return s.encode("utf-16-le") + b"\x00\x00"


def n(pos: int, key: int, length: int, rack: int, vel: int = 72) -> bytes:
    return NOTE.pack(pos, 0x4000, rack, length, key, 0, 120, 0, 64, -128, 64,
                     max(1, min(127, vel)), -128, -128)


def pack_clip(pattern: int, start_bar: float, length_bars: float, track_iid: int) -> bytes:
    position = int(round(start_bar * BAR))
    length = int(round(length_bars * BAR))
    return CLIP60.pack(position, 0x5000, 0x5000 + pattern, length, 500 - track_iid,
                      0, b"\x78\x00", 0x8040, b"@d\x80\x80", 0xFFFFFFFF, 0xFFFFFFFF, CLIP_EXTRA)


def join(hits: list[tuple]) -> bytes:
    return b"".join(n(*h) for h in hits)


def chord(start: int, length: int, layers: list[tuple[int, int, int]]) -> list[tuple]:
    return [(start, key, length, rack, vel) for key, rack, vel in layers]


def pat_pad_bed_a() -> bytes:
    """PAT 1 — 8-bar Dm → Bb → F → C with voice-leading."""
    hits: list[tuple] = []
    hits += chord(0, 780, [
        (D3, SAKURA, 52), (F3, SAKURA, 46), (A3, SAKURA, 42),
        (D2, MORPHINE, 38), (A2, MORPHINE, 34),
        (D4, SAKURA_HI, 28), (A4, CHOIR, 22), (F4, CHOIR, 20),
    ])
    hits += chord(768, 780, [
        (Bb2, MORPHINE, 36), (D3, SAKURA, 50), (F3, SAKURA, 44), (Bb3, SAKURA, 40),
        (D4, SAKURA_HI, 26), (F4, CHOIR, 22), (Bb4, CHOIR, 18),
    ])
    hits += chord(1536, 780, [
        (F2, MORPHINE, 36), (A2, SAKURA, 48), (C4, SAKURA, 42), (F3, SAKURA, 44),
        (A3, SAKURA_MID, 26), (C4, CHOIR, 20), (A4, CHOIR, 18),
    ])
    hits += chord(2304, 780, [
        (C4, SAKURA, 50), (52, SAKURA, 44), (55, SAKURA, 42),  # C E G
        (36, MORPHINE, 34), (55, CHOIR, 20), (72, CHOIR, 18),  # C2, G, C5
    ])
    return join(hits)


def pat_pad_bed_b() -> bytes:
    """PAT 2 — 8-bar thinner glass bed."""
    hits: list[tuple] = []
    for start, layers in (
        (0, [(D3, SAKURA_MID, 44), (A3, SAKURA, 38), (D4, SAKURA_HI, 30), (D2, MORPHINE, 30)]),
        (768, [(Bb3, SAKURA_MID, 42), (F3, SAKURA, 36), (D3, CHOIR, 18)]),
        (1536, [(A3, SAKURA_MID, 40), (C4, SAKURA, 36), (F2, MORPHINE, 28)]),
        (2304, [(C4, SAKURA_MID, 42), (G3, SAKURA, 36), (C4, CHOIR, 18)]),
    ):
        for key, rack, vel in layers:
            hits.append((start, key, 780, rack, vel))
    return join(hits)


def pat_lead() -> bytes:
    """PAT 3 — 8-bar white lead (D min pentatonic, arch contour)."""
    melody = [
        (0, A4, 360, 58), (384, C5, 300, 62), (768, D5, 420, 68),
        (1248, A4, 240, 56), (1536, F4, 360, 64), (1920, D4, 300, 60),
        (2304, A4, 280, 66), (2688, D4, 480, 62),
    ]
    return join((p, k, ln, LEAD, v) for p, k, ln, v in melody)


def pat_lead_peak() -> bytes:
    """PAT 4 — 8-bar peak lead (higher answer)."""
    melody = [
        (0, D5, 340, 70), (384, F5, 380, 74), (864, D5, 280, 68),
        (1200, C5, 340, 72), (1632, A4, 420, 76), (2160, C5, 300, 72),
        (2592, D5, 360, 74), (3024, A4, 540, 70),
    ]
    return join((p, k, ln, LEAD, v) for p, k, ln, v in melody)


def pat_shimmer() -> bytes:
    """PAT 5 — 4-bar ice shimmer."""
    hits = []
    for bar in range(4):
        base = bar * BAR
        for i, key in enumerate((A4, D5, F5, A4)):
            hits.append((base + i * 96, key, 84, AUTOGUN, 22 + (i % 2) * 2))
    return join(hits)


def pat_sub() -> bytes:
    """PAT 6 — 8-bar reese roots (Dm prog)."""
    return join([
        (0, D2, 740, REESE, 38), (768, Bb2, 740, REESE, 36),
        (1536, F2, 740, REESE, 34), (2304, 36, 740, REESE, 32),  # C2
    ])


def pat_choir() -> bytes:
    """PAT 7 — 8-bar choir wash."""
    hits: list[tuple] = []
    for start, keys in (
        (0, [(A4, 22), (D5, 18), (F5, 16)]),
        (768, [(F4, 20), (Bb4, 18), (D5, 16)]),
        (1536, [(A4, 20), (C5, 18), (F5, 16)]),
        (2304, [(G4, 20), (C5, 18), (64, 16)]),  # E5
    ):
        for key, vel in keys:
            hits.append((start, key, 780, CHOIR, vel))
    return join(hits)


def pat_fx() -> bytes:
    """PAT 8 — 2-bar glass swell."""
    return join([
        (0, A4, 520, FX, 46), (144, D5, 460, FX, 36),
        (288, F5, 400, FX, 28), (432, A4, 340, FX, 22),
    ])


def pat_peak() -> bytes:
    """PAT 9 — 8-bar full bloom."""
    hits: list[tuple] = []
    for key, rack, vel in (
        (D3, SAKURA, 54), (F3, SAKURA, 48), (A3, SAKURA, 44),
        (D4, SAKURA_HI, 34), (D2, MORPHINE, 40),
        (A3, CHOIR, 26), (D4, CHOIR, 24), (F4, CHOIR, 22),
    ):
        hits.append((0, key, 8 * BAR - 24, rack, vel))
    for p, k, ln, v in (
        (480, F4, 280, 72), (960, A4, 340, 76), (1440, D5, 380, 78),
        (2016, C5, 280, 74), (2496, A4, 420, 76),
    ):
        hits.append((p, k, ln, LEAD, v))
    for bar in (0, 2, 4, 6):
        hits.append((bar * BAR, A4, 72, AUTOGUN, 24))
        hits.append((bar * BAR + 192, D5, 72, AUTOGUN, 22))
    return join(hits)


def pat_outro() -> bytes:
    """PAT 10 — 4-bar dissolve."""
    hits: list[tuple] = []
    for start, layers in (
        (0, [(D3, SAKURA, 34), (A3, CHOIR, 16), (D2, MORPHINE, 24)]),
        (384, [(F3, SAKURA_MID, 26), (D4, SAKURA_HI, 14)]),
        (768, [(D3, SAKURA, 20), (A2, MORPHINE, 14)]),
    ):
        for key, rack, vel in layers:
            hits.append((start, key, 720, rack, vel))
    hits.append((0, A4, 840, FX, 22))
    return join(hits)


PATTERN_NOTES = {
    1: pat_pad_bed_a, 2: pat_pad_bed_b, 3: pat_lead, 4: pat_lead_peak,
    5: pat_shimmer, 6: pat_sub, 7: pat_choir, 8: pat_fx,
    9: pat_peak, 10: pat_outro,
}
PATTERN_NAMES = {
    1: "Pad Bed A", 2: "Pad Bed B", 3: "White Lead", 4: "Lead Peak",
    5: "Ice Shimmer", 6: "Soft Root", 7: "Choir Wash", 8: "Glass FX",
    9: "Full Bloom", 10: "Dissolve",
}


def build_playlist() -> bytes:
    """32 bars @ 84 BPM ≈ 1:31 — mist → bed → voice → peak → outro."""
    clips: list[bytes] = []
    add = lambda pat, start, length, track: clips.append(pack_clip(pat, start, length, track))

    # 0–4 mist
    add(1, 0, 4, TR_PAD)
    add(8, 0, 2, TR_FX)

    # 4–12 bed
    add(1, 4, 8, TR_PAD)
    add(6, 4, 8, TR_SUB)
    add(5, 4, 8, TR_SHIMMER)
    add(7, 8, 4, TR_CHOIR)

    # 12–20 voice
    add(2, 12, 8, TR_PAD)
    add(3, 12, 8, TR_LEAD)
    add(5, 12, 8, TR_SHIMMER)
    add(6, 12, 8, TR_SUB)
    add(7, 12, 8, TR_CHOIR)
    add(8, 18, 2, TR_FX)

    # 20–28 peak
    add(9, 20, 8, TR_PAD)
    add(4, 20, 8, TR_LEAD)
    add(5, 20, 8, TR_SHIMMER)
    add(6, 20, 8, TR_SUB)
    add(7, 20, 8, TR_CHOIR)
    add(8, 20, 2, TR_FX)

    # 28–32 outro
    add(10, 28, 4, TR_PAD)
    add(8, 28, 2, TR_FX)

    return b"".join(clips)


def strip_missing_vsts(events: list) -> list[tuple[int, bytes]]:
    cleaned: list[tuple[int, bytes] | None] = list(events)
    for i, (eid, p) in enumerate(events):
        if eid == 203:
            if any(m in utf16_decode(p) for m in MISSING_VSTS): cleaned[i] = None
        elif eid == 213:
            if any(m.encode("utf-8") in p or m.encode("utf-16-le") in p for m in MISSING_VSTS):
                cleaned[i] = None
    return [e for e in cleaned if e is not None]


def enable_track(payload: bytes) -> bytes:
    if len(payload) < 48: return payload
    d = bytearray(payload); d[12] = 1
    if len(d) > 21: d[21] = 0
    if len(d) > 47: d[47] = 0
    return bytes(d)


def patch_project(events: list[tuple[int, bytes]]) -> list[tuple[int, bytes]]:
    events = strip_missing_vsts(events)
    out: list[tuple[int, bytes]] = []
    current_chan = current_pat = None
    notes_replaced: set[int] = set()
    names_replaced: set[int] = set()
    chan_named: set[int] = set()
    playlist_done = title_done = tempo_done = False
    last_track_iid = None

    for eid, payload in events:
        if eid == 194 and not title_done:
            out.append((194, utf16_encode(SONG_TITLE))); title_done = True; continue
        if eid == 156 and not tempo_done:
            out.append((156, struct.pack("<I", BPM * 1000))); tempo_done = True; continue
        if eid == 64:
            current_chan = struct.unpack("<H", payload)[0]; current_pat = None
            out.append((eid, payload)); continue
        if eid == 65:
            current_pat = struct.unpack("<H", payload)[0]; current_chan = None
            out.append((eid, payload)); continue
        if eid == 193 and current_pat in PATTERN_NAMES and current_pat not in names_replaced:
            out.append((193, utf16_encode(PATTERN_NAMES[current_pat])))
            names_replaced.add(current_pat); continue
        if eid == 224:
            if current_pat in PATTERN_NOTES and current_pat not in notes_replaced:
                out.append((224, PATTERN_NOTES[current_pat]()))
                notes_replaced.add(current_pat)
            elif current_pat in PATTERN_NOTES: continue
            else: out.append((224, b""))
            continue
        if eid == 233:
            out.append((233, build_playlist())); playlist_done = True; continue
        if eid == 238:
            last_track_iid = struct.unpack_from("<I", payload, 0)[0]
            out.append((238, enable_track(payload))); continue
        if eid == 239 and last_track_iid in TRACK_RENAMES:
            out.append((239, utf16_encode(TRACK_RENAMES[last_track_iid])))
            last_track_iid = None; continue
        if eid == 203 and current_chan in CHANNEL_NAMES and current_chan not in chan_named:
            out.append((203, utf16_encode(CHANNEL_NAMES[current_chan])))
            chan_named.add(current_chan); continue
        if eid == 22 and current_chan in USED:
            out.append((22, struct.pack("<b", 0))); continue
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
    pat = None; pat_notes: dict[int, int] = {}; playlist_clips = 0; tempo = None
    max_bar = 0.0

    for eid, p in events:
        if eid == 156 and len(p) >= 4:
            tempo = struct.unpack("<I", p[:4])[0] / 1000.0
        elif eid == 65:
            pat = struct.unpack("<H", p)[0]
        elif eid == 224 and pat is not None:
            pat_notes[pat] = len(p) // 24
            for i in range(len(p) // 24):
                if NOTE.unpack_from(p, i * 24)[1] & 0x0008:
                    problems.append(f"slide in pat{pat}")
        elif eid == 233:
            if len(p) % 60: problems.append(f"playlist not 60-byte ({len(p)})")
            playlist_clips = len(p) // 60
            for i in range(playlist_clips):
                raw = p[i * 60:(i + 1) * 60]
                pos, _, idx, length, tr, _, _, flags, _, _, _, _ = CLIP60.unpack(raw)
                if idx < 0x5000: problems.append(f"clip#{i} bare index")
                if flags & 0x2000: problems.append(f"clip#{i} muted")
                if 500 - tr not in range(1, 8): problems.append(f"clip#{i} bad track")
                max_bar = max(max_bar, (pos + length) / BAR)
        elif eid == 238 and len(p) >= 13:
            iid = struct.unpack_from("<I", p, 0)[0]
            if iid <= 7 and p[12] != 1: problems.append(f"track {iid} disabled")
        elif eid == 203:
            if any(m in utf16_decode(p) for m in MISSING_VSTS):
                problems.append(f"VST left: {utf16_decode(p)}")

    duration_sec = TOTAL_BARS * (240 / BPM)
    print(f"  tempo: {tempo} BPM | target: {TOTAL_BARS} bars ≈ {duration_sec:.0f}s ({duration_sec/60:.1f} min)")
    print(f"  playlist clips: {playlist_clips} | arrangement ends ~bar {max_bar:.1f}")
    if tempo != float(BPM): problems.append(f"tempo {tempo} != {BPM}")
    if max_bar < TOTAL_BARS - 1: problems.append(f"arrangement too short ({max_bar} bars)")
    for pn in sorted(PATTERN_NOTES):
        c = pat_notes.get(pn, 0)
        print(f"  pat{pn:2d} {PATTERN_NAMES[pn]:16s} notes={c}")
        if c == 0: problems.append(f"empty pat {pn}")
    if problems:
        print("PROBLEMS:")
        for pr in problems: print(" -", pr)
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
