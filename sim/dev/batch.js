// DEV: batch fights with a scripted policy, for balance comparisons (sim/QA.md 4 fights).
//   node sim/dev/batch.js [--seeds 40] [--by] [--only <fight name part>] [--log <fight> <seed>] [--no-dmg | --rule75]
// Damage advantage (P 5.2): both sides split leftover advantage dice for the best expected damage; --rule75 moves a
// die while the attack still hits 75% or more without it; --no-dmg keeps every die on the attack.
// The policy is crude and the same in both modes: nearest conscious enemy, best weapon, a few powers
// (heal the dying, buffs once, Bellow, Magic Missile, Bane, Steady Aim, Shield Bash, off-hand), ranged
// creatures step away when engaged. Treat its numbers as comparisons between versions, not tuning advice.
"use strict";
const path = require("path");
const Eng = require("../engine.js");
require("../effects.js");
const CARDS = require(path.join(__dirname, "..", "cards.js"));
const G = Eng.geometry;

globalThis.BEARERS_SCENARIOS = [];
require("../scenarios/party.js");
require("../scenarios/skirmish.js");
require("../scenarios/chieftain.js");
const SC = globalThis.BEARERS_SCENARIOS;

// ---------- fights (sim/QA.md 4) ----------
const LEGEND = { "#": "wall", "~": "difficult", "+": "cover", ":": "dark" };
function cellsOf(rows) { const c = {}; rows.forEach((r, y) => [...r].forEach((ch, x) => { if (LEGEND[ch]) c[x + "," + y] = LEGEND[ch]; })); return c; }
const foeCard = (name) => CARDS.foes.find((f) => f.name === name);
const foe = (id, name, pos, label) => ({ id, side: "foe", name: label || name, pos, build: Eng.fromFoe(foeCard(name), CARDS), react: "auto" });
const party = (n) => globalThis.BEARERS_PARTY([[2, 5], [1, 7], [1, 4], [2, 8]]).slice(0, n).map((c) => Object.assign(c, { react: "auto" }));
const open = (w, h) => ({ w, h, cells: {} });
function fromSample(name) {
  const s = JSON.parse(JSON.stringify(SC.find((x) => x.name.startsWith(name))));
  s.map = { w: s.map.rows[0].length, h: s.map.rows.length, cells: cellsOf(s.map.rows) };
  s.creatures = s.creatures.map((c) => Object.assign(c, { react: "auto", build: c.build || Eng.fromFoe(foeCard(c.foe), CARDS) }));
  return s;
}
const FIGHTS = [
  { name: "4 vs 3 Bandits + 2 Archers (road)", make: () => fromSample("Road ambush") },
  { name: "4 vs 4 Wolves", make: () => ({ map: open(18, 12), creatures: party(4).concat([foe("f1", "Wolf", [10, 3], "Wolf 1"), foe("f2", "Wolf", [10, 5], "Wolf 2"), foe("f3", "Wolf", [10, 7], "Wolf 3"), foe("f4", "Wolf", [10, 9], "Wolf 4")]) }) },
  { name: "4 vs Ogre", make: () => ({ map: open(18, 12), creatures: party(4).concat([foe("f1", "Ogre", [10, 5])]) }) },
  { name: "4 vs Ogre Chieftain (alone)", make: () => ({ map: open(18, 12), creatures: party(4).concat([foe("f1", "Ogre Chieftain", [10, 5])]) }) },
  { name: "Sample Boss: Chieftain + 2 Wolves + Cultist", make: () => fromSample("Boss: the Ogre Chieftain") },
  { name: "2 (Bram, Wren) vs 6 Goblins", make: () => ({ map: open(18, 12), creatures: party(2).concat([2, 3, 5, 6, 8, 9].map((y, i) => foe("f" + i, "Goblin", [10, y], "Goblin " + (i + 1)))) }) },
  { name: "4 vs 3 Legionaries + Captain + Cultist", make: () => ({ map: open(18, 12), creatures: party(4).concat([foe("f1", "Legionary", [9, 3], "Legionary 1"), foe("f2", "Legionary", [9, 5], "Legionary 2"), foe("f3", "Legionary", [9, 7], "Legionary 3"), foe("f4", "Bandit Captain", [11, 5]), foe("f5", "Cultist", [12, 7])]) }) },
];

// ---------- policy ----------
const NO_DMG = process.argv.includes("--no-dmg");
const RULE75 = process.argv.includes("--rule75");
const DMG = { left: 0, moved: 0 };
// Hit chance on d20 + toHit against def with k advantage dice (natural 20 hits, natural 1 misses).
const hitChance = (toHit, def, k) => 1 - Math.pow(1 - Math.min(0.95, Math.max(0.05, (21 - (def - toHit)) / 20)), k + 1);
// Expected highest total of n rolls of a damage expression ("2d6+3 Physical").
function expMax(expr, n) {
  let dist = { 0: 1 }, flat = 0;
  for (const m of String(expr).matchAll(/([+−-]?)\s*(\d+)(?:d(\d+))?/g)) {
    const sign = m[1] === "-" || m[1] === "−" ? -1 : 1;
    if (!m[3]) { flat += sign * +m[2]; continue; }
    for (let i = 0; i < +m[2]; i++) {
      const nd = {};
      for (const [v, q] of Object.entries(dist)) for (let f = 1; f <= +m[3]; f++) nd[+v + sign * f] = (nd[+v + sign * f] || 0) + q / +m[3];
      dist = nd;
    }
  }
  const vs = Object.keys(dist).map(Number).sort((x, y) => x - y);
  let cdf = 0, e = 0;
  for (const v of vs) { const prev = Math.pow(cdf, n); cdf += dist[v]; e += v * (Math.pow(cdf, n) - prev); }
  return e + flat;
}
function withDamageDice(f, cmd) {
  if (cmd.type !== "attack" && cmd.type !== "power") return cmd;
  const pv = f.preview(cmd);
  if (!pv.ok || !pv.info || pv.info.toHit == null || pv.info.defense == null) return cmd;
  const net = (pv.info.adv || 0) - (pv.info.dis || 0);
  if (net <= 0) return cmd;
  const def = typeof pv.info.defense === "number" ? pv.info.defense : Math.max(...String(pv.info.defense).match(/\d+/g).map(Number));
  let k = 0;
  if (RULE75) while (k < net && hitChance(pv.info.toHit, def, net - k - 1) >= 0.75) k++;
  else if (!NO_DMG && pv.info.damage) {
    // the split with the best expected damage (crits ignored)
    let bestEv = -1;
    for (let j = 0; j <= net; j++) {
      const ev = hitChance(pv.info.toHit, def, net - j) * expMax(pv.info.damage, j + 1);
      if (ev > bestEv + 1e-9) { bestEv = ev; k = j; }
    }
  }
  DMG.left += net; DMG.moved += k;
  return k ? Object.assign({}, cmd, { toDamage: k }) : cmd;
}
const conscious = (c) => !c.dead && !c.fled && c.hp > 0;
const CR = (f) => Object.values(f.state.creatures);
const wpn = (id) => CARDS.cards[id] && CARDS.cards[id].atk;
const avg = (d) => { const m = String(d || "1d4").match(/(\d+)d(\d+)/); return m ? +m[1] * (+m[2] + 1) / 2 : 1; };
function reachOf(c) {
  const ws = c.form ? [] : c.hands.map(wpn).filter((w) => w && !w.range);
  return ws.some((w) => w.reach) ? 10 : 5;
}
const isRanged = (c) => !c.form && c.hands.some((id) => wpn(id) && wpn(id).range);
function nearest(f, c, pool) {
  return pool.slice().sort((a, b) => G.dist(c, a) - G.dist(c, b) || a.hp - b.hp)[0];
}
// Positions are top-left squares; space in squares by size.
const SPACE = { Tiny: 1, Small: 1, Medium: 1, Large: 2, Huge: 3, Gargantuan: 4 };
function occupied(f, self, x, y, sideOnly) {
  for (const o of CR(f)) {
    if (o.id === self.id || o.dead || o.fled) continue;
    if (sideOnly && o.side === self.side) continue;
    const n = SPACE[o.size] || 1;
    if (x >= o.pos[0] && x < o.pos[0] + n && y >= o.pos[1] && y < o.pos[1] + n) return true;
  }
  return false;
}
function free(f, c, p, endHere) {
  const st = f.state, n = SPACE[c.size] || 1;
  for (let dx = 0; dx < n; dx++) for (let dy = 0; dy < n; dy++) {
    const x = p[0] + dx, y = p[1] + dy;
    if (x < 0 || y < 0 || x >= st.map.w || y >= st.map.h || st.map.cells[x + "," + y] === "wall") return false;
    if (occupied(f, c, x, y, !endHere)) return false;
  }
  return true;
}
// BFS to the nearest square where goal(pos) holds.
function pathTo(f, c, goal) {
  const key = (p) => p[0] + "," + p[1], prev = new Map([[key(c.pos), null]]), q = [c.pos.slice()];
  let end = null;
  while (q.length) {
    const p = q.shift();
    if (goal(p) && free(f, c, p, true)) { end = p; break; }
    for (const [dx, dy] of [[1, 0], [-1, 0], [0, 1], [0, -1], [1, 1], [1, -1], [-1, 1], [-1, -1]]) {
      const np = [p[0] + dx, p[1] + dy];
      if (!prev.has(key(np)) && free(f, c, np, false)) { prev.set(key(np), p); q.push(np); }
    }
  }
  if (!end) return null;
  const out = [];
  for (let p = end; p && key(p) !== key(c.pos); p = prev.get(key(p))) out.unshift(p);
  return out;
}
const distAt = (c, p, t) => G.dist(Object.assign({}, c, { pos: p }), t);

function Policy(f) {
  const used = {}; // one-off powers already used this fight, by creature
  const once = (c, k) => { used[c.id] = used[c.id] || {}; if (used[c.id][k]) return false; used[c.id][k] = 1; return true; };
  const did = (cmd) => {
    cmd = withDamageDice(f, cmd);
    let r = f.do(cmd);
    for (let i = 0; r.ok && f.pending && i < 20; i++) r = f.do({ type: "answer", choice: f.pending.kind === "reaction" ? null : 0 });
    if (!r.ok && /Engine error/.test(r.error)) throw new Error(r.error + " " + JSON.stringify(cmd));
    return r.ok;
  };
  const power = (c, pid, targets, extra) => did(Object.assign({ type: "power", actor: c.id, power: pid, targets: targets || [] }, extra || {}));
  const powerId = (c, name) => { const o = f.legal(c.id).find((x) => x.type === "power" && x.label.startsWith(name)); return o ? o.power : null; };
  // Move along a path toward goal, as far as the budget allows. maxActs: actions it may spend on it (2a).
  function moveToward(c, goal, keepActs) {
    const p = pathTo(f, c, goal);
    if (!p || !p.length) return false;
    for (let n = p.length; n > 0; n--) {
      const cmd = { type: "move", actor: c.id, path: p.slice(0, n) };
      const pv = f.preview(cmd);
      if (!pv.ok) continue;
      if (keepActs != null) {
        const need = Math.ceil(Math.max(0, pv.info.cost - (c.turn.speed - c.turn.moved)) / Math.max(1, speed(c)));
        if (c.turn.acts - need < keepActs) continue;
      }
      return did(cmd);
    }
    return false;
  }
  const speed = (c) => Math.max(0, c.totals.SPD - (c.conds.some((k) => ["Grappled", "Restrained"].includes(k.name)) ? 999 : 0));
  function attackOpts(c, t) {
    return f.legal(c.id).filter((o) => o.type === "attack" && !o.offhand && o.candidates.includes(t.id))
      .map((o) => ({ o, score: avg(o.weapon === "natural" ? c.form.weapon.dice : wpn(o.weapon) ? wpn(o.weapon).dice : "1d4") + (o.weapon === "unarmed" || o.weapon === "improvised" ? -2 : 0) - (o.thrown ? 0.5 : 0) - (G.dist(c, t) <= 5 && wpn(o.weapon) && (wpn(o.weapon).range || o.thrown) ? 4 : 0) }))
      .sort((a, b) => b.score - a.score).map((x) => x.o);
  }
  function support(c) {
    const allies = CR(f).filter((o) => o.side === c.side && !o.dead && !o.fled);
    const foes = CR(f).filter((o) => o.side !== c.side && conscious(o));
    // heal the dying or badly hurt
    const hurt = allies.filter((o) => o.hp === 0 || o.hp < 0.35 * o.maxHp).sort((a, b) => a.hp - b.hp);
    for (const t of hurt) for (const name of ["Healing Word", "Cure Wounds", "Mossbalm", "Greater Potion of Healing", "Potion of Healing"]) {
      const pid = powerId(c, name);
      if (!pid) continue;
      if (/Potion/.test(name) && t !== c && G.dist(c, t) > 5) continue;
      if (power(c, pid, [t.id])) return true;
    }
    if (c.hp < 0.5 * c.maxHp && powerId(c, "Second Wind") && power(c, powerId(c, "Second Wind"), [c.id])) return true;
    if (allies.length >= 2) for (const name of ["Bless", "Rally", "Rallying Cry"]) {
      const pid = powerId(c, name);
      if (pid && !used[c.id + name]) {
        const near = allies.filter((o) => G.dist(c, o) <= 30 && conscious(o)).slice(0, 3).map((o) => o.id);
        if (power(c, pid, near)) { used[c.id + name] = 1; return true; }
      }
    }
    const bel = powerId(c, "Bellow");
    if (bel && foes.some((o) => G.dist(c, o) <= 30) && power(c, bel, foes.filter((o) => G.dist(c, o) <= 30).map((o) => o.id))) return true;
    const bane = powerId(c, "Bane");
    if (bane && once(c, "bane")) {
      const t = foes.filter((o) => G.dist(c, o) <= 30).sort((a, b) => b.totals.STR - a.totals.STR)[0];
      if (t && power(c, bane, [t.id])) return true;
      used[c.id].bane = 0;
    }
    return false;
  }
  function offense(c, t) {
    // spells first. Hold (Subdue) exists only when sim/dev/subdue.js adds it: the toughest foe, once per foe.
    const hold = powerId(c, "Hold");
    if (hold) {
      const h = CR(f).filter((o) => o.side !== c.side && conscious(o) && G.dist(c, o) <= 60 && !o.conds.some((k) => k.subdue))
        .sort((a, b) => (b.boss - a.boss) || b.hp - a.hp)[0];
      if (h && once(c, "hold" + h.id) && power(c, hold, [h.id])) return true;
    }
    const mm = powerId(c, "Magic Missile");
    if (mm && power(c, mm, [t.id, t.id, t.id])) return true;
    const fb = powerId(c, "Fire Bolt");
    if (fb && !c.hands.some((id) => wpn(id) && wpn(id).range) && G.dist(c, t) > 5 && power(c, fb, [t.id])) return true;
    if (isRanged(c) && G.dist(c, t) > 5) { const sa = powerId(c, "Steady Aim"); if (sa && once(c, "sa" + f.state.turnNo)) power(c, sa, [c.id]); }
    const sw = powerId(c, "Sweeping Blow");
    if (sw && CR(f).filter((o) => o.side !== c.side && conscious(o) && G.dist(c, o) <= reachOf(c)).length >= 2 && power(c, sw, [])) return true;
    const bite = powerId(c, "Bite");
    if (bite && power(c, bite, [t.id])) return true;
    const opts = attackOpts(c, t);
    // ranged creatures shoot unless engaged; others hit in melee
    for (const o of opts) {
      if (!did(Object.assign({}, o, { target: t.id, candidates: undefined, label: undefined }))) continue;
      const sb = powerId(c, "Shield Bash");
      if (sb && conscious(t) && G.dist(c, t) <= 5) power(c, sb, [t.id], { mode: "prone" });
      const oh = f.legal(c.id).find((x) => x.type === "attack" && x.offhand && x.candidates.includes(t.id));
      if (oh && conscious(t)) did(Object.assign({}, oh, { target: t.id, candidates: undefined, label: undefined }));
      return true;
    }
    if (fb && power(c, fb, [t.id])) return true;
    return false;
  }
  function turn(c) {
    if (!did({ type: "beginTurn", actor: c.id })) throw new Error("beginTurn refused " + c.name);
    for (let step = 0; step < 16 && f.state.active === c.id && f.state.phase === "fight"; step++) {
      const foes = CR(f).filter((o) => o.side !== c.side && conscious(o));
      if (!foes.length || c.hp === 0) break;
      if (support(c)) continue;
      // ranged and engaged: step away first
      const engagedBy = foes.filter((o) => G.engaged(c, o));
      if (isRanged(c) && engagedBy.length && once(c, "kite" + f.state.turnNo)) {
        const pv = f.preview({ type: "act", actor: c.id, action: "disengage" });
        if (pv.ok && pv.info.cost !== "action" && did({ type: "act", actor: c.id, action: "disengage" })) {
          moveToward(c, (p) => foes.every((o) => distAt(c, p, o) >= 15), 1);
          continue;
        }
      }
      // pick a target: one in reach, else the nearest
      const inReach = foes.filter((o) => attackOpts(c, o).length && (G.dist(c, o) <= reachOf(c) || isRanged(c) || attackOpts(c, o).some((x) => x.thrown)));
      const t = inReach.length ? nearest(f, c, inReach) : nearest(f, c, foes);
      if (powerId(c, "Bite") && G.dist(c, t) <= 5 && offense(c, t)) continue;
      if ((G.dist(c, t) <= reachOf(c) || (isRanged(c) && !engagedBy.length) || powerId(c, "Magic Missile")) && offense(c, t)) continue;
      // close in, only while an action is left to use there
      if (c.turn.acts <= 0) break;
      const r = reachOf(c);
      if (moveToward(c, (p) => distAt(c, p, t) <= r, 1)) continue;
      if (moveToward(c, (p) => distAt(c, p, t) <= r, 0)) continue;
      if (offense(c, t)) continue; // thrown or ranged from where it stands
      break;
    }
    if (f.state.active === c.id) did({ type: "endTurn", actor: c.id });
  }
  return { turn };
}

// ---------- runner ----------
function runFight(fd, seed, log) {
  const sc = Object.assign({ version: 1, name: fd.name, seed, surprise: null }, fd.make(), { seed });
  sc.surprise = null; // QA 4: rolled initiative
  const f = Eng.createFight(sc, CARDS);
  const P = Policy(f);
  f.do({ type: "start" });
  let guard = 0;
  while (f.state.phase === "fight" && f.state.round <= 30 && guard++ < 2000) {
    const st = f.state;
    const todo = CR(f).filter((c) => c.side === st.side && !c.dead && !c.fled && !st.done.includes(c.id));
    if (!todo.length) break;
    // Bosses on the other side take their half turn after the first character
    if (st.done.length) for (const b of CR(f).filter((c) => c.boss && !c.dead && c.side !== st.side && !st.halfTurn[c.id] && conscious(c))) {
      const ok = f.do({ type: "beginTurn", actor: b.id, half: true }).ok;
      if (ok) { if (f.state.active === b.id) halfTurn(f, P, b); }
    }
    if (f.state.phase !== "fight") break;
    // a half turn can drop the creature that was next
    const next = todo.find((c) => !c.dead && !c.fled);
    if (!next) continue;
    P.turn(next);
  }
  if (log) for (const e of f.events) console.log(e.text);
  const sum = f.summary();
  const stats = Object.values(f.state.stats);
  const rounds = f.state.round;
  const side = (s, k) => stats.filter((x) => x.side === s).reduce((n, x) => n + x[k], 0);
  return {
    win: f.state.winner === "pc", rounds,
    pcDpr: side("pc", "dmgDealt") / rounds, foeDpr: side("foe", "dmgDealt") / rounds,
    downs: side("pc", "downs"), deaths: CR(f).filter((c) => c.side === "pc" && c.dead).length,
    foeZero: side("foe", "dmgDealt") === 0, sum,
  };
}
// A Boss half turn: Bellow or one attack (or movement), through the same policy pieces.
function halfTurn(f, P, b) {
  const foes = CR(f).filter((o) => o.side !== b.side && conscious(o));
  const near = foes.filter((o) => G.dist(b, o) <= 30);
  const bel = f.legal(b.id).find((x) => x.type === "power" && x.label.startsWith("Bellow"));
  if (bel && near.length && f.do({ type: "power", actor: b.id, power: bel.power, targets: near.map((o) => o.id) }).ok) { /* used */ }
  else {
    const t = foes.filter((o) => G.dist(b, o) <= reachOf(b)).sort((a, c) => a.hp - c.hp)[0];
    const o = t && f.legal(b.id).find((x) => x.type === "attack" && !x.offhand && x.candidates.includes(t.id));
    if (o) f.do(withDamageDice(f, { type: "attack", actor: b.id, weapon: o.weapon, target: t.id }));
  }
  while (f.pending) f.do({ type: "answer", choice: f.pending.kind === "reaction" ? null : 0 });
  if (f.state.active === b.id) f.do({ type: "endTurn", actor: b.id });
}

function main() {
  const arg = (k, d) => { const i = process.argv.indexOf(k); return i > 0 ? process.argv[i + 1] : d; };
  const seeds = +arg("--seeds", 40), only = arg("--only", null);
  const li = process.argv.indexOf("--log");
  if (li > 0) {
    const fd = FIGHTS.find((x) => x.name.includes(process.argv[li + 1]));
    const r = runFight(fd, +process.argv[li + 2] || 1, true);
    console.log(JSON.stringify(Object.assign({}, r, { sum: undefined })));
    return;
  }
  console.log("| Fight | PC win | Rounds avg (min–max) | PC DPR | Foe DPR | PC downs / fight | PC deaths (total) | Foes dealt 0 |");
  console.log("|---|---|---|---|---|---|---|---|");
  for (const fd of FIGHTS) {
    if (only && !fd.name.includes(only)) continue;
    const rs = [];
    for (let s = 1; s <= seeds; s++) rs.push(runFight(fd, s));
    const m = (k) => rs.reduce((n, r) => n + r[k], 0) / rs.length;
    const rr = rs.map((r) => r.rounds);
    console.log(`| ${fd.name} | ${rs.filter((r) => r.win).length}/${seeds} | ${m("rounds").toFixed(1)} (${Math.min(...rr)}–${Math.max(...rr)}) | ${m("pcDpr").toFixed(1)} | ${m("foeDpr").toFixed(1)} | ${m("downs").toFixed(1)} | ${rs.reduce((n, r) => n + r.deaths, 0)} | ${rs.filter((r) => r.foeZero).length} |`);
    // --by: damage per round of each Bearer
    if (process.argv.includes("--by")) {
      const by = {};
      for (const r of rs) for (const x of Object.values(r.sum.creatures)) if (x.side === "pc") by[x.name] = (by[x.name] || 0) + x.dmgDealt / r.rounds / rs.length;
      console.log(`|  | ${Object.entries(by).map(([k, v]) => `${k} ${v.toFixed(1)}`).join(", ")} |`);
    }
  }  console.log(`\nAdvantage dice left after cancelling: ${DMG.left}, moved to damage: ${DMG.moved} (${(100 * DMG.moved / Math.max(1, DMG.left)).toFixed(0)}%).`);
}
if (require.main === module) main();
module.exports = { runFight, FIGHTS };
