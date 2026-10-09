# Aspects (working title)

A streamlined, classless, level-less variant of fifth edition.
Characters are built from interchangeable **Aspects** placed in **Slots**: weapons, armor, spellbooks, traits and techniques are all Aspects. Loot them from defeated enemies, swap them at rests, and **Shatter** spare ones to open new Slots.

- Core loop: **explore → fight → loot → rest & rebuild**
- Power ceiling: roughly a level-12 character in fifth edition
- Setting-agnostic (for now)

## Contents
| Path | What |
|---|---|
| [rules/PLAYERS.md](rules/PLAYERS.md) | Player Rules (standalone, source) |
| [rules/GM.md](rules/GM.md) | Game Master's Guide: running the world, monsters, Bosses, loot, encounters |
| [rules/DESIGN.md](rules/DESIGN.md) | Internal design rules: Rank scaling, card constraints, design notes, fifth-edition conversion (no PDF) |
| [rules/Aspects-Player-Rules.pdf](rules/Aspects-Player-Rules.pdf) · [rules/Aspects-GM-Guide.pdf](rules/Aspects-GM-Guide.pdf) | Illustrated PDFs |
| [tools/](tools/) | `build_pdf.py` (PDF), `illustrations.py` (SVG art), `shatter_sim.py` (economy simulation, obsolete since Shatter was removed) |
| [ATTRIBUTION.md](ATTRIBUTION.md) | SRD 5.2.1 CC-BY-4.0 attribution |
| [CHANGELOG.md](CHANGELOG.md) | Version history |

## Roadmap
1. **v0.1** Core rulebook
2. v0.2 Aspect catalog (Cores, Rank I–II Aspects) as YAML + generated catalog
3. v0.3 Monster conversions, balance pass, Rank III–IV Aspects
4. v0.4 First playtest (pregens, one-shot)
5. Later: printed cards, character sheets, setting

## Building the PDF
```
.venv/bin/pip install markdown
.venv/bin/python tools/build_pdf.py
```
Needs Chromium. Fonts (Cinzel, EB Garamond) load from Google Fonts at build time.
