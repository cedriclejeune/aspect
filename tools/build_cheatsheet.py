"""Build the two-sided combat cheat sheet.

Front: every action, reaction and free thing you can do on a turn.
Back: a summary of the combat rules (Chapters 5-8 and 10 of rules/PLAYERS.md).

Usage: .venv/bin/python tools/build_cheatsheet.py [--lang fr]
Output: rules/Bearers-Combat-Cheat-Sheet.pdf (and build/cheatsheet.html for inspection)
--lang fr: the French sheet from tools/cheatsheet_fr.py, in rules/fr/Porteurs-Aide-memoire-combat.pdf
Needs: Chromium (set CHROMIUM=/path/to/binary if it isn't on PATH as `chromium`).
The text is written by hand: when a combat rule changes in PLAYERS.md, update it here too.
"""
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BUILD = ROOT / "build"
OUT = ROOT / "rules" / "Bearers-Combat-Cheat-Sheet.pdf"

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">'
         '<link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@500;700&'
         'family=EB+Garamond:ital,wght@0,400;0,600;1,400&display=block" rel="stylesheet">')

CSS = """
@page { size: Letter; margin: 0.4in; background: #f6efdd; }
html { background: #f6efdd; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
body { font-family: 'EB Garamond', Georgia, serif; font-size: 8.6pt; line-height: 1.24; color: #2b1d12; margin: 0; }
.page { height: 10.15in; display: flex; flex-direction: column; break-after: page; overflow: hidden; }
.page:last-child { break-after: auto; }
.page.dense { font-size: 7.9pt; line-height: 1.2; }
.page.dense h2 { margin-top: 5pt; }
.page.dense td { padding: 1.4pt 3.5pt; }
header { display: flex; align-items: baseline; justify-content: space-between;
  border-bottom: 2.5px solid #8a1c1c; padding-bottom: 3pt; margin-bottom: 7pt; }
header h1 { font-family: Cinzel, serif; color: #8a1c1c; font-size: 19pt; margin: 0; letter-spacing: .05em; }
header .tag { font-family: Cinzel, serif; color: #b07d2b; font-size: 8.5pt; letter-spacing: .08em; }
.cols { column-count: 3; column-gap: 12pt; column-fill: balance; }
.cols.two { column-count: 2; }
h2 { font-family: Cinzel, serif; color: #8a1c1c; font-size: 10.5pt; margin: 7pt 0 3pt;
  border-bottom: 1.3px solid #b07d2b; padding-bottom: 1pt; break-after: avoid; }
h2:first-child { margin-top: 0; }
h2 small { font-size: 7pt; color: #b07d2b; letter-spacing: .04em; }
p { margin: 0 0 3.5pt; }
ul { margin: 0 0 4pt; padding-left: 11pt; }
li { margin: 0 0 1.6pt; }
strong { color: #3a1f10; }
em { color: #5a4630; }
table { width: 100%; border-collapse: collapse; margin: 1pt 0 5pt; break-inside: avoid; }
th { font-family: Cinzel, serif; font-size: 7.2pt; background: #8a1c1c; color: #f6efdd; text-align: left; padding: 2pt 4pt; }
td { padding: 1.8pt 4pt; border-bottom: 1px solid #e0cfa6; vertical-align: top; }
tr:nth-child(even) td { background: rgba(176,125,43,.09); }
td:first-child { font-weight: 600; color: #3a1f10; white-space: nowrap; }
.box { break-inside: avoid; background: #fbf6e9; border: 1.5px solid #2b1d12; border-radius: 6px;
  padding: 4pt 6pt 3pt; margin: 0 0 6pt; box-shadow: 2px 2px 0 #e6d8b5; }
.box > b:first-child { display: block; font-family: Cinzel, serif; font-size: 8.4pt; color: #8a1c1c; margin-bottom: 1.5pt; }
.box.gold { border-color: #b07d2b; }
.economy { display: grid; grid-template-columns: 2fr 1fr 1fr; gap: 5pt; margin-bottom: 8pt; }
.economy div { background: #fbf6e9; border: 1.5px solid #2b1d12; border-radius: 6px; padding: 3pt 5pt 4pt;
  box-shadow: 2px 2px 0 #e6d8b5; font-size: 8pt; }
.economy b { display: block; font-family: Cinzel, serif; color: #fbf6e9; background: #8a1c1c;
  margin: -3pt -5pt 3pt; padding: 2pt 5pt; border-radius: 4px 4px 0 0; font-size: 8.3pt; }
.economy div.react b { background: #b07d2b; }
.adv { display: flex; gap: 0; margin: 2pt 0 4pt; font-size: 7pt; text-align: center; }
.adv span { flex: 1; border: 1px solid #e0cfa6; padding: 1pt 0; }
.adv span i { display: block; font-style: normal; color: #7a6648; font-size: 6.4pt; }
footer { font-size: 6.8pt; color: #7a6648; text-align: center; margin-top: auto; }
"""

FRONT = """
<section class="page">
<header><h1>Actions &amp; Reactions</h1><span class="tag">BEARERS · Combat Cheat Sheet</span></header>

<div class="economy">
  <div><b>Two Actions</b>Any two from the list below, in any order. The same one twice is fine: Move twice, Attack twice. No bonus actions.</div>
  <div><b>Free</b>One object interaction (draw, open, pick up). Speak briefly.</div>
  <div class="react"><b>Reaction</b>One per round, on anyone's turn when its trigger occurs, or on your own turn if it has none. Regained at the start of your turn.</div>
</div>

<div class="cols">
<h2>Actions <small>6.3</small></h2>
<table>
<tr><th>Action</th><th>Effect</th></tr>
<tr><td>Move</td><td>Move up to your speed. You can split it around your other action.</td></tr>
<tr><td>Attack</td><td>One weapon or unarmed attack (more with Aspects like <em>Twin Strike</em>). Any attack can be swapped for a <strong>Grapple</strong> or <strong>Shove</strong>.</td></tr>
<tr><td>Cast</td><td>Cast a 1-action spell, or use a power of your gear or Aspects that takes an action (Anthem, Dirge, Shift into a Form).</td></tr>
<tr><td>Disengage</td><td>Your movement doesn't provoke opportunity attacks this turn. <strong>Not while Surrounded.</strong></td></tr>
<tr><td>Dodge</td><td>Until your next turn: <strong>+3 to all your Defenses</strong>. Lost if Incapacitated or speed 0.</td></tr>
<tr><td>Help</td><td>Before your next turn, one ally gets <strong>+3</strong> on its next check for a task, or its next attack vs a creature within 5 ft of you.</td></tr>
<tr><td>Hide</td><td>DEX check to hide. Must be out of sight (full cover or Dark). Fails below 15 or below a watcher's passive Awareness. Success: <strong>Invisible</strong> to them.</td></tr>
<tr><td>Use</td><td>Use an object, or gear that takes an action: drink or give a potion.</td></tr>
<tr><td>Stand up</td><td>Stand from Prone.</td></tr>
<tr><td>Ready</td><td>Choose a trigger and an action or move. When it happens, spend your <strong>reaction</strong> to do it.</td></tr>
<tr><td>Search</td><td>INT check to find something hidden.</td></tr>
<tr><td>Recall</td><td>INT check to remember lore.</td></tr>
<tr><td>First Aid</td><td>INT check DC 10: stabilize a dying creature.</td></tr>
<tr><td>Escape</td><td>Unarmed attack (STR or DEX + 2) vs the grappler's higher of STR / DEX Defense. Hit: you're free.</td></tr>
<tr><td>Hold on<br><small>both actions</small></td><td>Keep a Subdue going: the next repeat that hits adds no decay.</td></tr>
<tr><td>Other</td><td>Anything else you describe. The GM rules.</td></tr>
</table>

<div class="box"><b>Grapple &amp; Shove <small>6.10</small></b>
Replaces one attack. Target within reach, at most <strong>one size larger</strong>. Make an <strong>unarmed attack (STR + 2)</strong> vs its higher of STR and DEX Defense.
<ul>
<li><strong>Grapple</strong> (free hand): target is <strong>Grappled</strong>. Drag it along: each foot costs 1 extra unless it's 2+ sizes smaller.</li>
<li><strong>Shove:</strong> push it 5 ft, or knock it <strong>Prone</strong>.</li>
</ul></div>

<h2>Reactions</h2>
<p>One per round. It works on <strong>anyone's</strong> turn, including your own.</p>
<table>
<tr><th>Reaction</th><th>Trigger → Effect</th></tr>
<tr><td>Opportunity<br>attack</td><td>A creature you can <strong>see</strong> leaves your reach <strong>by moving</strong> → one melee attack against it. Being pushed, teleporting or Disengaging don't provoke. <small>6.5</small></td></tr>
<tr><td>Off-hand<br>attack</td><td>You attack with a <strong>Light</strong> weapon → one attack with a <em>different</em> Light weapon in your other hand. No ability modifier to damage (unless negative). Both in Hand Slots. <small>6.9</small></td></tr>
<tr><td>Readied<br>action</td><td>The trigger you named with Ready happens → take the readied action or move.</td></tr>
<tr><td>Spell</td><td>A spell with a reaction casting time (e.g. <em>Shield</em> from <em>Conjurer's Book</em>). Needs an empty Hand.</td></tr>
<tr><td>Cue</td><td>Divine or Glamour: change a roll by a creature within 60 ft who hears you, <strong>after the roll</strong>, before the GM says if it succeeds.</td></tr>
<tr><td>Gear &amp; Aspects</td><td>Any power marked <strong>Reaction</strong>. With a trigger: <em>Ring of Warding</em> (an attack hits you → +2 to that Defense). Without one, on your own turn: <em>Alchemist's Fire</em> (throw a flask).</td></tr>
</table>

<div class="box gold"><b>Free (no action)</b>
<ul>
<li>One object interaction per turn.</li>
<li>Speak briefly.</li>
<li>Drop Prone.</li>
<li>End a spell you cast.</li>
<li>Revert from a Form (on your turn).</li>
</ul></div>

<h2>Movement <small>6.4</small></h2>
<table>
<tr><th>Move</th><th>Cost</th></tr>
<tr><td>Square</td><td>5 ft, diagonals included</td></tr>
<tr><td>Difficult terrain</td><td>+1 ft per ft (rubble, undergrowth, a creature's space)</td></tr>
<tr><td>Stand up</td><td>An action</td></tr>
<tr><td>Crawl</td><td>+1 ft per ft</td></tr>
<tr><td>Climb / swim</td><td>+1 ft per ft without a climb / swim speed</td></tr>
<tr><td>Drag a grappled foe</td><td>+1 ft per ft (unless 2+ sizes smaller)</td></tr>
<tr><td>Long jump</td><td>10 + 2×STR ft (half without a 10-ft run-up)</td></tr>
<tr><td>High jump</td><td>3 + STR ft (half without a run-up)</td></tr>
</table>
<ul>
<li>Pass through an <strong>ally</strong> (difficult terrain), or an <strong>enemy</strong> only if it's 2 sizes larger or smaller.</li>
<li>You can't end your turn in another creature's space.</li>
</ul>

<div class="box"><b>Limits on your turn</b>
<ul>
<li><strong>First round, first side:</strong> one action instead of two (reaction kept). Ignored in an <strong>ambush</strong>.</li>
<li><strong>Incapacitated</strong> (also Stunned, Unconscious): no actions or reactions.</li>
<li><strong>Surrounded</strong> (3+ enemies engaged with you): no Disengage.</li>
<li><strong>Grappled / Restrained / Stunned:</strong> speed 0.</li>
<li><strong>Loading</strong> weapon: one shot per action or reaction.</li>
<li><strong>Spellbook:</strong> needs an empty Hand to cast.</li>
<li><strong>Divine &amp; Glamour:</strong> need your voice. Not while Incapacitated, underwater or shifted.</li>
<li><strong>Subdued:</strong> you lose your turn until a repeat misses.</li>
</ul></div>
</div>
<footer>Section numbers refer to the Bearers Player Rules. Specific beats general: gear or an Aspect that says otherwise wins.</footer>
</section>
"""

BACK = """
<section class="page dense">
<header><h1>Combat Rules</h1><span class="tag">BEARERS · Combat Cheat Sheet</span></header>
<div class="cols">

<h2>Order of Combat <small>6.1</small></h2>
<ul>
<li><strong>Surprise:</strong> a side that sneaks up unnoticed surprises the other and goes first, no roll.</li>
<li><strong>Side initiative:</strong> otherwise each side rolls <strong>d20 + the best DEX</strong> among its members. Reroll ties. A side that is all Invisible: advantage.</li>
<li><strong>Round</strong> (~6 s): first side takes all its turns, then the other side.</li>
<li><strong>Bosses</strong> also take a <strong>half turn</strong> (one action) during the characters' side.</li>
<li>Within a side, act in any agreed order, one full turn at a time.</li>
<li><strong>First-mover rule:</strong> round 1 only, the first side gets one action each. <strong>Ambush</strong> (other side surprised): full turns.</li>
</ul>

<h2>Making an Attack <small>6.6</small></h2>
<p>The <strong>attacker always rolls</strong> vs a <strong>Defense</strong> (10 + ability + bonuses). Weapons hit the <strong>higher of STR / DEX Defense</strong>; other effects name theirs.</p>
<table>
<tr><th>Roll</th><th>Formula</th></tr>
<tr><td>Weapon</td><td>d20 + the ability it names (higher of two: STR / DEX, staff or wand INT / WIL) + to-hit</td></tr>
<tr><td>Spell</td><td>d20 + INT + book's Spell attack</td></tr>
<tr><td>WIL magic</td><td>d20 + WIL + printed Attack</td></tr>
<tr><td>Unarmed</td><td>+2 to hit · 1 + STR Physical</td></tr>
<tr><td>Improvised</td><td>+0 to hit · 1d4 + STR Physical</td></tr>
</table>
<ul>
<li><strong>Hit</strong> if total ≥ Defense. <strong>Nat 20:</strong> always hits, critical. <strong>Nat 1:</strong> always misses.</li>
<li><strong>Damage:</strong> weapon die + the same modifier. <strong>Crit:</strong> damage dice twice, modifiers once.</li>
<li><strong>Area:</strong> roll once vs each target's Defense, only the You question. Miss = half damage.</li>
</ul>

<h2>The Three Questions <small>5.2</small></h2>
<p>Ask before each attack. Each gives <strong>one die at most</strong>; reasons both ways cancel inside a question.</p>
<table>
<tr><th>Question</th><th>Advantage</th><th>Disadvantage</th></tr>
<tr><td>You</td><td>You're unseen</td><td>Long range, target unseen, enemy within 5 ft of your bow, you're Prone, Restrained, Poisoned…</td></tr>
<tr><td>Target</td><td>It's Prone, Restrained or Stunned</td><td>—</td></tr>
<tr><td>Crowd</td><td>Your side outnumbers</td><td>Its side outnumbers</td></tr>
</table>
<ul>
<li>Checks and saves: only <strong>You</strong> applies.</li>
<li>Each disadvantage cancels one advantage. Roll <strong>1 + what's left</strong>: keep highest (adv) or lowest (dis). Nat 20 / 1 read on the kept die.</li>
<li><strong>Advantage on damage:</strong> before rolling, move leftover advantage dice to damage. Each one rolls all damage again; keep the best. Disadvantage stays on the attack.</li>
<li>Gear, Aspects, Help and Dodge give <strong>flat</strong> bonuses (+3 / −3), not dice.</li>
</ul>
<div class="adv">
<span>4.5<i>4d20 ↓</i></span><span>5.5<i>3d20 ↓</i></span><span>7.2<i>2d20 ↓</i></span>
<span><b>10.5</b><i>1d20</i></span><span>13.8<i>2d20 ↑</i></span><span>15.5<i>3d20 ↑</i></span><span>16.5<i>4d20 ↑</i></span>
</div>

<h2>Engagement <small>6.5</small></h2>
<ul>
<li><strong>Engaged:</strong> within 5 ft of an enemy, neither Incapacitated, at most one size apart.</li>
<li><strong>Outnumbered</strong> (Crowd): count around the <em>target</em>. Your side = your creatures engaged with it. Its side = the target (if engaged by your side) + its allies within 5 ft. More = 1 adv die, fewer = 1 dis die. Same dice for every attacker, melee or ranged.</li>
<li><strong>Surrounded:</strong> 3+ enemies engaged with you → no Disengage.</li>
</ul>

<h2>Cover <small>6.8</small></h2>
<ul>
<li><strong>Cover:</strong> +2 to STR and DEX Defense.</li>
<li><strong>Full cover:</strong> can't be targeted; blocks sight and areas; lets you hide and approach unseen.</li>
</ul>

<h2>Conditions <small>8</small></h2>
<table>
<tr><th>Condition</th><th>Effects</th></tr>
<tr><td>Blinded</td><td>Fail sight checks. Attacks vs you adv; yours dis.</td></tr>
<tr><td>Charmed</td><td>Can't harm the charmer. It has adv on WIL checks vs you.</td></tr>
<tr><td>Frightened</td><td>Dis on checks and attacks while source in sight. Can't move closer.</td></tr>
<tr><td>Grappled</td><td>Speed 0. Dis on attacks except vs grappler. Ends if it's Incapacitated or you leave its reach.</td></tr>
<tr><td>Incapacitated</td><td>No actions, reactions or speech. Not engaged with anyone.</td></tr>
<tr><td>Invisible</td><td>Can't be seen. Attacks vs you dis; yours adv.</td></tr>
<tr><td>Poisoned</td><td>Dis on attacks and ability checks.</td></tr>
<tr><td>Prone</td><td>Crawl or stand only. Your attacks dis. Attacks vs you: one adv die, any range.</td></tr>
<tr><td>Restrained</td><td>Speed 0. Attacks vs you adv; yours dis.</td></tr>
<tr><td>Stunned</td><td>Incapacitated, speed 0. Attacks vs you adv. <em>Petrified: + resist all.</em></td></tr>
<tr><td>Unconscious</td><td>Stunned + Prone, drops items. <strong>Any hit within 5 ft is a crit.</strong></td></tr>
</table>
<p>Conditions don't stack with themselves.</p>

<div class="box"><b>Subdue <small>8</small></b>
<ul>
<li><strong>Hit:</strong> target loses its next turn.</li>
<li><strong>Repeat</strong> at the start of each of its turns, free: same bonus vs same Defense, only decay dice. Hit: it loses that turn too. Miss: it breaks free.</li>
<li><strong>Decay:</strong> each repeat that hits, and each time the source takes damage, adds 1 disadvantage die.</li>
<li><strong>Ends</strong> on a miss, if the source is Incapacitated or dies, or chooses to. Harming a Charmed target frees it.</li>
</ul></div>

<h2>Damage <small>7.2–7.3</small></h2>
<ul>
<li><strong>Resistance</strong> halves, <strong>vulnerability</strong> doubles (applied in that order, after other modifiers). Two resistances = one.</li>
<li><strong>Temp HP:</strong> lost first, don't stack (keep higher), not healing, last until a long rest.</li>
</ul>

<h2>Falling to 0 HP <small>7.4</small></h2>
<ul>
<li><strong>Instant death</strong> if leftover damage ≥ your HP max.</li>
<li>Otherwise <strong>Unconscious</strong>; roll a death save (d20, no modifiers) at the start of each turn. You take a <strong>Wound</strong> (7.6).</li>
</ul>
<table>
<tr><th>Death save</th><th>Result</th></tr>
<tr><td>10+</td><td>1 success</td></tr>
<tr><td>9 or less</td><td>1 failure</td></tr>
<tr><td>Nat 20</td><td>Regain 1 HP</td></tr>
<tr><td>Nat 1</td><td>2 failures</td></tr>
<tr><td>Hit at 0 HP</td><td>1 failure (2 if crit); die if damage ≥ HP max</td></tr>
</table>
<p><strong>3 successes:</strong> stable (1 HP after 1d4 hours). <strong>3 failures:</strong> dead. <strong>Any healing</strong> wakes you and resets the count. <strong>First Aid</strong> (DC 10 INT, action) stabilizes.</p>

<h2>Magic in Combat <small>10</small></h2>
<ul>
<li><strong>Spellbook:</strong> an empty Hand to cast. One pool of <strong>spell points</strong> (all books + INT) pays any book's spells (cost 1/2/3/4/6/8 by level, cantrips free). Obvious unless Subtle.</li>
<li><strong>Divine, Glamour, Nature:</strong> WIL, paid from one pool of <strong>Resolve</strong> (all decks + WIL, back on a short rest). Always obvious.</li>
<li><strong>Forms:</strong> gear stops counting; Form HP goes first, extra damage carries over.</li>
</ul>

<div class="box gold"><b>Morale <small>6.11</small></b>
When a foe group's <strong>Leader</strong> falls, and when half the group is down: one <strong>WIL check (DC 10)</strong> with its best WIL. Fail: the group flees or surrenders. Bosses never check.</div>

<h2>After the Fight <small>7.5</small></h2>
<ul>
<li><strong>Short rest</strong> (1 h, 2 per long rest): regain half missing HP; S.R. uses and Resolve return; don or doff Armor.</li>
<li><strong>Long rest</strong> (8 h): all HP, uses, Resolve and spell points; swap Aspects.</li>
<li><strong>Downtime</strong> (3 days somewhere safe): as a long rest, and heals all your Wounds.</li>
</ul>
</div>
<footer>Golden rules: the rule of fun · no one left out · specific beats general · round down · everything stacks · the GM decides.</footer>
</section>
"""


def build_html(lang="en"):
    if lang == "fr":
        sys.path.insert(0, str(Path(__file__).parent))
        import cheatsheet_fr
        return (f'<!doctype html><html lang="fr"><head><meta charset="utf-8">{FONTS}'
                f'<title>Porteurs · Aide-mémoire de combat</title><style>{CSS}</style></head>'
                f'<body>{cheatsheet_fr.FRONT}{cheatsheet_fr.BACK}</body></html>')
    return (f'<!doctype html><html><head><meta charset="utf-8">{FONTS}'
            f'<title>Bearers Combat Cheat Sheet</title><style>{CSS}</style></head>'
            f'<body>{FRONT}{BACK}</body></html>')


def main():
    global OUT
    lang = sys.argv[sys.argv.index("--lang") + 1] if "--lang" in sys.argv else "en"
    if lang == "fr":
        OUT = ROOT / "rules" / "fr" / "Porteurs-Aide-memoire-combat.pdf"
    BUILD.mkdir(exist_ok=True)
    html_path = BUILD / ("cheatsheet-fr.html" if lang == "fr" else "cheatsheet.html")
    html_path.write_text(build_html(lang), encoding="utf-8")
    subprocess.run(
        [
            os.environ.get("CHROMIUM", "chromium"), "--headless", "--disable-gpu", "--no-sandbox",
            "--no-pdf-header-footer", "--virtual-time-budget=20000", f"--print-to-pdf={OUT}",
            html_path.as_uri(),
        ],
        check=True, capture_output=True,
    )
    print(f"Wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
