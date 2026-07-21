# flp-experiments-2

Programmatic FL Studio `.flp` generation (clone-and-patch, not from-scratch).

## Generators

| Script | Output | Notes |
|--------|--------|-------|
| `generate_dark_phonk.py` | `out/dark_phonk.flp` | Phonk mano template, 32-byte playlist clips |
| `generate_white_armor.py` | `out/white_armor.flp` | Project_5 native synths, 60-byte (FL24) clips |

```bash
python generate_dark_phonk.py
python generate_white_armor.py
```

Requires FL Studio 2024 locally (factory packs / existing project templates).

## Skill

Hard-won FLP format notes live in [`.cursor/skills/flp-generation/`](.cursor/skills/flp-generation/) (`SKILL.md` + `reference.md`).

## Repo

https://github.com/sbf-developer/flp-experiments-2
