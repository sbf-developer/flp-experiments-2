# flp-experiments-2

Programmatic FL Studio `.flp` generation (clone-and-patch, not from-scratch).

## Generators

| Script | Output | Notes |
|--------|--------|-------|
| `generate_dark_phonk.py` | `out/dark_phonk.flp` | Phonk mano template, 32-byte playlist clips |
| `generate_hardstyle_phonk.py` | `out/covenant_strike.flp` | Hardstyle × dark phonk, 150 BPM, F# minor |
| `generate_white_armor.py` | `out/white_armor.flp` | Project_5 native synths, 60-byte (FL24) clips |
| `generate_pale_meridian.py` | `out/pale_meridian.flp` | Chill Eb-major dreamscape, 76 BPM, 60-byte clips |

```bash
python generate_dark_phonk.py
python generate_hardstyle_phonk.py
python generate_white_armor.py
python generate_pale_meridian.py
```

Requires FL Studio 2024 locally (factory packs / existing project templates).

## Skill

Hard-won FLP format notes live in [`.cursor/skills/flp-generation/`](.cursor/skills/flp-generation/) (`SKILL.md` + `reference.md`).

## Repo

https://github.com/sbf-developer/flp-experiments-2
