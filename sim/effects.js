/*
 * Bearers card effects (sim/SPEC.md section 5): the named special cases (`hook` in a power).
 * Loads after engine.js, in a page (globalThis.BearersEngine) or under Node (require).
 *
 *   close_order  Gladius    passive: +params.dmg damage while an ally is engaged with the same creature
 *   brace        Boarspear  rider on its opportunity attacks: +params.dmg damage
 *   pierce       Pilum      rider on a hit: the target's Shield gives no bonus until it pulls the pilum free
 *                           (a "Pierced" condition; the engine offers the action to end it)
 *   sweep        Sweeping Blow  action power: the Attack action as one roll against each enemy within the reach of a
 *                           held melee weapon with one of params.props (Heavy, Reach); half damage on a miss
 */
(function (root, factory) {
  const Eng = root.BearersEngine || (typeof require === "function" ? require("./engine.js") : null);
  const api = factory(Eng);
  root.BearersEffects = api;
  if (typeof module !== "undefined" && module.exports) module.exports = api;
})(typeof globalThis !== "undefined" ? globalThis : this, function (Eng) {
  "use strict";
  if (!Eng) return {};
  const params = (ctx) => ctx.power.params || {};

  // Close Order (Gladius): judged when the damage is rolled.
  Eng.registerHook("close_order", {
    modifyDamage(ctx) {
      if (ctx.role !== "attacker" || !ctx.target) return;
      const a = ctx.actor, t = ctx.target;
      const ally = ctx.creatures().find((c) => c.side === a.side && c !== a && ctx.engaged(c, t));
      if (!ally) return;
      ctx.damage.parts.push({ dice: params(ctx).dmg || "1d4", type: ctx.damage.type });
      ctx.emit({ t: "note", actor: a.id, target: t.id, power: ctx.power.id, text: `Close Order: +${params(ctx).dmg || "1d4"} (${ally.name} is engaged with ${t.name}).` });
    },
  });

  // Brace (Boarspear): the engine only runs this rider on an opportunity attack with the spear.
  Eng.registerHook("brace", {
    modifyDamage(ctx) {
      ctx.damage.parts.push({ dice: params(ctx).dmg || "1d8", type: ctx.damage.type });
      ctx.emit({ t: "note", actor: ctx.actor.id, target: ctx.target && ctx.target.id, power: ctx.power.id, text: `Brace: +${params(ctx).dmg || "1d8"}.` });
    },
  });

  // Pierce (Pilum). RULING R401: any hit with the pilum (thrown or in melee) pierces a Shield the target holds;
  // its Defense bonus is gone until the target spends an action to pull the pilum free. A target without a
  // Shield in hand is unaffected.
  Eng.registerHook("pierce", {
    onTrigger(ctx) {
      const t = ctx.trigger.target;
      if (!t || t.dead || t.form) return;
      const shield = t.hands.find((id) => ctx.cards.cards[id] && (ctx.cards.cards[id].type || ctx.cards.cards[id].kw[0]) === "Shield");
      if (!shield) return;
      ctx.addCond(t, "Pierced", { card: shield, endAction: "Pull the pilum free", power: "Pierce" });
    },
  });

  // Sweeping Blow: an Attack action made as an area roll (Eng areaWeaponAttack). cmd.weapon picks the weapon when
  // several qualify (default: the first one in hand); cmd.targets may name a subset of the enemies in reach.
  // RULING R601: "each enemy within your reach" counts enemies within the chosen weapon's reach that the attacker has
  // a clear line to; by default it leaves out enemies at 0 HP (the attacker may still name them in cmd.targets).
  // RULING R602: the sweep is the whole Attack action: no extra attacks (Twin Strike) and no two-weapon bonus attack
  // after it, and it can't follow an attack already made with the action. Triggers on taking the Attack action fire.
  const sweepWeapon = (ctx) => {
    const a = ctx.actor, props = params(ctx).props || ["heavy", "reach"];
    if (a.form) return null;
    const ok = (id) => { const cd = ctx.cards.cards[id]; return cd && cd.atk && !cd.atk.range && props.some((k) => cd.atk[k]); };
    const id = ctx.cmd && ctx.cmd.weapon ? ctx.cmd.weapon : a.hands.find(ok);
    return id && a.hands.includes(id) && ok(id) ? ctx.weapon(id) : null;
  };
  const sweepTargets = (ctx, w) => {
    const a = ctx.actor, reach = ctx.weaponReach(w);
    const pool = ctx.creatures().filter((t) => t.side !== a.side && !t.dead && ctx.distance(a, t) <= reach && ctx.sees(a, t) &&
      !a.conds.some((k) => k.name === "Charmed" && k.source === t.id));
    const ids = ctx.cmd && ctx.cmd.targets && ctx.cmd.targets.length ? ctx.cmd.targets : null;
    if (!ids) return pool.filter((t) => t.hp > 0);
    const out = ids.map((id) => pool.find((t) => t.id === id));
    return out.some((t) => !t) ? null : out;
  };
  Eng.registerHook("sweep", {
    plan(ctx) {
      const w = sweepWeapon(ctx);
      if (!w) return `${ctx.power.name} needs a ${(params(ctx).props || ["heavy", "reach"]).map((k) => k[0].toUpperCase() + k.slice(1)).join(" or ")} melee weapon in hand`;
      const targets = sweepTargets(ctx, w);
      if (!targets) return "Pick enemies within your reach";
      if (!targets.length) return `No enemy within reach of ${w.name}`;
      const info = ctx.attackInfo(targets[0], { w, area: true, toDamage: ctx.cmd && ctx.cmd.toDamage });
      const dice = w.two && ctx.actor.hands.length < ctx.actor.build.slots.hand ? w.two : w.dice;
      const mod = ctx.actor.totals[info.abil];
      return { targets, info: { weapon: w.id, toHit: info.bonus, dice: info.dice, adv: info.adv, dis: info.dis, toDamage: info.toDamage, why: info.why.concat(info.parts), vs: "weapon",
        defense: targets.map((t) => `${t.name} ${ctx.attackInfo(t, { w, area: true }).def}`).join(", "),
        damage: `${dice}${mod ? (mod > 0 ? "+" : "−") + Math.abs(mod) : ""} ${w.type || "Physical"} (half on a miss)`, range: ctx.weaponReach(w) } };
    },
    onUse(ctx) {
      const w = sweepWeapon(ctx);
      ctx.areaWeaponAttack(w, ctx.targets, { attackAction: true, label: `sweeps with ${w.name}`, toDamage: ctx.cmd && ctx.cmd.toDamage });
    },
  });

  return { hooks: ["close_order", "brace", "pierce", "sweep"] };
});
