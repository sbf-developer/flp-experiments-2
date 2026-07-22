# Advanced Music Production

Deep reference for **making tracks that actually sound good** — theory, hooks,
low-end, tension, sound design, reference analysis. Read after skimming
[production.md](production.md); use **before** encoding to FLP.

Sources: [Native Instruments voice leading](https://blog.native-instruments.com/voice-leading/),
[BeatKey borrowed chords](https://chords.beatkey.app/borrowed-chords),
[iZotope kick/bass](https://www.izotope.com/en/learn/how-to-mix-kick-and-bass),
[Beat Kitchen bass design](https://beatkitchen.io/guides/electronic-music/04-bass-design/),
[Orphiq hooks](https://orphiq.com/resources/how-to-write-a-hook),
[Born To Produce structure](https://www.borntoproduce.com/blogs/blog/what-is-song-structure-arrangement-guide),
[Mastering.com tension/release](https://mastering.com/5-ways-to-create-tension-and-release-in-modern-production/),
[Red Star layering](https://redstar.media/guides/production/sound-design-fundamentals).

---

## 1. Emotional intent (start here)

Before key/tempo, define **one sentence**:

> "Listener should feel ___ for ___ bars, then ___ at the drop."

| Intent | Harmonic color | Arrangement | Density |
|--------|---------------|-------------|---------|
| Cold float | Lydian / major 9 pads | Long intro, slow lead entry | Very sparse |
| Dark menace | Minor + Phrygian b2 | Short intro, early cowbell | Mid → heavy drop |
| Anthem lift | IV → I, bVII borrow | Build 8 bars, wide drop | Strip break, full stack |
| Ultra slowed | Half-time, long 808 | Minimal elements, space | Low avg density |
| Hardtekk rush | Minor, snare roll build | 4-on-floor drop | High transient density |

Every arrangement decision should pass: **"Does this serve the intent?"**

---

## 2. Advanced harmony

### Modes (same root, different color)

| Mode | Intervallic color | Use for |
|------|-------------------|---------|
| Ionian (major) | Bright, resolved | Pop beds, dreamscape home |
| Aeolian (natural minor) | Dark, stable minor | Phonk, trap, hardstyle |
| Dorian | Minor but brighter (major 6) | Jazz phonk, groove |
| Phrygian | b2 tension | Dark phonk, evil color |
| Lydian | #4 float | Dream pads, filmic |
| Mixolydian | b7 rock pull | bVII → I energy |

### Borrowed chords (modal interchange)

From **parallel minor** while staying in major (example: Eb major):

| Borrowed | Chord in Eb | Effect | Resolve to |
|----------|-------------|--------|------------|
| iv | Abm | melancholy twist | Eb or Bb |
| bVI | Cb/B | cinematic drama | Bb or Eb |
| bVII | Db | anthemic rock lift | Eb |
| bIII | Gb | bluesy/soul | Ab or Eb |

**Rules:** Establish key first (2–4 bars diatonic). One borrowed chord = color.
Always **resolve** — borrowed chords are guests, not a new key.

Example dreamscape: `Eb – Ab – Abm – Eb` (iv for one bar of bittersweet).

Example phonk (F# minor): `F#m – D – C# – B` (i – VI – V – VII).

### Cadences ( endings that feel finished or unresolved )

| Cadence | Progression | Feel |
|---------|-------------|------|
| Authentic | V → I (Bb → Eb) | Strong home |
| Plagal | IV → I (Ab → Eb) | Gentle amen |
| Deceptive | V → vi (Bb → Cm) | Surprise, not done |
| Half | anything → V | Suspended, wants more |

Use **deceptive** before a drop (Bb → Cm) to delay resolution, then slam I at drop.

### Extended chords (pads & choir)

| Chord | Notes (Eb) | Mood |
|-------|--------------|------|
| maj7 | Eb G Bb D | lush, jazzy |
| min7 | C Eb G Bb | soft minor |
| sus4 | Ab Db Eb | open, unresolved |
| sus2 | Ab Bb Eb | airy |
| add9 | Eb G Bb F | sparkle without 7th tension |

Dreamscape pads: stack root + 3rd + 5th + 7th across octaves; root loudest.

---

## 3. Hook & melody craft

### The hook formula

Best hooks share DNA ([Orphiq](https://orphiq.com/resources/how-to-write-a-hook),
[Wisseloord](https://wisseloord.org/academy/how-to-write-memorable-melodies-that-people-cant-forget)):

1. **≤5 distinct pitch classes** in the motif
2. **Leap up, step down** — fourth/fifth jump, then conjunct return
3. **Rhythmic identity** — syncopation often beats more notes
4. **2–4 bar cell** — statement (bars 1–2) + answer (bars 3–4)
5. **Rule of three** — repeat 3×, vary on 4th
6. **Peak note** on title moment or emotional apex

### Contour templates

```
Arch:        low → peak bar 2–3 → resolve home
Question:    rise with open ending (ends on 2 or 5)
Answer:      fall to root/octave
Wave:        up-down-up-down (phonk cowbell)
```

### Shower test

Hum the lead/hook after 24h away. Can't remember it → simplify.

### Instrumental vs vocal

| Type | Priority |
|------|----------|
| Vocal hook | Lyric rhythm locks first; open vowels on peaks |
| Synth lead | Contour + rhythm first; harmony second |
| Cowbell hook | 3–5 notes, syncopated, minor pentatonic |
| Shimmer | High register, soft vel, chord tones only |

### Contrast rule

Hook section must feel **different** from bed: higher register, longer notes,
or denser rhythm — not just louder velocity.

---

## 4. Low-end design (compose stage)

Most mud is decided **before mixing** ([iZotope](https://www.izotope.com/en/learn/how-to-mix-kick-and-bass),
[Beat Kitchen](https://beatkitchen.io/guides/electronic-music/04-bass-design/)).

### Frequency ownership

| Element | Owns (Hz) | Generator note |
|---------|-----------|----------------|
| Kick sub thump | 40–70 | One kick per groove |
| 808 fundamental | 40–80 | Root of key |
| Bass synth body | 80–150 | Different note or off-beat |
| Bass shot | 100–300 | Short, not continuous |

### Composition rules

1. **Tune kick** to key OR place bass notes around kick fundamental.
2. **Alternate** kick downbeat / bass off-beat (house, hardstyle).
3. **Half-time phonk:** kick 1 + clap 3; 808 long — don't stack kick+808 same tick every bar unless intentional.
4. **One sub owner** — 808 OR reese, not both loud.
5. **Break:** remove kick AND 808/sub together for max drop impact.

### Phonk 808 patterns

| Pattern | Feel |
|---------|------|
| Long root (4 bars) | Ultra slowed, covenant vibe |
| Root → fifth → root | Walk, movement |
| Stab on 1 + ghost on 3 | Hardstyle pump |
| Low octave slide (portamento in FL) | Reverse bass feel — use note retrigger |

---

## 5. Sound design & layering

Even with factory samples / native synths, think in **spectral layers**
([Red Star](https://redstar.media/guides/production/sound-design-fundamentals)):

| Layer | Hz | Role | Velocity |
|-------|-----|------|----------|
| Sub | 20–80 | Weight | 808/reese 34–127 |
| Body | 80–500 | Warmth | Pads 40–60 |
| Presence | 500–5k | Cut | Snare, cowbell, clap |
| Air | 5k+ | Shimmer | Autogun 22–30 |

**Each layer one job.** Can't articulate its job → remove it.

Project_5 dreamscape stack:
- Morphine = sub/body · Sakura = mid pad · Sakura hi = air · Choir = chord tones · Autogun = sparkle

Phonk mano stack:
- Kick = sub thump · 808 = bass · Cowbell = mid hook · Snares = presence · FX = transitions only

---

## 6. Tension & release toolkit

Beyond "add snare roll" ([Mastering.com](https://mastering.com/5-ways-to-create-tension-and-release-in-modern-production/)):

| Technique | Implementation | Best for |
|-----------|----------------|----------|
| Sub starvation | Remove kick+808 4–8 bars before drop | EDM, hardstyle |
| Filter rise | HPF sweep on pad (automate in FL) | Builds |
| Stereo narrow → wide | Break mono, drop wide | Anthem drops |
| Rhythmic acceleration | 16ths crescendo → silence 1 beat | Hardtekk |
| Reverb swell | Send up on build, snap dry at drop | Dreamscape |
| Deceptive harmony | V → vi instead of V → I | Pre-chorus |
| Strategic silence | 1 beat empty before downbeat | Any drop |

**Kick re-entry:** exactly bar 1 of drop — never early.

---

## 7. Reference track analysis protocol

When user gives references ([AudioServices](https://audioservices.studio/blog/deconstructing-a-reference-track)):

### Step 1 — Quantify
- BPM (tap tempo / analyzer)
- Key (play along, find bass landing note)
- Major/minor, density (sparse vs stacked)

### Step 2 — Map structure
Place markers every section change. Count bars per section:

```
Intro:     bars 0–16   (16) — elements: pad only
Verse:     bars 16–32  (16) — + drums, + bass
Build:     bars 32–40  (8)  — + roll, filter
Drop:      bars 40–56  (16) — full stack
...
```

### Step 3 — Element matrix

| Section | Kick | Bass | Lead | Pad | FX |
|---------|------|------|------|-----|-----|
| Intro | — | — | — | ✓ | light |
| Drop | ✓ | ✓ | ✓ | ✓ | hit |

### Step 4 — Extract, don't copy
Take: **bar lengths, energy curve, one signature timbre**
Don't take: exact notes, exact sample, exact chord voicing

### Step 5 — Write brief

```markdown
## Song brief
- Title:
- Intent: listener feels ___ then ___
- BPM / Key:
- Template: phonk mano | Project_5
- Progression: (8 bars)
- Reference structure: intro 16 / verse 16 / build 8 / drop 16
- Signature element: cowbell | pad wash | reverse 808
- Avoid: (what references don't do)
```

---

## 8. Section contrast matrix

Every section must differ from the previous ([Born To Produce](https://www.borntoproduce.com/blogs/blog/what-is-song-structure-arrangement-guide)):

| Dimension | Low energy | High energy |
|-----------|------------|-------------|
| Element count | 1–2 | 5–7 |
| Register | mid only | sub → air full |
| Rhythm | half-time / none | 4-on-floor / dense |
| Harmony | 1 chord / drone | full progression |
| Velocity avg | 30–50 | 80–127 |
| FX | long reverb tail | dry, transient |

**Second drop** should differ from first: add choir, higher lead, or new percussion — not a copy-paste.

---

## 9. Quality rubric (score before encoding)

Rate 1–5; **don't encode below 4 average**:

| Criterion | 1 (bad) | 5 (good) |
|-----------|---------|----------|
| **Hook** | No identifiable motif | Hum-able in one listen |
| **Harmony** | Random notes | Voice-led progression |
| **Groove** | Clashing rhythms | One clear pocket |
| **Sections** | Single loop | 8-bar grid, contrast |
| **Density** | Everything always on | Add/subtract deliberate |
| **Register** | All same octave | Sub/mid/air separated |
| **Low-end** | Kick+808 fight | Alternating or owned bands |
| **Intent** | Generic | Mood obvious in 8 bars |

---

## 10. Generator integration checklist

When writing `generate_*.py`:

```python
# At top of file — document musical decisions
SONG_BRIEF = """
Intent: cold dreamscape → warm peak → dissolve
Key: Eb major | BPM: 76
Progression: Eb Ab Cm Bb (8 bars, voice-led)
Structure: 12 mist / 12 bed / 12 voice / 12 peak / 12 outro
"""
```

- [ ] `SONG_BRIEF` comment block present
- [ ] Progression written in comments before patterns
- [ ] Each pattern function named by **role** not bar count
- [ ] Velocities tiered (not all 100+)
- [ ] Lead enters after bed (unless intro is hook-led)
- [ ] Break section removes kick+bass patterns from playlist
- [ ] Second peak differs from first (pattern swap)
- [ ] Track iids verified against [genres.md](genres.md)
- [ ] Musical rubric ≥ 4/5 mentally confirmed

---

## 11. Study path (becoming good)

Rotating focus — one per new generator:

1. **Voice leading** — dreamscape pads only, no drums
2. **Groove** — drums only, one chord drone
3. **Hook** — 4-bar motif, minimal backing
4. **Arrangement** — same loops, structure only changes
5. **Low-end** — kick + 808 ownership
6. **Reference clone** — map reference bars, original notes

Re-analyze one reference track per week: BPM, key, bar map, element matrix.

---

## Quick decision tree

```
New track request?
├─ Has references? → Analyze (§7) → brief → harmony → patterns
├─ Genre phonk/hardstyle? → phonk mano, verify iids 2/3/5/8/13
├─ Genre ambient/synth? → Project_5, 60-byte clips, long notes
├─ Sounds muddy? → Subtract layers (§5), check low-end (§4)
├─ Sounds boring? → Hook (§3), not more notes
├─ Drop weak? → Break without kick+bass (§6)
└─ Silent in FL? → SKILL.md FLP checklist (format layer)
```
