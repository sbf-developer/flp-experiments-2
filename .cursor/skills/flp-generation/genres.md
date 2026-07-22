# Genre & Template Guide

Maps musical intent → template choice, playlist lanes, and generator patterns.

---

## Template selection

| Template | Path | Clip size | Best for |
|----------|------|-----------|----------|
| phonk mano | `%FLStudioFactoryData%\…\Phonk\phonk mano\phonk mano.flp` | 32-byte | Sample-based phonk, drums, 808, cowbell |
| Project_5 | `Documents\…\Projects\Project_5\Project_5.flp` | 60-byte | Native synths (Sakura, Morphine, Autogun, choir) |

**Never mix clip sizes** — match template exactly or FL crashes.

---

## phonk mano — playlist lanes (verified)

| iid | Track name | Use for |
|-----|------------|---------|
| 1 | Original | **NEVER** — disabled in template |
| 2 | Cowbell | Cowbell / hook patterns |
| 3 | Bass & Subscribe | 808 / bass patterns |
| 5 | Kick | Drums / kick patterns |
| 8 | Snares | Perc / ghost / spice |
| 13 | FX | Impacts, risers, crashes |

Generators: `generate_dark_phonk.py`, `generate_hardstyle_phonk.py`

---

## Project_5 — channels & lanes

| Channel | Plugin role | Playlist lane (iid) |
|---------|-------------|---------------------|
| 0 | Sakura — main pad | 1 Pads |
| 1 | Autogun — shimmer | 3 Shimmer |
| 2 | Morphine — deep pad | 2 Deep |
| 3 | Reese — sub shadow | 6 Sub |
| 4 | Sakura hi | (in pad patterns) |
| 5 | Sakura mid | (in pad patterns) |
| 6 | Lead synth | 4 Lead |
| 7 | Air choir | 5 Choir |
| 8 | FX | 7 FX |

All Project_5 lanes iid 1–7 enabled. Generators: `generate_white_armor.py`, `generate_pale_meridian.py`

---

## Dark phonk

- **BPM:** 130–140 · **Key:** Ab or F# minor
- **Hook:** cowbell minor pentatonic / syncopated 8ths
- **Drums:** half-time kick (1 + 3), clap 2+4, ghost snares
- **808:** root-heavy, 4-bar walks, bass shot on downbeats
- **Arrangement:** intro sparse → verse full → break half-time → drop dense → outro fade
- **Avoid:** 4-on-floor kick; major chords; busy cowbell every 16th

---

## Hardstyle × phonk hybrid

- **BPM:** 150 · **Key:** F# minor
- **Verse:** half-time phonk (pat 5)
- **Drop:** four-on-floor kick (pat 6) + reverse-bass 808 pump
- **Build:** hardtekk snare roll (16ths crescendo) into drop
- **Break:** ultra-slowed — kick on 1 only, strip 808 to drone
- **Avoid:** mixing half-time and 4-on-floor in same section without transition

---

## Dreamscape / ambient synth

- **BPM:** 76–88 · **Key:** Eb major, D minor, or F Lydian
- **Harmony:** I–IV–vi–V or I–IV–I–V; voice-led pad voicings
- **Lead:** enters bar 12+; long notes (360–540 ticks); pentatonic
- **Shimmer:** Autogun vel 22–30; not continuous in intro
- **Sub:** Reese vel 34–40; follows roots, not busy
- **Choir:** chord tones only; vel 18–28
- **Arrangement:** mist (12 bars) → bed → voice → peak → dissolve
- **Avoid:** short staccato everything; phonk drums; dense percussion

---

## Encoding reminder

Musical choices live in `production.md`. After composing:

1. Clone correct template
2. Patch event 224 (notes) + 233 (playlist) + 238 (enable tracks)
3. Set tempo (event 156 = BPM × 1000)
4. Name patterns (event 193) and tracks (event 239)
5. Run verify checklist in `SKILL.md`
