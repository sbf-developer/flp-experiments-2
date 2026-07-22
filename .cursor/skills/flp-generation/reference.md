# FLP parser/writer reference

Minimal, dependency-free FLP event parser and writer used by the generator.

## Parser

```python
import struct

def read_varint(data: bytes, pos: int) -> tuple[int, int]:
    size, shift = 0, 0
    while pos < len(data):
        b = data[pos]; pos += 1
        size |= (b & 0x7F) << shift
        if not (b & 0x80): break
        shift += 7
    return size, pos

def parse_events(data: bytes) -> list[tuple[int, bytes]]:
    pos = 0; events = []
    while pos < len(data):
        eid = data[pos]; pos += 1
        if eid <= 63:        payload = data[pos:pos+1]; pos += 1
        elif eid <= 127:    payload = data[pos:pos+2]; pos += 2
        elif eid <= 191:     payload = data[pos:pos+4]; pos += 4
        else:
            length, pos = read_varint(data, pos)
            payload = data[pos:pos+length]; pos += length
        events.append((eid, payload))
    return events
```

## Writer

```python
def write_varint(size: int) -> bytes:
    out = bytearray()
    while True:
        byte = size & 0x7F; size >>= 7
        if size: byte |= 0x80
        out.append(byte)
        if not size: break
    return bytes(out)

def build_events(events: list[tuple[int, bytes]]) -> bytes:
    out = bytearray()
    for eid, payload in events:
        out.append(eid)
        if eid <= 63:    out.extend(payload[:1])
        elif eid <= 127: out.extend(payload[:2])
        elif eid <= 191: out.extend(payload[:4])
        else:
            out.extend(write_varint(len(payload))); out.extend(payload)
    return bytes(out)

def read_flp(path):
    raw = path.read_bytes()
    assert raw[:4] == b"FLhd"
    header = raw[:14]
    assert raw[14:18] == b"FLdt"
    return header, parse_events(raw[22:])

def write_flp(path, header, events):
    payload = build_events(events)
    path.write_bytes(bytes(header) + b"FLdt" + struct.pack("<I", len(payload)) + payload)
```

## Note struct (24 bytes)

```python
NOTE = struct.Struct("<iHH iHH b B b b b b b b")
# position, flags, rack_channel, length, key, group,
# fine_pitch, _u1, release, midi_channel, pan, velocity, mod_x, mod_y

def pack_note(pos, key, length=192, rack=0, vel=100):
    return NOTE.pack(pos, 0x4000, rack, length, key, 0,
                     120, 0, 64, -128, 64, vel, -128, -128)
```

## Playlist pattern clip (32-byte, pre-FL21)

```python
CLIP = struct.Struct("<I H H I H H 2s H 4s I I")
# position, 0x5000, 0x5000+pattern, length, 500-track, group,
# b"\x78\x00", item_flags(0x8040), b"@d\x80\x80",
# uint32 start_u=0, uint32 end_u=length   ← pattern-clip convention
# Audio clips use float32 sample offsets in those 8 bytes instead.
# NEVER write float 0.0/0.0 for pattern clips — FL shows zero-width slivers.

def pack_clip(pattern, start_bar, length_bars, track, BAR=384):
    length = length_bars * BAR
    return CLIP.pack(start_bar*BAR, 0x5000, 0x5000+pattern, length,
                     500-track, 0, b"\x78\x00", 0x8040, b"@d\x80\x80", 0, length)
```

## Playlist pattern clip (60-byte, FL21+ / FL Studio 2024)

Match the template. Project_1 / white_armor use 60-byte items:

```python
CLIP60 = struct.Struct("<I H H I H H 2s H 4s I I 28s")
EXTRA = b"\x01" + b"\x00" * 27

def pack_clip60(pattern, start_bar, length_bars, track, BAR=384):
    length = int(length_bars * BAR)
    return CLIP60.pack(
        int(start_bar * BAR), 0x5000, 0x5000 + pattern, length,
        500 - track, 0, b"\x78\x00", 0x8040, b"@d\x80\x80",
        0xFFFFFFFF, 0xFFFFFFFF, EXTRA,
    )
```

If `len(playlist) % 60 == 0` and not divisible cleanly by 32 alone in intent,
use 60. Mixing sizes crashes FL (`FLEngine_x64.dll`).

## Event ID quick reference

| ID  | Name | Size class | Payload |
|-----|------|-----------|---------|
| 0   | (channel enabled flag) | byte | 1 = enabled |
| 22  | RoutedTo | byte (i8) | mixer insert; 0 = master |
| 64  | NewChan | word (u16) | channel index |
| 65  | NewPat | word (u16) | pattern number |
| 67  | CurrentPat | word | selected pattern |
| 196 | SamplePath | text | UTF-16 LE + `\x00\x00` |
| 199 | (channel name, some versions) | text | UTF-8 |
| 203 | Name | text | UTF-16 LE + wide null (channel & plugin) |
| 213 | NewPlugin state | data | VST path as UTF-8 inside |
| 215 | (sampler/internal state) | data | binary floats |
| 224 | Notes | data | N × 24-byte notes |
| 233 | Playlist | data | N × 32-byte clips (pre-FL21) |
| 236 | InsertFlags | data | 12 bytes/insert; bit 3 (0x08) = enabled, bit 12 = solo |
| 238 | TrackData | data | 66 bytes; enabled @ [12], locked @ [47] |
| 239 | TrackName | text | playlist lane name |

## Playlist tracks & mute (Song mode)

```python
# track_rvidx = 500 - track_iid   → lands on playlist track iid
# phonk mano: never use iid 1 (Original, disabled).
# Correct lanes: 2=Cowbell, 3=Bass, 5=Kick, 8=Snares, 13=FX
# Force-enable after clone:
def enable_track(p: bytes) -> bytes:
    d = bytearray(p)
    d[12] = 1          # enabled (green LED)
    if len(d) > 21: d[21] = 0
    if len(d) > 47: d[47] = 0  # unlocked
    return bytes(d)
```

Clip `item_flags`: `0x8040` unmuted, `0x2000` / `0xb040` muted (grey clip).
FL UI Mute tool (speaker+X) can mute clips after open — switch to Pencil;
generator must still ship unmuted clips + enabled tracks.

## Note flags

| Bit | Value | Meaning |
|-----|-------|---------|
| 0x0008 | 8 | **Slide** — do not set for normal notes (no trigger) |
| 0x4000 | 16384 | standard note flag (set this) |

## Common "no audio" symptoms → cause

| Symptom | Likely cause |
|---------|--------------|
| 0% CPU, black meters, notes visible in rack | Notes are slide notes (flags & 0x0008) |
| Clips in playlist, no meters | Playlist item_index not `0x5000+pattern` (read as audio clip) |
| "missing samples" / red channels | Event 196 path doesn't exist on disk |
| Loads then crashes (FLEngine_x64.dll) | Playlist item size mismatch (32 vs 60 bytes) or FLhd nChannels mismatch |
| Signal dies in mixer | Missing VST in insert FX chain — route to master or strip VST |
| Stale behavior | FL cached old project — close fully and reopen |
| Zero-width / sliver clips | Pattern clip tails written as float 0.0/0.0 instead of `(0, length)` |
| PAT fine, Song missing whole lanes | Playlist track disabled (event 238) or clips on track iid 1 |
| PAT fine, some clips silent/grey | Clip mute flag or FL Mute tool left active |
| 808/crash cut every bar | Too many abutting 1-bar clips — use long looping clips |

## Channel-block walking

Channel events appear between a `NewChan` (64) and the next `NewChan`. Track
`current_chan` from event 64, then read 196 (sample path), 22 (routing), 203
(name), 215 (state) until the next 64. Same pattern for patterns: `NewPat` (65)
followed by `Notes` (224).

## PyFLP (when it works)

`pyflp` can parse/validate, but `EventEnum` membership issues and opaque event
types make surgical edits hard. Use it to *inspect* structure, but do binary
edits with the manual parser above. Source: `pyflp/pattern.py` (note struct,
`_NoteFlags`), `pyflp/mixer.py` (`_InsertFlags`, `InsertFlagsEvent` 12-byte
struct), `pyflp/plugin.py` (plugin event IDs).
