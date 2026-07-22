# Music Production — Theory, Composition & Arrangement

Use this **before** writing notes or playlist clips. The FLP format layer
(`SKILL.md`, `reference.md`) encodes what you compose — it does not fix bad
harmony, muddy density, or incoherent structure.

**Advanced:** [production-advanced.md](production-advanced.md) — modes, borrowed
chords, hooks, low-end, tension, reference analysis, quality rubric.
**Brief template:** [song-brief-template.md](song-brief-template.md)

---

## Core workflow: compose → arrange → encode → verify

```
1. Intent    — mood, genre, tempo, key, reference tracks (1–3)
2. Harmony   — key + 4–8 bar progression with voice-leading
3. Roles     — assign each channel a job (kick = pulse, pad = bed, lead = identity…)
4. Patterns  — write PAT-mode loops; each must sound good alone
5. Arrangement — 8-bar grid: add/subtract/transform per section
6. Encode    — clone template, patch Notes + Playlist (SKILL.md)
7. Verify    — FLP checklist + musical checklist (below)
```

**Rule:** If it sounds bad in PAT mode on one pattern, Song mode will not save it.

---

## Four pillars (every track needs all four)

| Pillar | Job | Failure mode |
|--------|-----|--------------|
| **Melody** | Identity, memory, emotional line | Random notes, no contour, fights the chord |
| **Harmony** | Emotional color, tonal home | Clashing chord tones, root jumps every bar |
| **Rhythm** | Groove, pulse, genre DNA | Everything on every beat; no pocket |
| **Arrangement** | Energy over time, contrast | 64-bar loop with no sections; density soup |

Composition = writing the ideas. Arrangement = when they enter, exit, and how dense the mix is.

---

## Music theory essentials

### Key & scale

Pick **one tonal center** per section (or whole track). All non-chromatic notes should
resolve toward it.

| Mood | Common keys/scales |
|------|-------------------|
| Dark / phonk | Minor (Ab, F#, Dm), Phrygian color |
| Dreamy / ambient | Major (Eb, D, F), Lydian (#4) for float |
| Tense / hardstyle | Minor + raised leading tone near drops |
| Warm / soulful | Major, mixolydian |

### Chord building (triads in a major key)

| Degree | Roman | Example in Eb | Feel |
|--------|-------|---------------|------|
| I | I | Eb | home, stable |
| ii | ii | Fm | gentle tension |
| iii | iii | Gm | color |
| IV | IV | Ab | lift, open |
| V | V | Bb | pull home |
| vi | vi | Cm | bittersweet |
| vii° | vii° | Ddim | unstable (use sparingly) |

**Strong progressions (memorize these):**
- Pop/ambient: **I – IV – vi – V** (Eb – Ab – Cm – Bb)
- Emotional: **vi – IV – I – V** (Cm – Ab – Eb – Bb)
- Dark phonk: **i – VI – III – VII** (Abm – F – Cb/E – Eb) or simpler **i – iv – i – V**
- Dreamscape: **I – IV – I – V** or **I – vi – IV – V** with long note lengths

### Voice leading (critical for pads & choir)

When changing chords, **minimize motion**:

1. **Keep common tones** in the same register/voice.
2. **Move other voices by step** (1–2 semitones) when possible.
3. **Bass may leap** to the new root; upper voices should not.
4. **Avoid parallel fifths/octaves** in two upper voices moving together (classical rule; less strict in pop bass+lead, but still avoid muddy doubles).
5. **Resolve tendency tones**: leading tone → up to tonic; chord 7th → down by step.

```python
# Good: Eb → Ab with common tone Eb held
# Eb pad: Eb3, G3, Bb3  →  Ab pad: Ab2, C4, Eb4  (Eb held/repeated)

# Bad: every voice jumps to new root-position voicing every bar
```

### Melody

- **Contour:** arch (up then down) or question-answer (call → response).
- **Strong beats:** prefer chord tones (1, 3, 5 of current chord).
- **Weak beats:** passing tones, neighbor tones OK.
- **Range:** lead usually 1–1.5 octaves; leave space below for bass, above for air.
- **Length:** long notes = calm; short = energy. Match genre.
- **Pentatonics** are safe for hooks: major (1-2-3-5-6), minor (1-b3-4-5-b7).

### Rhythm & groove

- **Four-on-floor** = hardstyle/house pulse (kick 1-2-3-4).
- **Half-time** = phonk/drill feel (kick on 1, snare/clap on 3).
- **Syncopation** = off-beat emphasis; use sparingly in ambient, heavily in phonk.
- **Ghost notes** = low-velocity layers; never full velocity on everything.
- **Genre contract:** phonk = swung/clap on 2+4; hardstyle = 150 BPM 4/4; ambient = 60–90 BPM, sparse.

---

## Arrangement & energy management

### 8-bar phrase grid

Electronic music is built in **8-bar blocks**. Introduce, remove, or transform
elements at 8-bar boundaries (4 or 16 also OK if deliberate).

| Section | Typical length | Energy | What to do |
|---------|---------------|--------|------------|
| Intro | 8–16 bars | Low | 1–2 elements; set mood |
| Verse / bed | 8–16 bars | Low–mid | Establish groove + harmony |
| Build | 4–8 bars | Rising | Add layers, rolls, filter rise |
| Drop / peak | 16–32 bars | High | Full stack; drop kick+bass together |
| Break | 8–16 bars | Low | **Remove** kick + sub (tension via absence) |
| Bridge | 8 bars | Mid | Variation without full drop |
| Outro | 8–16 bars | Falling | Subtract until 1 element remains |

### Subtractive arrangement (recommended)

1. Build the **fullest section first** (usually drop or peak).
2. Duplicate it across the timeline.
3. **Mute/remove** elements to carve intro, break, outro.
4. Every mute should have a reason: contrast, tension, breathing room.

### Tension & release

- **Removing** kick + bass before a drop creates more impact than adding more noise.
- Kick must **not** return until bar 1 of the drop (exact downbeat).
- Breakdown: keep melody/pad/atmosphere; strip rhythm section.
- Builds: snare rolls, risers, HPF automation — but don't stack all at once.

### Density rules

- **Max ~4 elements** in the same frequency band (e.g. 60–120 Hz: kick + 808 + sub + bass pad = mud).
- **One role per playlist lane** — cowbell on Cowbell track, not Bass track.
- **Long looping clips** > 64 abutting 1-bar slices (tails cut, patterns restart awkwardly).
- If bored → add **variation** (new pattern every 8 bars). If muddy → **subtract**.

---

## Register & orchestration (channel roles)

Assign before writing notes:

| Register | Hz (approx) | Roles |
|----------|-------------|-------|
| Sub | 30–60 | 808 root, reese shadow — **one owner** |
| Bass | 60–200 | Bass shots, low synth |
| Low-mid | 200–500 | Body, warmth |
| Mid | 500–2k | Pads, snares, claps, cowbell |
| High-mid | 2k–6k | Lead, choir air |
| Air | 6k+ | Shimmer, hats, FX |

**Velocity hierarchy:** kick/snare loudest in drums; pads 40–60; ghosts 25–45;
ambient layers very soft. Not everything at 127.

---

## Pre-encoding checklist (musical quality)

Before patching the FLP, confirm:

### Harmony
- [ ] Key chosen; progression written (at least 4 bars, ideally 8)
- [ ] Voice-leading: common tones held, upper voices move by step
- [ ] No random chromatic notes outside key (unless passing tones)

### Melody
- [ ] Lead has contour and rests; not a wall of 16ths
- [ ] Melody notes mostly chord tones on downbeats
- [ ] Lead enters **after** bed is established (not bar 1 unless intentional)

### Rhythm
- [ ] One clear groove per section (don't mix half-time + 4-on-floor same bar)
- [ ] Kick/snare/clap not all identical velocity
- [ ] Fills only before section changes (1 bar max)

### Arrangement
- [ ] Sections mapped on 8-bar grid with labels (intro/verse/build/drop/break/outro)
- [ ] Each section has **fewer or different** elements than the last (contrast)
- [ ] Break removes kick + bass before next drop
- [ ] Clips on **correct playlist lanes** (verify template track iids!)
- [ ] Pattern names describe content (not "Pattern 12")

### Mix-ready habits (even in MIDI)
- [ ] One sub/bass owner per section
- [ ] Pad velocities layered (root loudest, extensions softer)
- [ ] FX/spice lanes not playing continuously through whole track

---

## Genre → musical choices (this repo)

| Genre | Template | BPM | Key | Groove | Arrangement notes |
|-------|----------|-----|-----|--------|-------------------|
| Dark phonk | phonk mano | 130–140 | Ab/F# min | Half-time clap 2+4 | Cowbell hook + 808 walk; sparse intro |
| Hardstyle phonk | phonk mano | 150 | F# min | 4-on-floor + phonk clap | Half-time verse → hardtekk build → drop |
| Dreamscape | Project_5 | 76–88 | Eb/D maj | None/minimal | Long pad chords; lead after bar 12; choir soft |
| Cold synth | Project_5 | 88 | D min | None | White Armor model: I–IV–vi–V, sparse lead |

See [genres.md](genres.md) for template track maps and generator conventions.

---

## Common mistakes we hit (learn from these)

| Symptom | Cause | Fix |
|---------|-------|-----|
| Incoherent mess | Wrong playlist lane iids | Dump template TrackData; map lanes |
| Everything fights | All elements same register/velocity | Spread octaves; velocity tiers |
| Boring loop | No arrangement, one 4-bar clip | 8-bar grid; subtractive sections |
| Drop weak | Kick never left | Break without kick+bass |
| Ambient harsh | Too many notes, short lengths | Long releases; fewer chord tones |
| Phonk dead | Slide notes / wrong item_index | FLP checklist in SKILL.md |
| Tails cut | 64× 1-bar abutting clips | One long clip per section |

---

## Reference listening workflow

When user gives playlist/mood references:

1. Identify **tempo band**, **major/minor**, **density** (sparse vs stacked).
2. Note **one signature element** (cowbell, pad wash, reverse bass…).
3. Map to **section lengths** (intro long or short? double drop?).
4. Choose template + key + progression **before** coding patterns.

Do not copy references literally — extract **structure and feel**.
