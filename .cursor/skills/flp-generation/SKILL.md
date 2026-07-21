---
name: flp-generation
description: Generate and patch FL Studio .flp project files programmatically with Python (manual binary parsing, not PyFLP). Use when generating FLP files, editing FL Studio projects from code, or debugging FLP audio/silence issues (missing samples, missing VSTs, slide-note bug, playlist clip format, mixer routing, disabled playlist tracks, mute-tool / muted clips).
---

# FL Studio .flp Generation

Hard-won knowledge from building a dark-phonk FLP generator. The FLP format is
undocumented and brittle; most "no audio" bugs come from a handful of specific
gotchas below. **When audio is missing, walk the checklist at the bottom first.**

## When to use this skill

- Generating `.flp` files from code
- Patching an existing template `.flp` (notes, playlist, sample paths, routing)
- Debugging an FLP that loads but produces no sound / 0% CPU / black meters
- Song mode plays only some patterns while PAT mode is fine

## Recommended approach: clone-and-patch, not from-scratch

Building an FLP from scratch is fragile (channel-block structure, `FLhd.nChannels`
must match, mixer init). **Prefer loading a working template FLP and patching
events in place**: replace `Notes`, `Playlist`, `SamplePath`, `RoutedTo` events.
Also patch playlist **track** state (event 238). Keep the template's
channel/mixer skeleton intact.

PyFLP exists but had `EventEnum` compatibility issues and hides granular control.
**Manual `struct` parsing is more reliable.** A minimal parser/writer is ~40 lines
(see `reference.md`).

## FLP file layout

```
"FLhd" + <4-byte len> + 6-byte header   # format(u16), nChannels(u16), PPQ(u16)
"FLdt" + <4-byte len> + events...
```

## Event ID size classes (how to parse)

The event ID byte determines payload size:

| ID range | Payload | Examples |
|----------|---------|----------|
| 0–63     | 1 byte  | 22 = RoutedTo |
| 64–127   | 2 bytes (WORD) | 64 = NewChan, 65 = NewPat |
| 128–191  | 4 bytes (DWORD) | |
| 192–207  | varint-len (TEXT) | 196 = SamplePath, 203 = Name |
| 208–255  | varint-len (DATA) | 213 = Plugin state, 224 = Notes, 233 = Playlist, 238 = TrackData |

Variable length uses 7-bit varint (continuation bit 0x80).

## Key event IDs

| ID | Name | Encoding | Notes |
|----|------|----------|-------|
| 22 | RoutedTo | i8 | Mixer insert index. **0 = Master.** |
| 64 | NewChan | u16 | Channel index; starts a channel block |
| 65 | NewPat | u16 | Pattern number; starts a pattern block |
| 196 | SamplePath | UTF-16 LE + trailing `\x00\x00` | Absolute or `%FLStudioFactoryData%`/`%FLStudioData%` token path |
| 203 | Name | UTF-16 LE + wide null | Channel name AND mixer-slot plugin name |
| 213 | Plugin state | UTF-8 (VST path inside) | Mixer insert FX / VSTi state |
| 215 | (sampler state) | binary floats | Internal/Sampler plugin state |
| 224 | Notes | N × 24-byte notes | Pattern note data (see below) |
| 233 | Playlist | N × 32-byte clips | Arrangement clips (pre-FL21 size) |
| 238 | TrackData | 66-byte struct | Playlist lane: enabled @ byte 12, locked @ 47 |
| 239 | TrackName | UTF-16 LE | Playlist track name |

## Note struct — 24 bytes (CRITICAL)

```
<i  H    H    i    H  H   b B b b b b b b>
pos flags rack len key grp fp _ rel mch pan vel mx my
```

```python
NOTE = struct.Struct("<iHH iHH b B b b b b b b")  # 24 bytes
```

**Gotcha #1 — Slide flag silences notes:** `flags` bit `0x0008` = Slide
(`_NoteFlags.Slide = 1 << 3`). Slide notes do NOT trigger a new hit — they glide
from the previous note's pitch. With no preceding normal note → **no sound, 0% CPU**.
Use `flags = 0x4000` (16384) for normal notes. **Never** `0x4008`.

**Gotcha #2 — midi_channel:** template notes use `midi_channel = 0x80` (i8 = -128).
Match it. A plain `0` may misroute on some channels.

Safe defaults: `flags=16384, fine_pitch=120, release=64, midi_channel=-128,
pan=64, mod_x=-128, mod_y=-128`. `rack_channel` = target channel index, `key` =
MIDI note number, `velocity` 0–127.

## Playlist pattern clip — 32 bytes (CRITICAL)

Pre-FL21 item (matches the phonk mano template):

```python
CLIP = struct.Struct("<I H H I H H 2s H 4s I I")  # 32 bytes
CLIP.pack(position, 0x5000, 0x5000 + pattern, length, 500 - track_iid, 0,
          b"\x78\x00", 0x8040, b"@d\x80\x80", 0, length)
# track_rvidx = 500 - track_iid  (track_iid is 1-based playlist lane)
# item_flags 0x8040 = unmuted; 0x2000 bit / 0xb040 = muted clip (greyed out)
# Last two uint32s for PATTERN clips are (0, length) — same ticks as length.
# Writing float 0.0/0.0 here collapses clips to zero-width slivers in Song mode.
# (Audio clips use real float32 sample offsets instead; do not mix them up.)
```

**Gotcha #3 — pattern clip item_index:** FL identifies a *pattern* clip when the
item_index field holds `0x5000 + pattern_number` (e.g. pattern 5 → `0x5005` =
20485). A **bare small integer** (1, 2, 3…) is read as an *audio-clip* index →
FL plays non-existent audio → **silence, black meters**. Always write
`0x5000 + pattern`. The separate `0x5000` field is a constant marker.

FL21+ uses 60-byte items; match the template's item size exactly or FL crashes
(`FLEngine_x64.dll` access violation).

**Gotcha #4 — playlist track mapping:** pyflp maps
`track_idx = 499 - track_rvidx` to the Nth TrackData event (0-based).
With `track_rvidx = 500 - track_iid`, clips land on playlist track **iid**.
In phonk mano, **iid 1 is disabled+locked** — never put clips on track 1.
Use named enabled lanes, e.g. 3=Cowbell, 4=Bass, 6=Kick, 9=Snares, 14=FX.

**Gotcha #5 — prefer long looping clips:** Many abutting 1-bar clips restart
patterns at every bar and cut 808/crash tails. One long clip of a 1- or 4-bar
pattern loops cleanly for the clip duration.

## Playlist track state (event 238) — CRITICAL for Song mode

```python
# TrackData is typically 66 bytes. Key bytes:
# [0:4]  iid (u32)
# [12]   enabled  (1 = green LED on, 0 = track silent in Song)
# [21]   content_locked
# [47]   locked

def enable_track(payload: bytes) -> bytes:
    data = bytearray(payload)
    data[12] = 1
    if len(data) > 21: data[21] = 0
    if len(data) > 47: data[47] = 0
    return bytes(data)
```

**Always** walk every event 238 after cloning a template and force-enable /
unlock tracks you use (or all of them). PAT mode ignores playlist track mute;
Song mode does not — this is why "patterns work alone but Song is missing parts".

## FL UI Mute tool (speaker+X) — not an FLP bug, but looks like one

Playlist toolbar: **Paint / Pencil / Delete / Mute(speaker) / …**

If **Mute** is selected (often highlighted), every click on a clip greys it out
and silences it in Song mode. Patterns still play fine in PAT mode.

**Recovery in FL:**
1. Click the **Pencil** (draw) tool to leave Mute mode (or press the draw shortcut).
2. If Mute is still needed temporarily: click each **dark/grey** clip once to unmute.
3. Or click the track's **green LED** so the whole lane is on.
4. Do not leave Mute selected while editing the arrangement.

**Generator cannot prevent** the user from re-muting clips in the UI after open.
It **can and must** ship a clean file: no muted clips, no disabled tracks.

## Prevent mute/silence problems in generated FLPs

When writing a project, always do all of these:

1. **Replace** the whole playlist (event 233) with your clips — don't leave
   template clips that may have mute flags (`flags & 0x2000` or `0xb040`).
2. Pack every clip with **`item_flags = 0x8040`** (unmuted).
3. Place clips only on **enabled** track iids (never phonk-mano track 1).
4. Patch **every** event 238: `enabled=1`, clear lock bits.
5. Pattern-clip tails: last 8 bytes = `struct.pack("<II", 0, length)`.
6. Use **long looping** clips per section, not 64× one-bar abutting slices.
7. Route used channels to Master (event 22 = 0); strip missing VSTs.
8. Verify after write: no clip mute bit, no disabled tracks among used iids,
   every sample path `exists()`, no slide notes.

## "No audio" debugging checklist

Walk these in order. Each is a real bug we hit:

1. **Wrong file open?** — Close FL fully, reopen the freshly generated file.
2. **Sample paths missing?** — Repoint event 196; verify `Path(path).exists()`.
   Decode UTF-16 LE (strip only final `\x00\x00`, not `rstrip`).
3. **Notes are slide notes?** — `flags & 0x0008` → use `0x4000`.
4. **Playlist item_index wrong?** — must be `0x5000 + pattern`.
5. **Zero-width playlist slivers?** — pattern clip tails must be uint32
   `(0, length)`, not float `0.0/0.0`.
6. **Song missing parts / PAT fine?** — disabled playlist track (event 238),
   or clips on track iid 1, or muted clips (`flags & 0x2000`), or FL Mute tool
   left active with greyed clips.
7. **Missing insert VSTs?** — route to Master or strip 203/213 for missing plugs.
8. **PAT mode on empty pattern?** — switch to Song, or select a populated pattern.

## Stripping missing VSTs

```python
MISSING = ("Serum","VU Meter","Ozone","CamelCrusher","OTT","Radiator","Kickstart","Valhalla")
for i,(eid,p) in enumerate(events):
    if eid == 203:  # name, UTF-16 LE
        name = p[:-2].decode("utf-16-le","replace") if p.endswith(b"\x00\x00") else p.decode("utf-16-le","replace")
        if any(m in name for m in MISSING): events[i] = None
    elif eid == 213:  # VST state, UTF-8 path inside
        if any(m.encode("utf-16-le") in p or m.encode("utf-8") in p for m in MISSING): events[i] = None
events[:] = [e for e in events if e is not None]
```

Native FL plugins (Fruity Limiter, Soft Clipper, Fruity Reverb) are built in and
never match — leave them.

## Factory sample paths

Use FL's path tokens for portability, or absolute paths for certainty:
- `%FLStudioFactoryData%\Data\Patches\Packs\…`
- `%FLStudioData%\…` (user data)

The factory Phonk pack lives at
`C:\Program Files\Image-Line\FL Studio 2024\Data\Patches\Packs\Phonk\`.

## Verifying a generated FLP

Always re-parse your output and confirm:
- Each used channel's event 196 decodes to a path that `exists()`
- Each used channel's event 22 == 0 (master) or a valid insert
- No remaining 203/213 events match missing-plugin names
- Playlist clips have item_index == `0x5000 + pattern`
- Playlist clips have `item_flags & 0x2000 == 0` and tails `(0, length)`
- No clips on track iid 1 (phonk mano); used tracks' event 238 `enabled == 1`
- Note `flags` has bit `0x0008` clear
- Prefer few long clips over hundreds of abutting 1-bar clips

## Reference

- Full parser/writer code and event-ID tables: see [reference.md](reference.md)
- Generators in this repo:
  - `generate_dark_phonk.py` — phonk mano template, **32-byte** playlist clips
  - `generate_white_armor.py` — Project_5 native synths, **60-byte** (FL24) clips
