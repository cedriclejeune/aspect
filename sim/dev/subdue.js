// DEV: how long a Subdue lasts (P 8, DESIGN 5). Gives Isolde a Rank I Subdue spell (Hold: Stunned, WIL) and runs
// the batch fights, then prints the turns each Hold took from its target.
//   node sim/dev/subdue.js [--seeds 40]
"use strict";
const path = require("path");
const Eng = require("../engine.js");
const CARDS = require(path.join(__dirname, "..", "cards.js"));
const { runFight, FIGHTS } = require("./batch.js");

CARDS.decks["B-I-01"].powers.push({ id: "B-I-01#hold", name: "Hold", kind: "Spell", cost: 2, use: "action", reach: 60, target: "enemy",
  atk: { abil: "deck", vs: "WIL" }, do: [{ cond: "Stunned" }], lasting: true, subdue: true });

const arg = (k, d) => { const i = process.argv.indexOf(k); return i > 0 ? process.argv[i + 1] : d; };
const seeds = +arg("--seeds", 40);
const pct = (n, d) => (d ? Math.round(100 * n / d) + "%" : "–");
const log = [];
let wins = 0, n = 0, rounds = 0;
for (const fd of FIGHTS) for (let s = 1; s <= seeds; s++) {
  Eng.dev.log = [];
  const r = runFight(fd, s);
  wins += r.win; n++; rounds += r.rounds;
  log.push(...Eng.dev.log); // holds still running when the fight ended aren't counted
}
Eng.dev.log = null;
console.log(`Turns lost per Hold (Boss: turns and half turns), ${seeds} seeds × ${FIGHTS.length} fights. PC wins ${pct(wins, n)}, ${(rounds / n).toFixed(1)} rounds.`);
console.log("| Target | Ended while up | 1 | 2 | 3 | 4+ | Avg | Downed while held |");
console.log("|---|---|---|---|---|---|---|---|");
for (const boss of [false, true]) {
  const all = log.filter((x) => x.boss === boss), up = all.filter((x) => x.why !== "target");
  const c = (k) => pct(up.filter((x) => x.lost === k).length, up.length);
  const avg = up.length ? (up.reduce((a, x) => a + x.lost, 0) / up.length).toFixed(2) : "–";
  console.log(`| ${boss ? "Boss" : "regular"} | ${up.length} | ${c(1)} | ${c(2)} | ${c(3)} | ${pct(up.filter((x) => x.lost >= 4).length, up.length)} | ${avg} | ${pct(all.length - up.length, all.length)} |`);
}
