/*
 * Bearers card effects (sim/SPEC.md section 5): the named special cases (`hook` in a power).
 * Loads after engine.js, in a page (globalThis.BearersEngine) or under Node (require).
 *
 *   close_order  Gladius    passive: +params.dmg damage while an ally is engaged with the same creature
 *   brace        Boarspear  rider on its opportunity attacks: +params.dmg damage
 *   pierce       Pilum      rider on a hit: the target's Shield gives no bonus until it pulls the pilum free
 *                           (a "Pierced" condition; the engine offers the action to end it)
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

  return { hooks: ["close_order", "brace", "pierce"] };
});
