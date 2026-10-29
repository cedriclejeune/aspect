"""Build the two-sided combat cheat sheet.

Front: every action, bonus action, reaction and free thing you can do.
Back: a summary of the combat rules (Chapters 5-8 and 10.5 of rules/RULES.md).

Usage: .venv/bin/python tools/build_cheatsheet.py
Output: rules/Aspects-Combat-Cheat-Sheet.pdf (and build/cheatsheet.html for inspection)
Needs: Chromium (set CHROMIUM=/path/to/binary if it isn't on PATH as `chromium`).
The text is written by hand: when a combat rule changes in RULES.md, update it here too.
"""
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BUILD = ROOT / "build"
OUT = ROOT / "rules" / "Aspects-Combat-Cheat-Sheet.pdf"

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">'
         '<link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@500;700&'
         'family=EB+Garamond:ital,wght@0,400;0,600;1,400&display=block" rel="stylesheet">')

CSS = """
@page { size: Letter; margin: 0.4in; background: #f6efdd; }
html { background: #f6efdd; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
body { font-family: 'EB Garamond', Georgia, serif; font-size: 8.6pt; line-height: 1.24; color: #2b1d12; margin: 0; }
.page { height: 10.15in; display: flex; flex-direction: column; break-after: page; overflow: hidden; }
.page:last-child { break-after: auto; }
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
.economy { display: grid; grid-template-columns: repeat(5, 1fr); gap: 5pt; margin-bottom: 8pt; }
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
<header><h1>Actions &amp; Reactions</h1><span class="tag">ASPECTS · Combat Cheat Sheet · v0.1</span></header>

<div class="economy">
  <div><b>Move</b>Up to your speed. Split it before and after your action.</div>
  <div><b>Action</b>One per turn, from the list below.</div>
  <div><b>Bonus Action</b>One per turn, <em>only</em> if a rule or Aspect gives you one.</div>
  <div><b>Free</b>One object interaction (draw, open, pick up). Speak briefly.</div>
  <div class="react"><b>Reaction</b>One per round, on anyone's turn when its trigger occurs. Regained at the start of your turn.</div>
</div>

<div class="cols">
<h2>Actions <small>6.3</small></h2>
<table>
<tr><th>Action</th><th>Effect</th></tr>
<tr><td>Attack</td><td>One weapon or unarmed attack (more with Aspects like <em>Twin Strike</em>). Any attack can be swapped for a <strong>Grapple</strong> or <strong>Shove</strong>.</td></tr>
<tr><td>Cast</td><td>Cast a 1-action spell, or use an Aspect power that takes an action.</td></tr>
<tr><td>Dash</td><td>Extra movement equal to your speed this turn.</td></tr>
<tr><td>Disengage</td><td>Your movement doesn't provoke opportunity attacks this turn.</td></tr>
<tr><td>Dodge</td><td>Until your next turn: attacks against you <strong>−3</strong>, your DEX saves <strong>+3</strong>. Lost if Incapacitated or speed 0.</td></tr>
<tr><td>Help</td><td>Before your next turn, one ally gets <strong>+3</strong> on its next check for a task, or its next attack vs a creature within 5 ft of you.</td></tr>
<tr><td>Hide</td><td>DEX check to hide. Must be out of sight (full cover or Dark). Fails below 15 or below a watcher's passive Awareness. Success: <strong>Invisible</strong> to them.</td></tr>
<tr><td>Use Item</td><td>Use an object or magic item that takes an action.</td></tr>
<tr><td>Ready</td><td>Choose a trigger and an action or move. When it happens, spend your <strong>reaction</strong> to do it.</td></tr>
<tr><td>Search</td><td>INT check to find something hidden.</td></tr>
<tr><td>Recall</td><td>INT check to remember lore.</td></tr>
<tr><td>First Aid</td><td>INT check DC 10: stabilize a dying creature.</td></tr>
<tr><td>Escape</td><td>STR or DEX check vs the grappler's DC (10 + its STR).</td></tr>
<tr><td>Other</td><td>Anything else you describe. The GM rules.</td></tr>
</table>

<div class="box"><b>Grapple &amp; Shove <small>6.10</small></b>
Replaces one attack. Target within reach, at most <strong>one size larger</strong>. It makes a <strong>STR or DEX save</strong> (its choice) vs <strong>DC 10 + your STR</strong>.
<ul>
<li><strong>Grapple</strong> (free hand): target is <strong>Grappled</strong>. Drag it along: each foot costs 1 extra unless it's 2+ sizes smaller.</li>
<li><strong>Shove:</strong> push it 5 ft, or knock it <strong>Prone</strong>.</li>
</ul></div>

<h2>Bonus Actions</h2>
<p>You have none by default. They come from:</p>
<table>
<tr><th>Bonus action</th><th>Effect</th></tr>
<tr><td>Off-hand attack</td><td>After taking the Attack action with a <strong>Light</strong> weapon: one attack with a <em>different</em> Light weapon in the other hand. No ability modifier to damage (unless negative). Both must be equipped Aspects. <small>6.9</small></td></tr>
<tr><td>Potion</td><td>Drink a potion, or give one to a creature within reach.</td></tr>
<tr><td>Spell</td><td>Cast a spell whose casting time is a bonus action.</td></tr>
<tr><td>Aspect</td><td>Any power an Aspect marks as a bonus action.</td></tr>
</table>

<h2>Reactions</h2>
<p>One per round. It works on <strong>anyone's</strong> turn, including your own.</p>
<table>
<tr><th>Reaction</th><th>Trigger → Effect</th></tr>
<tr><td>Opportunity<br>attack</td><td>A creature you can <strong>see</strong> leaves your reach <strong>using its movement</strong> → one melee attack against it. Being pushed, teleporting or Disengage don't provoke. <small>6.5</small></td></tr>
<tr><td>Readied<br>action</td><td>The trigger you named with Ready happens → take the readied action or move.</td></tr>
<tr><td>Spell</td><td>A spell with a reaction casting time, when its trigger occurs (e.g. <em>Shield</em> from <em>Conjurer's Book I</em>). Still one spell paid with points per turn.</td></tr>
<tr><td>Aspect</td><td>Any power an Aspect marks as a reaction (e.g. a looted duelist's parry).</td></tr>
</table>

<div class="box gold"><b>Free (no action)</b>
<ul>
<li>Drop Prone.</li>
<li>One object interaction per turn.</li>
<li>Speak briefly.</li>
<li>End your concentration.</li>
</ul></div>

<h2>Movement <small>6.4</small></h2>
<table>
<tr><th>Move</th><th>Cost</th></tr>
<tr><td>Square</td><td>5 ft, diagonals included</td></tr>
<tr><td>Difficult terrain</td><td>+1 ft per ft (rubble, undergrowth, a creature's space)</td></tr>
<tr><td>Stand up</td><td>Half your speed</td></tr>
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

<div class="box"><b>Things that take your turn away</b>
<ul>
<li><strong>First round, first side:</strong> movement <em>or</em> action, not both (bonus action and reaction kept). Ignored in an <strong>ambush</strong>.</li>
<li><strong>Incapacitated</strong> (also Stunned, Unconscious): no actions, bonus actions or reactions.</li>
<li><strong>Grappled / Restrained / Stunned:</strong> speed 0.</li>
<li><strong>Loading</strong> weapon: one shot per action, bonus action or reaction.</li>
<li>You <strong>can't swap Aspects</strong> during combat.</li>
</ul></div>
</div>
<footer>Section numbers refer to the Aspects Core Rules. Specific beats general: an Aspect that says otherwise wins.</footer>
</section>
"""

BACK = """
<section class="page">
<header><h1>Combat Rules</h1><span class="tag">ASPECTS · Combat Cheat Sheet · v0.1</span></header>
<div class="cols">

<h2>Order of Combat <small>6.1</small></h2>
<ul>
<li><strong>Surprise:</strong> the GM decides who is caught unaware.</li>
<li><strong>Side initiative:</strong> each side rolls <strong>d20 + average DEX</strong> of its members. Surprised side: disadvantage. Reroll ties. A side that is all Invisible: advantage.</li>
<li><strong>Round</strong> (~6 s): first side takes all its turns, then the other side, then <strong>Bosses</strong> take their extra turn.</li>
<li>Within a side, act in any agreed order, one full turn at a time.</li>
<li><strong>First-mover rule:</strong> round 1 only, the first side gets movement <em>or</em> action. <strong>Ambush</strong> (other side surprised): full turns.</li>
</ul>

<h2>Making an Attack <small>6.6</small></h2>
<table>
<tr><th>Roll</th><th>Formula</th></tr>
<tr><td>Melee</td><td>d20 + STR (DEX if Finesse) + weapon Rank bonus</td></tr>
<tr><td>Ranged</td><td>d20 + DEX + weapon Rank bonus (thrown: its melee ability)</td></tr>
<tr><td>Spell</td><td>d20 + INT + book Rank bonus</td></tr>
<tr><td>Unarmed</td><td>+2 Rank bonus · 1 + STR Physical</td></tr>
<tr><td>Improvised</td><td>No Rank bonus · 1d4 Physical</td></tr>
</table>
<ul>
<li><strong>Hit</strong> if total ≥ AC. <strong>Nat 20:</strong> always hits, critical. <strong>Nat 1:</strong> always misses.</li>
<li><strong>Damage:</strong> weapon die + the same ability modifier.</li>
<li><strong>Critical:</strong> roll all damage dice twice, add modifiers once.</li>
<li><strong>Heavy</strong> weapon without STR +1 (melee) / DEX +1 (ranged): −3 to hit.</li>
<li><strong>Rank bonus:</strong> I +2 · II +3 · III +4 · IV +5. Only the highest applies to a roll.</li>
</ul>

<h2>Advantage &amp; Disadvantage <small>5.2</small></h2>
<ul>
<li>Only <strong>situations</strong> give dice: location, position, conditions.</li>
<li>Each source adds a d20; each disadvantage cancels one advantage. Roll <strong>1 + what's left</strong>: keep highest (adv) or lowest (dis). <strong>No cap.</strong> A source counts once.</li>
<li>Nat 20 / nat 1 read on the kept die.</li>
<li><strong>Rank I–II Aspects and actions</strong> (Help, Dodge) give flat <strong>+3 / −3</strong>, not dice. Rank III–IV may give real dice.</li>
</ul>
<div class="adv">
<span>3.9<i>5d20 ↓</i></span><span>4.5<i>4d20 ↓</i></span><span>5.5<i>3d20 ↓</i></span><span>7.2<i>2d20 ↓</i></span>
<span><b>10.5</b><i>1d20</i></span><span>13.8<i>2d20 ↑</i></span><span>15.5<i>3d20 ↑</i></span><span>16.5<i>4d20 ↑</i></span><span>17.2<i>5d20 ↑</i></span>
</div>
<p><em>Average result by d20s rolled, keeping highest ↑ or lowest ↓.</em></p>

<h2>Common Situations</h2>
<table>
<tr><th>Situation</th><th>Effect</th></tr>
<tr><td>You're unseen</td><td>Adv on your attacks</td></tr>
<tr><td>Target unseen</td><td>Dis on your attacks</td></tr>
<tr><td>Beyond normal range</td><td>Dis (beyond long: impossible)</td></tr>
<tr><td>Ranged, enemy within 5 ft</td><td>Dis (if it can see you)</td></tr>
<tr><td>Underwater, no swim speed</td><td>Dis on attacks, half speed, Fire halved</td></tr>
<tr><td>Cover</td><td><strong>+2 AC</strong>, +2 DEX saves</td></tr>
<tr><td>Full cover</td><td>Can't be targeted; blocks areas</td></tr>
</table>

<h2>Conditions <small>8</small></h2>
<table>
<tr><th>Condition</th><th>Effects</th></tr>
<tr><td>Blinded</td><td>Fail sight checks. Attacks vs you adv; yours dis.</td></tr>
<tr><td>Charmed</td><td>Can't harm the charmer. It has adv on CHA checks vs you.</td></tr>
<tr><td>Frightened</td><td>Dis on checks and attacks while source in sight. Can't move closer.</td></tr>
<tr><td>Grappled</td><td>Speed 0. Dis on attacks except vs grappler. Ends if grappler Incapacitated or you're moved out of reach.</td></tr>
<tr><td>Incapacitated</td><td>No actions, bonus actions, reactions or speech. Concentration ends.</td></tr>
<tr><td>Invisible</td><td>Can't be seen. Attacks vs you dis; yours adv.</td></tr>
<tr><td>Poisoned</td><td>Dis on attacks and ability checks.</td></tr>
<tr><td>Prone</td><td>Crawl or stand only. Your attacks dis. Attacks vs you: adv within 5 ft, dis beyond.</td></tr>
<tr><td>Restrained</td><td>Speed 0. Attacks vs you adv; yours dis. Dis on DEX saves.</td></tr>
<tr><td>Stunned</td><td>Incapacitated, speed 0. Auto-fail STR &amp; DEX saves. Attacks vs you adv. <em>(Paralyzed; Petrified = + resist all.)</em></td></tr>
<tr><td>Unconscious</td><td>Stunned + Prone, drops items. <strong>Any hit within 5 ft is a crit.</strong></td></tr>
</table>
<p>Conditions don't stack with themselves.</p>

<div class="box"><b>Exhaustion <small>levels 1–6, stacks</small></b>
Each level: <strong>−2 to all d20 tests, −5 ft speed</strong>. Level 6: death. A long rest removes 1.</div>

<h2>Damage <small>7.2–7.3</small></h2>
<p><strong>Types:</strong> Physical · Fire · Cold · Lightning · Poison · Necrotic · Radiant.</p>
<ul>
<li><strong>Resistance</strong> halves, <strong>vulnerability</strong> doubles. No immunity. Order: other modifiers → resistance → vulnerability. Two resistances = one.</li>
<li><strong>Temp HP:</strong> lost first, don't stack (keep higher), not healing, last until a long rest.</li>
</ul>

<h2>Dropping to 0 HP <small>7.4</small></h2>
<ul>
<li><strong>Monsters</strong> usually die.</li>
<li><strong>Instant death</strong> if leftover damage ≥ your HP max.</li>
<li>Otherwise <strong>Unconscious</strong>, and death saves at the start of each turn.</li>
</ul>
<table>
<tr><th>Death save (d20)</th><th>Result</th></tr>
<tr><td>10+</td><td>1 success</td></tr>
<tr><td>9 or less</td><td>1 failure</td></tr>
<tr><td>Nat 20</td><td>Regain 1 HP</td></tr>
<tr><td>Nat 1</td><td>2 failures</td></tr>
<tr><td>Hit at 0 HP</td><td>1 failure (2 if crit); die if damage ≥ HP max</td></tr>
</table>
<p><strong>3 successes:</strong> stable (1 HP after 1d4 hours). <strong>3 failures:</strong> dead. <strong>Any healing</strong> wakes you and resets the count. <strong>First Aid</strong> (DC 10 INT, action) stabilizes.</p>

<h2>Spells in Combat <small>10</small></h2>
<ul>
<li><strong>Save DC</strong> = Book DC (7/8/9/10 by Rank) + INT. Saves are STR, DEX or INT only.</li>
<li><strong>One spell per turn</strong> paid with spell points (cantrips free). Cost = spell level.</li>
<li>No components. Casting is <strong>obvious</strong> unless the spell is Subtle.</li>
<li>Needs a clear path to a target in range.</li>
</ul>
<div class="box"><b>Concentration <small>10.5</small></b>
One spell at a time. Ends if you cast another, become Incapacitated, die, or choose to. <strong>Taking damage:</strong> INT save, DC <strong>10 or half the damage</strong> (higher), <strong>max 15</strong>.</div>

<h2>Saves &amp; DCs</h2>
<ul>
<li><strong>Save</strong> = d20 + ability modifier + Aspect bonuses. STR: poison, push, grapple, heat/cold. DEX: blasts, traps, breath. INT: mind, fear, charm, concentration.</li>
<li><strong>Monster DC</strong> by CR: 0–1: 10 · 2–3: 11 · 4–5: 12 · 6–7: 13 · 8–10: 14 · 11+: 15.</li>
</ul>

<div class="box gold"><b>Bosses <small>11.3</small></b>
A second full turn at the end of each round. May have <strong>Legendary Resistance</strong> (turn a failed save into a success, X/day). Can't use the same Recharge power on both turns in a round.</div>

<h2>After the Fight</h2>
<ul>
<li><strong>Loot moment:</strong> one character may equip a dropped Aspect at once.</li>
<li><strong>Short rest</strong> (1 h, 2 per long rest): regain half missing HP, swap 1 Aspect.</li>
<li><strong>Long rest</strong> (8 h): all HP, uses and points; rearrange; Shatter; −1 Exhaustion.</li>
</ul>
</div>
<footer>Golden rules: specific beats general · round down · crits and named modifiers don't stack with themselves · the GM decides.</footer>
</section>
"""


def build_html():
    return (f'<!doctype html><html><head><meta charset="utf-8">{FONTS}'
            f'<title>Aspects Combat Cheat Sheet</title><style>{CSS}</style></head>'
            f'<body>{FRONT}{BACK}</body></html>')


def main():
    BUILD.mkdir(exist_ok=True)
    html_path = BUILD / "cheatsheet.html"
    html_path.write_text(build_html(), encoding="utf-8")
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
