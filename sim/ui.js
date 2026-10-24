// Bearers combat sim: the page. It reads fight.state and sends commands through fight.do; every rule lives in the engine.
(function () {
  "use strict";
  const DEV = !!globalThis.BEARERS_DEV;
  const CARDS = globalThis.BEARERS_CARDS;
  const Eng = globalThis.BearersEngine;
  const params = new URLSearchParams(location.search);
  const LS = { setup: "bearers-sim:setup", fight: "bearers-sim:fight", presets: "bearers-sim:presets", prefs: "bearers-sim:prefs" };
  const ABIL = ["STR", "DEX", "INT", "WIL"];
  const ROWS = ["STR", "DEX", "INT", "WIL", "STRd", "DEXd", "INTd", "WILd", "HP", "SPD"];
  const TERRAIN = [["wall", "Wall", "#"], ["difficult", "Difficult", "~"], ["cover", "Cover", "+"], ["dark", "Dark", ":"]];
  const CONDS = ["Blinded", "Charmed", "Frightened", "Grappled", "Incapacitated", "Invisible", "Poisoned", "Prone", "Restrained", "Stunned", "Unconscious"];
  const SIZES = ["Tiny", "Small", "Medium", "Large", "Huge", "Gargantuan"];
  const SIDE = { pc: "Characters", foe: "Foes" };
  const SLOT_TYPES = {
    armor: ["Armor"], hand: ["Weapon", "Shield", "Instrument"], jewelry: ["Jewelry"],
    item: ["Consumable", "Recipe", "Purse", "Spellbook"], aspect: ["Trait", "Technique", "Knack", "Divine", "Glamour", "Nature"],
  };
  const USE_LABEL = { action: "Action", bonus: "Bonus", reaction: "Reaction", trigger: "Trigger", passive: "Passive", free: "Free" };

  const clone = (o) => (o == null ? o : JSON.parse(JSON.stringify(o)));
  const store = {
    get(k, d) { try { const v = localStorage.getItem(k); return v ? JSON.parse(v) : d; } catch (e) { return d; } },
    set(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch (e) { /* storage full or blocked */ } },
    del(k) { try { localStorage.removeItem(k); } catch (e) { /* blocked */ } },
  };

  // ---------- DOM ----------
  function h(sel, attrs, ...kids) {
    const [tag, ...cls] = sel.split(".");
    const el = document.createElement(tag || "div");
    if (cls.length) el.className = cls.join(" ");
    if (attrs != null && (typeof attrs !== "object" || attrs instanceof Node || Array.isArray(attrs))) { kids.unshift(attrs); attrs = null; }
    for (const [k, v] of Object.entries(attrs || {})) {
      if (v == null || v === false) continue;
      if (k.startsWith("on")) el.addEventListener(k.slice(2), v);
      else if (k === "class") el.className += (el.className ? " " : "") + v;
      else if (k === "style" && typeof v === "object") for (const [sk, sv] of Object.entries(v)) el.style.setProperty(sk.replace(/[A-Z]/g, (m) => "-" + m.toLowerCase()), sv);
      else if (k === "html") el.innerHTML = v;
      else if (k === "value") el.value = v;
      else if (k === "checked" || k === "disabled" || k === "selected") el[k] = !!v;
      else el.setAttribute(k, v === true ? "" : v);
    }
    const add = (k) => {
      if (k == null || k === false) return;
      if (Array.isArray(k)) k.forEach(add);
      else el.appendChild(k instanceof Node ? k : document.createTextNode(String(k)));
    };
    kids.forEach(add);
    return el;
  }
  const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]);
  const md = (s) => esc(s).replace(/\*\*(.+?)\*\*/g, "<b>$1</b>").replace(/\*(.+?)\*/g, "<i>$1</i>");
  const sign = (n) => (n > 0 ? "+" + n : n < 0 ? "−" + -n : "+0");
  function select(value, options, onchange, attrs) {
    // options: [[value, label]] or [{group, items: [[value, label]]}]
    const opt = ([v, l]) => h("option", { value: v, selected: String(v) === String(value) }, l);
    return h("select", Object.assign({ onchange: (e) => onchange(e.target.value) }, attrs || {}),
      options.map((o) => (o.group ? h("optgroup", { label: o.group }, o.items.map(opt)) : opt(o))));
  }
  function num(value, onchange, attrs) {
    return h("input", Object.assign({ type: "number", value, onchange: (e) => onchange(e.target.value === "" ? null : +e.target.value) }, attrs || {}));
  }
  function download(name, text, type) {
    const a = h("a", { href: URL.createObjectURL(new Blob([text], { type: type || "application/json" })), download: name });
    document.body.appendChild(a); a.click(); a.remove();
    setTimeout(() => URL.revokeObjectURL(a.href), 1000);
  }

  // ---------- cards ----------
  const card = (id) => (id && CARDS.cards[id]) || null;
  const cardName = (id) => (card(id) ? card(id).name : id === "unarmed" ? "Unarmed strike" : id === "improvised" ? "Improvised weapon" : id || "—");
  const foeByName = (n) => CARDS.foes.find((f) => f.name === n);
  const twoHanded = (id) => !!(card(id) && card(id).atk && card(id).atk.twoHanded);
  function slotOf(c) {
    for (const [slot, types] of Object.entries(SLOT_TYPES)) if (types.includes(c.type)) return slot;
    return null;
  }
  const RANKS = ["I", "II", "III", "IV", "V"];
  function pool(slot) {
    const list = Object.values(CARDS.cards).filter((c) => slotOf(c) === slot);
    list.sort((a, b) => (a.group === b.group ? 0 : a.group === "starter" ? -1 : 1) || RANKS.indexOf(a.rank) - RANKS.indexOf(b.rank) || a.name.localeCompare(b.name));
    const groups = [];
    for (const g of ["starter", "loot"]) {
      const items = list.filter((c) => c.group === g).map((c) => [c.id, `${c.name} (${c.rank})`]);
      if (items.length) groups.push({ group: g === "starter" ? "Starter" : "Loot", items });
    }
    return groups;
  }
  function findPower(id, build) {
    const src = String(id).split("#")[0];
    const c = card(src);
    if (c && c.fx) {
      const p = c.fx.find((x) => x.id === id);
      const n = p && build && build.recharge && build.recharge[id];
      if (n) { const q = Object.assign({}, p, { recharge: n }); delete q.uses; return q; }  // foe Recharge override (R701)
      if (p) return p;
    }
    const d = CARDS.decks[src];
    if (d) { const p = d.powers.find((x) => x.id === id); if (p) return p; }
    return ((build && build.ownFx) || []).find((x) => x.id === id) || null;
  }
  function sourceName(powerId) {
    const src = String(powerId).split("#")[0];
    if (card(src)) return card(src).name;
    if (src.startsWith("foe-")) return "Own powers";
    return src;
  }

  // ---------- builds and scenarios ----------
  function blankBuild() {
    return { core: "C-I-05", body: null, armor: null, hands: [], carried: [], jewelry: [], items: [], aspects: [],
      slots: { hand: 2, jewelry: 1, item: 2, aspect: 3 }, bonus: {}, extraDice: 0, recharge: {}, ownFx: [], powers: [], boss: false, senses: {}, alert: false, foe: null };
  }
  function normBuild(b) {
    const out = Object.assign(blankBuild(), clone(b || {}));
    out.slots = Object.assign({ hand: 2, jewelry: 1, item: 2, aspect: 3 }, out.slots || {});
    out.items = (out.items || []).map((i) => (typeof i === "string" ? { id: i, n: 1 } : i));
    return out;
  }
  function rowsToCells(rows) {
    const cells = {}, legend = { "#": "wall", "~": "difficult", "+": "cover", ":": "dark" };
    rows.forEach((r, y) => [...r].forEach((ch, x) => { if (legend[ch]) cells[x + "," + y] = legend[ch]; }));
    return cells;
  }
  function materialize(src) {
    const sc = clone(src);
    sc.version = 1;
    sc.name = sc.name || "Untitled fight";
    sc.seed = sc.seed == null ? 1 : sc.seed;
    sc.surprise = sc.surprise || null;
    sc.map = sc.map || { w: 16, h: 12, cells: {} };
    if (sc.map.rows) { sc.map.h = sc.map.h || sc.map.rows.length; sc.map.w = sc.map.w || sc.map.rows[0].length; sc.map.cells = rowsToCells(sc.map.rows); delete sc.map.rows; }
    sc.map.cells = sc.map.cells || {};
    sc.creatures = (sc.creatures || []).map((c) => {
      let build = c.build;
      if (!build && c.foe) {
        const foe = foeByName(c.foe);
        build = foe ? Eng.fromFoe(foe, CARDS) : blankBuild();
      }
      return { id: c.id, side: c.side || "pc", name: c.name || (c.foe || "Bearer"), build: normBuild(build), pos: c.pos || null, react: c.react || "ask" };
    });
    sc.creatures.forEach((c) => { if (!c.pos) c.pos = freeSpot(sc, c); });
    return sc;
  }
  function blankScenario() {
    return { version: 1, name: "New fight", seed: randomSeed(), surprise: null, map: { w: 16, h: 12, cells: {} }, creatures: [] };
  }
  const randomSeed = () => 1 + Math.floor(Math.random() * 99999);
  function spanOf(build) {
    const size = totalsOf(build).size || "Medium";
    return size === "Large" ? 2 : size === "Huge" ? 3 : size === "Gargantuan" ? 4 : 1;
  }
  function occupied(sc, except) {
    const occ = new Set();
    for (const c of sc.creatures) {
      if (c === except || !c.pos) continue;
      const n = spanOf(c.build);
      for (let dx = 0; dx < n; dx++) for (let dy = 0; dy < n; dy++) occ.add(c.pos[0] + dx + "," + (c.pos[1] + dy));
    }
    return occ;
  }
  function fits(sc, c, pos) {
    const n = spanOf(c.build), occ = occupied(sc, c);
    for (let dx = 0; dx < n; dx++) for (let dy = 0; dy < n; dy++) {
      const x = pos[0] + dx, y = pos[1] + dy, k = x + "," + y;
      if (x < 0 || y < 0 || x >= sc.map.w || y >= sc.map.h || occ.has(k) || sc.map.cells[k] === "wall") return false;
    }
    return true;
  }
  function freeSpot(sc, c) {
    const cols = [...Array(sc.map.w).keys()];
    if (c.side === "foe") cols.reverse();
    for (const x of cols) for (let y = 0; y < sc.map.h; y++) if (fits(sc, c, [x, y])) return [x, y];
    return [0, 0];
  }
  const totalsCache = new Map();
  function totalsOf(build) {
    const k = JSON.stringify(build);
    if (!totalsCache.has(k)) {
      let t, errs;
      try { t = Eng.totals(build, CARDS); } catch (e) { t = { errors: ["totals: " + e.message] }; }
      try { errs = Eng.validate(build, CARDS) || []; } catch (e) { errs = ["validate: " + e.message]; }
      totalsCache.set(k, { t, errs: [...new Set([...(t.errors || []), ...errs])] });
      if (totalsCache.size > 500) totalsCache.clear();
    }
    return totalsCache.get(k).t;
  }
  const errorsOf = (build) => (totalsOf(build), totalsCache.get(JSON.stringify(build)).errs);

  // ---------- app state ----------
  const A = {
    setup: null, view: "setup", sel: null, brush: "select", fight: null, sc: null, base: null,
    presets: store.get(LS.presets, {}), prefs: Object.assign({ manual: false }, store.get(LS.prefs, {})),
    logOpen: new Set(), toast: null, sawOver: false, foePick: CARDS && CARDS.foes[0] ? CARDS.foes[0].name : "", foeCount: 1,
  };
  const F = { sel: null, armed: null, path: [], preview: null, hoverArea: null };

  const DEMO = params.get("demo");
  function saveSetup() { if (!DEMO) store.set(LS.setup, A.setup); }
  function saveFight() { if (A.fight && !DEMO) store.set(LS.fight, A.fight.export()); }
  function toast(msg, bad) {
    A.toast = { msg, bad };
    render();
    clearTimeout(toast.t);
    toast.t = setTimeout(() => { A.toast = null; render(); }, 3500);
  }
  function nextId(side) {
    let n = 1;
    while (A.setup.creatures.some((c) => c.id === side + n)) n++;
    return side + n;
  }
  function uniqueName(base) {
    const names = new Set(A.setup.creatures.map((c) => c.name));
    if (!names.has(base)) return base;
    let n = 2;
    while (names.has(base + " " + n)) n++;
    return base + " " + n;
  }

  function numbered(base) {
    const names = new Set(A.setup.creatures.map((c) => c.name));
    let n = 1;
    while (names.has(base + " " + n)) n++;
    return base + " " + n;
  }

  // ---------- render ----------
  let rendering = false;
  function render() {
    if (rendering) return;
    rendering = true;
    const app = document.getElementById("app");
    const keep = {};
    app.querySelectorAll("[data-scroll]").forEach((el) => (keep[el.dataset.scroll] = el.scrollTop));
    const atBottom = (() => { const l = app.querySelector(".log-list"); return !l || l.scrollHeight - l.scrollTop - l.clientHeight < 40; })();
    app.textContent = "";
    app.appendChild(topbar());
    if (A.view === "setup") app.appendChild(setupView());
    else if (A.view === "fight") app.appendChild(fightView());
    else app.appendChild(summaryView());
    if (A.fight && A.fight.pending && A.view === "fight") app.appendChild(promptModal());
    app.querySelectorAll("[data-scroll]").forEach((el) => { if (keep[el.dataset.scroll] != null) el.scrollTop = keep[el.dataset.scroll]; });
    const log = app.querySelector(".log-list");
    if (log && atBottom) log.scrollTop = log.scrollHeight;
    rendering = false;
  }

  function topbar() {
    const tab = (v, label, dis) => h("button.tab", { class: A.view === v ? "on" : null, disabled: dis, onclick: () => { A.view = v; render(); } }, label);
    const fileIn = h("input", { type: "file", accept: ".json,application/json", style: { display: "none" }, onchange: (e) => importFile(e.target.files[0]) });
    const samples = globalThis.BEARERS_SCENARIOS || [];
    return h("header.topbar",
      h("div.brand", "Bearers", h("span", " Combat Sim"), DEV ? h("span.devtag", Eng && Eng.stub ? "dev · stub engine" : "dev") : null),
      h("nav.tabs", tab("setup", "Setup"), tab("fight", "Fight", !A.fight), tab("summary", "Summary", !A.fight)),
      A.toast ? h("div.toast", { class: A.toast.bad ? "bad" : null }, A.toast.msg) : h("div.spacer"),
      h("div.tools",
        select("", [["", "Load a sample…"], ...samples.map((s, i) => [i, s.name])], (v) => { if (v !== "") loadScenario(samples[+v]); }, { title: "Sample scenarios" }),
        h("button", { onclick: () => fileIn.click(), title: "Import a scenario or an exported fight (.json)" }, "Import"),
        h("button", { onclick: () => download(slug(A.setup.name) + ".json", JSON.stringify(A.setup, null, 1)), title: "Export this setup as a scenario file" }, "Export setup"),
        h("button", { onclick: () => { if (confirm("Start a blank setup?")) { A.setup = blankScenario(); A.sel = null; saveSetup(); render(); } } }, "New"),
        fileIn));
  }
  const slug = (s) => String(s || "fight").toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "") || "fight";

  function loadScenario(src) {
    try {
      A.setup = materialize(src);
      A.sel = A.setup.creatures[0] ? A.setup.creatures[0].id : null;
      A.view = "setup";
      saveSetup();
      toast(`Loaded “${A.setup.name}”.`);
    } catch (e) { toast("Could not load: " + e.message, true); }
  }
  function importFile(file) {
    if (!file) return;
    const r = new FileReader();
    r.onload = () => {
      let data;
      try { data = JSON.parse(r.result); } catch (e) { return toast("Not a JSON file.", true); }
      if (data.scenario && data.commands) {
        try { A.setup = materialize(data.scenario); saveSetup(); resumeFight(data); toast("Fight replayed from file."); }
        catch (e) { toast("Replay failed: " + e.message, true); }
      } else loadScenario(data);
    };
    r.readAsText(file);
  }

  // ---------- setup view ----------
  function setupView() {
    return h("main.setup", rosterPanel(), mapEditor(), builderPanel());
  }

  function rosterPanel() {
    const row = (c) => {
      const t = totalsOf(c.build), errs = errorsOf(c.build);
      const desc = c.build.foe ? c.build.foe : c.build.core ? cardName(c.build.core) : "raw body";
      return h("div.roster-row", {
        class: (A.sel === c.id ? "on " : "") + "side-" + c.side, draggable: "true",
        ondragstart: (e) => { e.dataTransfer.setData("text/plain", c.id); },
        onclick: () => { A.sel = c.id; render(); },
      },
        h("span.dot"),
        h("div.rr-main", h("div.rr-name", c.name, c.build.boss ? h("span.boss", "Boss") : null, errs.length ? h("span.warn", { title: errs.join("\n") }, "!") : null),
          h("div.rr-sub", `${desc} · ${t.HP} HP · ${t.size}`)),
        select(c.react, [["ask", "ask"], ["auto", "auto"], ["never", "never"]], (v) => { c.react = v; saveSetup(); render(); },
          { title: "Reactions: ask = prompt me, auto = engine decides, never = decline", onclick: (e) => e.stopPropagation() }),
        h("button.icon", { title: "Duplicate", onclick: (e) => { e.stopPropagation(); duplicate(c); } }, "⧉"),
        h("button.icon", { title: "Remove", onclick: (e) => { e.stopPropagation(); A.setup.creatures = A.setup.creatures.filter((x) => x !== c); if (A.sel === c.id) A.sel = null; saveSetup(); render(); } }, "✕"));
    };
    const side = (s) => A.setup.creatures.filter((c) => c.side === s);
    return h("aside.panel.roster", { "data-scroll": "roster" },
      h("div.panel-head", h("h2", "Characters"), h("button", { onclick: addCharacter }, "+ Character")),
      side("pc").map(row),
      side("pc").length ? null : h("p.hint", "No characters yet."),
      h("div.panel-head", h("h2", "Foes")),
      h("div.add-foe",
        select(A.foePick, CARDS.foes.map((f) => [f.name, f.name + (f.boss ? " (Boss)" : "")]), (v) => { A.foePick = v; }),
        h("span", "×"), num(A.foeCount, (v) => { A.foeCount = Math.max(1, Math.min(20, v || 1)); }, { min: 1, max: 20, class: "count" }),
        h("button", { onclick: addFoes }, "Add")),
      h("button.subtle", { onclick: addBlankFoe }, "+ Blank foe (raw body)"),
      side("foe").map(row),
      h("p.hint", "Drag a creature onto the map to place it. Large creatures fill 2×2 squares."),
      presetsBox());
  }
  function addCharacter() {
    const c = { id: nextId("pc"), side: "pc", name: uniqueName("Bearer"), build: blankBuild(), pos: null, react: "ask" };
    c.pos = freeSpot(A.setup, c);
    A.setup.creatures.push(c); A.sel = c.id; saveSetup(); render();
  }
  function addFoes() {
    const foe = foeByName(A.foePick);
    if (!foe) return;
    for (let i = 0; i < A.foeCount; i++) {
      const c = { id: nextId("foe"), side: "foe", name: "", build: normBuild(Eng.fromFoe(foe, CARDS)), pos: null, react: "auto" };
      c.name = A.foeCount > 1 || A.setup.creatures.some((x) => x.build.foe === foe.name) ? numbered(foe.name) : foe.name;
      c.pos = freeSpot(A.setup, c);
      A.setup.creatures.push(c);
      A.sel = c.id;
    }
    saveSetup(); render();
  }
  function addBlankFoe() {
    const b = blankBuild();
    b.core = null; b.body = { STR: 1, DEX: 1, INT: 0, WIL: 0, HP: 10, SPD: 30, size: "Medium" };
    const c = { id: nextId("foe"), side: "foe", name: uniqueName("Foe"), build: b, pos: null, react: "auto" };
    c.pos = freeSpot(A.setup, c);
    A.setup.creatures.push(c); A.sel = c.id; saveSetup(); render();
  }
  function duplicate(c) {
    const d = clone(c);
    d.id = nextId(c.side);
    d.name = numbered(c.name.replace(/ \d+$/, ""));
    d.pos = null; d.pos = freeSpot(A.setup, d);
    A.setup.creatures.push(d); A.sel = d.id; saveSetup(); render();
  }

  function presetsBox() {
    const sel = A.setup.creatures.find((c) => c.id === A.sel);
    const names = Object.keys(A.presets).sort();
    let pick = names[0] || "";
    return h("div.presets",
      h("div.panel-head", h("h2", "Presets")),
      sel ? h("button", { onclick: () => {
        const n = prompt("Preset name", sel.name);
        if (!n) return;
        A.presets[n] = { name: sel.name, side: sel.side, build: clone(sel.build) };
        store.set(LS.presets, A.presets); toast(`Saved preset “${n}”.`);
      } }, "Save selected as preset") : h("p.hint", "Select a creature to save it as a preset."),
      names.length ? h("div.row",
        select(pick, names.map((n) => [n, n]), (v) => (pick = v)),
        h("button", { title: "Add a creature from this preset", onclick: () => {
          const p = A.presets[pick]; if (!p) return;
          const c = { id: nextId(p.side), side: p.side, name: uniqueName(p.name), build: normBuild(p.build), pos: null, react: p.side === "pc" ? "ask" : "auto" };
          c.pos = freeSpot(A.setup, c); A.setup.creatures.push(c); A.sel = c.id; saveSetup(); render();
        } }, "Add"),
        h("button.icon", { title: "Delete preset", onclick: () => { delete A.presets[pick]; store.set(LS.presets, A.presets); render(); } }, "✕")) : null);
  }

  // ---------- map (shared by the editor and the fight) ----------
  function cellSize(w, avail) { return Math.max(22, Math.min(46, Math.floor(avail / w))); }
  function shortName(name, span) {
    const m = name.match(/^(.*?)\s+(\d+)$/);
    const base = m ? m[1] : name, n = m ? m[2] : "";
    const room = span > 1 ? 20 : 5 - n.length;
    return (base.length > room ? base.slice(0, room) : base) + n;
  }

  function mapGrid(map, cs, opt) {
    const grid = h("div.map", { style: { width: map.w * cs + "px", height: map.h * cs + "px", "--cs": cs + "px" } });
    for (let y = 0; y < map.h; y++) for (let x = 0; x < map.w; x++) {
      const k = x + "," + y;
      const cell = h("div.cell", { class: map.cells[k] || null, style: { left: x * cs + "px", top: y * cs + "px" }, "data-k": k });
      if (opt.decorate) opt.decorate(cell, k, x, y);
      grid.appendChild(cell);
    }
    return grid;
  }

  function mapEditor() {
    const sc = A.setup, cs = cellSize(sc.map.w, window.innerWidth - 300 - 460 - 70);
    let painting = false;
    const paint = (cell) => {
      const k = cell.dataset.k;
      if (A.brush === "clear") delete sc.map.cells[k]; else sc.map.cells[k] = A.brush;
      cell.className = "cell " + (sc.map.cells[k] || "");
    };
    const grid = mapGrid(sc.map, cs, {
      decorate: (cell, k, x, y) => {
        cell.addEventListener("mousedown", (e) => { if (A.brush !== "select") { e.preventDefault(); painting = true; paint(cell); } });
        cell.addEventListener("mouseenter", () => { if (painting) paint(cell); });
        cell.addEventListener("dragover", (e) => e.preventDefault());
        cell.addEventListener("drop", (e) => { e.preventDefault(); place(e.dataTransfer.getData("text/plain"), [x, y]); });
      },
    });
    grid.addEventListener("mouseup", () => { if (painting) { painting = false; saveSetup(); } });
    grid.addEventListener("mouseleave", () => { if (painting) { painting = false; saveSetup(); } });
    for (const c of sc.creatures) {
      if (!c.pos) continue;
      const span = spanOf(c.build), t = totalsOf(c.build);
      grid.appendChild(h("div.token", {
        class: `side-${c.side}${A.sel === c.id ? " selected" : ""}${c.build.boss ? " is-boss" : ""}${A.brush !== "select" ? " ghost" : ""}`,
        style: { left: c.pos[0] * cs + "px", top: c.pos[1] * cs + "px", width: span * cs + "px", height: span * cs + "px" },
        draggable: "true", title: `${c.name} · ${t.HP} HP`,
        ondragstart: (e) => e.dataTransfer.setData("text/plain", c.id),
        onclick: () => { A.sel = c.id; render(); },
      }, h("span.tk-name", shortName(c.name, span))));
    }
    const brush = (b, label, key) => h("button.brush", { class: (A.brush === b ? "on " : "") + "b-" + b, onclick: () => { A.brush = b; render(); }, title: key ? `Paint ${label.toLowerCase()} (scenario rows use “${key}”)` : null }, label);
    return h("section.mapcol",
      h("div.map-tools",
        h("label.field", "Name", h("input.wide", { value: sc.name, onchange: (e) => { sc.name = e.target.value; saveSetup(); render(); } })),
        h("label.field", "Grid", num(sc.map.w, (v) => resize(v, sc.map.h), { min: 4, max: 40, class: "count" }), "×", num(sc.map.h, (v) => resize(sc.map.w, v), { min: 4, max: 40, class: "count" })),
        h("label.field", "Surprised", select(sc.surprise || "", [["", "nobody"], ["pc", "characters"], ["foe", "foes"]], (v) => { sc.surprise = v || null; saveSetup(); })),
        h("label.field", "Seed", num(sc.seed, (v) => { sc.seed = v || 1; saveSetup(); }, { class: "seed" }),
          h("button.icon", { title: "New random seed", onclick: () => { sc.seed = randomSeed(); saveSetup(); render(); } }, "⚄"))),
      h("div.map-tools",
        h("span.label", "Paint"), brush("select", "Move tokens"), TERRAIN.map(([k, l, ch]) => brush(k, l, ch)), brush("clear", "Clear"),
        h("button.subtle", { onclick: () => { if (confirm("Clear all terrain?")) { sc.map.cells = {}; saveSetup(); render(); } } }, "Clear map")),
      h("div.map-wrap", { "data-scroll": "map" }, grid),
      h("div.start-row",
        h("button.primary", { onclick: startFight, disabled: !sc.creatures.some((c) => c.side === "pc") || !sc.creatures.some((c) => c.side === "foe") }, "Start fight"),
        h("label.check", h("input", { type: "checkbox", checked: A.prefs.manual, onchange: (e) => { A.prefs.manual = e.target.checked; store.set(LS.prefs, A.prefs); } }), "Manual dice"),
        store.get(LS.fight, null) ? h("button", { onclick: () => { const exp = store.get(LS.fight, null); if (exp) resumeFight(exp); } }, "Resume last fight") : null,
        warnings()));
  }
  function warnings() {
    const bad = A.setup.creatures.filter((c) => errorsOf(c.build).length);
    return bad.length ? h("span.warnline", `${bad.length} build${bad.length > 1 ? "s" : ""} with errors: ${bad.map((c) => c.name).join(", ")}`) : null;
  }
  function resize(w, hh) {
    const sc = A.setup;
    sc.map.w = Math.max(4, Math.min(40, w || sc.map.w)); sc.map.h = Math.max(4, Math.min(40, hh || sc.map.h));
    for (const k of Object.keys(sc.map.cells)) { const [x, y] = k.split(",").map(Number); if (x >= sc.map.w || y >= sc.map.h) delete sc.map.cells[k]; }
    for (const c of sc.creatures) if (c.pos && !fits(sc, c, c.pos)) c.pos = freeSpot(sc, c);
    saveSetup(); render();
  }
  function place(id, pos) {
    const c = A.setup.creatures.find((x) => x.id === id);
    if (!c) return;
    if (!fits(A.setup, c, pos)) return toast("That space is blocked.", true);
    c.pos = pos; A.sel = c.id; saveSetup(); render();
  }

  // ---------- builder ----------
  function builderPanel() {
    const c = A.setup.creatures.find((x) => x.id === A.sel);
    if (!c) return h("aside.panel.builder", h("h2", "Builder"), h("p.hint", "Select a creature in the roster or on the map to build it."));
    const b = c.build, t = totalsOf(b), errs = errorsOf(b);
    const set = (fn) => { fn(); saveSetup(); render(); };
    const foe = b.foe ? foeByName(b.foe) : null;

    const frame = (label, slot, value, onchange, extra) => {
      const cd = card(value);
      return h("div.frame", { class: "f-" + slot + (value === "__2h" ? " covered" : "") },
        h("div.frame-band", label),
        value === "__2h" ? h("div.frame-empty", "Held by a Two-Handed weapon") :
          [select(value || "", [["", "— empty —"], ...pool(slot)], onchange), extra || null,
            cd ? h("div.frame-text", { html: (cd.text || []).map(md).join("<br>") + (cd.req ? `<div class="req">Req ${Object.entries(cd.req).map(([k, n]) => k + " +" + n).join(", ")}</div>` : "") }) : null]);
    };
    // Hands: each card takes one frame, a Two-Handed weapon two.
    const handFrames = [];
    for (const id of b.hands) { handFrames.push(id); if (twoHanded(id)) handFrames.push("__2h"); }
    while (handFrames.length < b.slots.hand) handFrames.push(null);
    const setHand = (i, v) => set(() => {
      const fr = handFrames.slice(0, Math.max(b.slots.hand, handFrames.length));
      fr[i] = v || null;
      if (v && twoHanded(v) && i + 1 < fr.length) fr[i + 1] = null;
      b.hands = fr.filter((x) => x && x !== "__2h");
    });
    const listFrames = (key, slot, label) => {
      const arr = b[key], out = [];
      for (let i = 0; i < Math.max(b.slots[slot], arr.length); i++) {
        const isItem = key === "items", v = isItem ? (arr[i] && arr[i].id) : arr[i];
        const stack = isItem && v && card(v) && card(v).type === "Consumable"
          ? h("label.stack", "×", num(arr[i].n || 1, (n) => set(() => (arr[i].n = Math.max(1, Math.min(3, n || 1)))), { min: 1, max: 3, class: "count" })) : null;
        out.push(frame(`${label} ${i + 1}${i >= b.slots[slot] ? " (over)" : ""}`, slot, v, (nv) => set(() => {
          if (!nv) arr.splice(i, 1);
          else arr[i] = isItem ? { id: nv, n: 1 } : nv;
          b[key] = arr.filter(Boolean);
        }), stack));
      }
      return out;
    };
    const deckPowers = [];
    for (const id of [...b.aspects, ...b.items.map((i) => i.id)]) {
      const cd = card(id), d = cd && cd.deck && CARDS.decks[cd.deck];
      if (d) deckPowers.push({ cover: cd, deck: d });
    }
    const sizes = SIZES.map((s) => [s, s]);
    return h("aside.panel.builder", { "data-scroll": "builder" },
      h("div.panel-head", h("input.name", { value: c.name, onchange: (e) => set(() => (c.name = e.target.value || c.name)) }),
        select(c.side, [["pc", "Character"], ["foe", "Foe"]], (v) => set(() => (c.side = v)))),
      foe ? h("div.foe-note", h("div", h("b", "Foe card: "), foe.name, " ", h("button.subtle", { onclick: () => set(() => (c.build = normBuild(Eng.fromFoe(foe, CARDS)))) }, "Reset to card")),
        foe.own.map((s) => h("div.own", { html: md(s) }))) : null,
      h("div.row",
        h("label.field", b.body ? "Body" : "Core",
          select(b.core || "__body", [{ group: "Cores", items: Object.values(CARDS.cards).filter((x) => x.kind === "core").map((x) => [x.id, `${x.name} (${x.rank}${x.size !== "Medium" ? ", " + x.size : ""})`]) },
            ["__body", "Raw body (foe)"]], (v) => set(() => {
            if (v === "__body") { b.core = null; b.body = b.body || { STR: 0, DEX: 0, INT: 0, WIL: 0, HP: 10, SPD: 30, size: "Medium" }; }
            else { b.core = v; b.body = null; }
          })))),
      b.body ? h("div.body-grid",
        ["STR", "DEX", "INT", "WIL", "HP", "SPD"].map((k) => h("label.field", k, num(b.body[k] || 0, (v) => set(() => (b.body[k] = v || 0)), { class: "count" }))),
        h("label.field", "Size", select(b.body.size || "Medium", sizes, (v) => set(() => (b.body.size = v))))) : null,
      h("div.frames",
        frame("Armor", "armor", b.armor, (v) => set(() => (b.armor = v || null))),
        handFrames.map((v, i) => frame(`Hand ${i + 1}${i >= b.slots.hand ? " (over)" : ""}`, "hand", v, (nv) => setHand(i, nv))),
        listFrames("jewelry", "jewelry", "Jewelry"),
        listFrames("items", "item", "Item"),
        listFrames("aspects", "aspect", "Aspect")),
      h("div.subhead", "Carried (swap into a Hand with the free interaction)"),
      h("div.chips",
        b.carried.map((id, i) => h("span.chip", cardName(id), h("button.icon", { onclick: () => set(() => b.carried.splice(i, 1)) }, "✕"))),
        select("", [["", "+ weapon…"], ...pool("hand")], (v) => { if (v) set(() => b.carried.push(v)); })),
      h("div.subhead", "Slots"),
      h("div.row.slots",
        [["hand", "Hands"], ["jewelry", "Jewelry"], ["item", "Items"], ["aspect", "Aspects"]].map(([k, l]) =>
          h("label.field", l, num(b.slots[k], (v) => set(() => (b.slots[k] = Math.max(0, Math.min(k === "aspect" ? 12 : 4, v || 0)))), { class: "count", min: 0 })))),
      h("div.hint", "Extra Gear Slots: Third Hand, Second Jewel, Great Backpack add one each."),
      h("div.subhead", "Foe tweaks"),
      h("div.row.slots",
        h("label.field", "Bonus HP", num(b.bonus.HP || 0, (v) => set(() => { if (v) b.bonus.HP = v; else delete b.bonus.HP; }), { class: "count" })),
        h("label.field", "Extra dice", num(typeof b.extraDice === "number" ? b.extraDice : 0, (v) => set(() => (b.extraDice = Math.max(0, v || 0))), { class: "count", min: 0 })),
        b.extraDice && typeof b.extraDice === "object" ? h("span.hint", "Per weapon: " + Object.entries(b.extraDice).map(([id, n]) => `${cardName(id)} +${n}`).join(", ") + " (a number here applies to every weapon)") : null,
        h("label.check", h("input", { type: "checkbox", checked: b.boss, onchange: (e) => set(() => (b.boss = e.target.checked)) }), "Boss"),
        h("label.check", h("input", { type: "checkbox", checked: b.alert, onchange: (e) => set(() => (b.alert = e.target.checked)) }), "Alert"),
        h("label.field", "Darkvision", num((b.senses || {}).darkvision || 0, (v) => set(() => { b.senses = b.senses || {}; if (v) b.senses.darkvision = v; else delete b.senses.darkvision; }), { class: "count", min: 0, step: 30 }))),
      (c.side === "foe" ? deckPowers : []).map(({ cover, deck }) => h("div.deck-pick",
        h("div.subhead", `${cover.name}: powers used`, h("span.hint", b.powers.length ? "" : " (all)")),
        h("div.chips", deck.powers.map((p) => h("label.check.small",
          h("input", { type: "checkbox", checked: !b.powers.length || b.powers.includes(p.name), onchange: (e) => set(() => {
            let list = b.powers.length ? b.powers.slice() : deck.powers.map((x) => x.name);
            list = e.target.checked ? [...new Set([...list, p.name])] : list.filter((n) => n !== p.name);
            b.powers = list.length === deck.powers.length ? [] : list;
          }) }), `${p.name}${p.cost ? " (" + p.cost + ")" : ""}`))))),
      b.ownFx && b.ownFx.length ? h("div", h("div.subhead", "Own powers"), h("div.chips", b.ownFx.map((p) => h("span.chip", p.name)))) : null,
      tally(t),
      errs.length ? h("ul.errors", errs.map((e) => h("li", e))) : h("p.ok", "Build is legal."));
  }
  function tally(t) {
    const cellv = (k) => (k === "HP" || k === "SPD" || k.endsWith("d") ? t[k] : sign(t[k] || 0));
    return h("div.tally",
      h("div.subhead", "Totals (tally card)"),
      h("table",
        h("tr", ABIL.map((k) => h("th", k)), h("th", "HP"), h("th", "Speed"), h("th", "Size")),
        h("tr", ABIL.map((k) => h("td", cellv(k))), h("td", t.HP), h("td", t.SPD + " ft"), h("td", t.size)),
        h("tr", ABIL.map((k) => h("th.def", k + " Def"))),
        h("tr", ABIL.map((k) => h("td.def", t[k + "d"])))));
  }

  // ---------- fight ----------
  function startFight() {
    const sc = clone(A.setup);
    let f;
    try { f = Eng.createFight(sc, CARDS); } catch (e) { return toast("Engine refused the scenario: " + e.message, true); }
    A.fight = f; A.sc = sc; A.base = clone(f.state); A.sawOver = false; A.logOpen.clear();
    if (f.setManualDice) f.setManualDice(A.prefs.manual);
    resetFightUI();
    A.view = "fight";
    send({ type: "start" });
  }
  function resumeFight(exp) {
    let f;
    try { f = Eng.replay(exp, CARDS); } catch (e) { return toast("Replay failed: " + e.message, true); }
    A.fight = f; A.sc = clone(exp.scenario);
    try { A.base = clone(Eng.createFight(clone(exp.scenario), CARDS).state); } catch (e) { A.base = clone(f.state); }
    A.sawOver = f.state.phase === "over";
    if (f.setManualDice) f.setManualDice(A.prefs.manual);
    resetFightUI(); A.view = "fight"; render();
  }
  function resetFightUI() { F.armed = null; F.path = []; F.preview = null; F.hoverArea = null; }
  const S = () => A.fight.state;
  const cr = (id) => S().creatures[id];
  const buildOf = (id) => { const c = A.sc && A.sc.creatures.find((x) => x.id === id); return c ? c.build : null; };

  function send(cmd) {
    const f = A.fight;
    let r;
    try { r = f.do(cmd); } catch (e) { console.error(e); r = { ok: false, error: "Engine error: " + e.message }; }
    if (!r || !r.ok) { toast((r && r.error) || "Not allowed.", true); return false; }
    resetFightUI();
    afterChange();
    return true;
  }
  function afterChange() {
    saveFight();
    const st = S();
    if (st.phase === "over" && !A.sawOver && !A.fight.pending) { A.sawOver = true; A.view = "summary"; }
    if (st.phase !== "over") A.sawOver = false;
    if (st.active) F.sel = st.active;
    render();
  }
  function undo() {
    if (!A.fight) return;
    let ok;
    try { ok = A.fight.undo(); } catch (e) { return toast("Undo failed: " + e.message, true); }
    if (ok === false) return toast("Nothing to undo.");
    resetFightUI();
    if (A.view === "summary") A.view = "fight";
    afterChange();
  }

  function fightView() {
    if (!A.fight) return h("main.empty", h("p", "No fight yet. Build one in Setup."));
    return h("main.fight", h("section.fcol", fightMap(), creatureCard()), h("aside.panel.actions", { "data-scroll": "actions" }, turnPanel()), logPanel());
  }

  // What a command template still needs from the map.
  function needOf(tpl) {
    if (tpl.need) return Array.isArray(tpl.need) ? tpl.need[0] : tpl.need;
    switch (tpl.type) {
      case "move": return "path";
      case "attack": case "shove": case "grapple": case "escape": return tpl.target ? null : "target";
      case "act": return tpl.action === "help" ? "target" : null;
      case "note": return "text";
      case "power": {
        const p = findPower(tpl.power, buildOf(tpl.actor));
        if (!p) return null;
        if (p.target === "point") return "point";
        if (p.target === "creature" || p.target === "ally" || p.target === "enemy") return "target";
        if (p.target === "darts") return "darts";
        if ((p.target === "allies" || p.target === "enemies") && p.count) return "targets";
        return null;
      }
      default: return null;
    }
  }
  function assemble() {
    const a = F.armed, cmd = Object.assign({}, a.tpl);
    delete cmd.label; delete cmd.need;
    if (a.need === "target") { if (cmd.type === "power") cmd.targets = a.targets.slice(0, 1); else cmd.target = a.targets[0]; }
    if (a.need === "targets" || a.need === "darts") cmd.targets = a.targets.slice();
    if (a.need === "point") cmd.point = a.point;
    if (a.level != null) cmd.level = a.level;
    if (a.need === "text") cmd.text = a.text || "";
    return cmd;
  }
  function previewCmd(cmd) {
    try { return A.fight.preview(cmd) || { ok: false, error: "No preview" }; } catch (e) { return { ok: false, error: "Preview error: " + e.message }; }
  }
  function arm(tpl) {
    const need = needOf(tpl);
    if (!need) {
      // Self or instant: preview powers first; everything else goes straight to the engine.
      if (tpl.type === "power") { F.armed = { tpl, need: null, targets: [], point: null, level: defaultLevel(tpl) }; refreshPreview(); render(); return; }
      const cmd = Object.assign({}, tpl); delete cmd.label;
      send(cmd); return;
    }
    F.path = [];
    F.armed = { tpl, need, targets: [], point: null, text: "", level: defaultLevel(tpl) };
    F.preview = null;
    render();
  }
  function defaultLevel(tpl) {
    if (tpl.type !== "power") return null;
    const p = findPower(tpl.power, buildOf(tpl.actor));
    return p && p.kind === "Spell" && p.cost ? p.cost : null;
  }
  function refreshPreview() {
    if (!F.armed) return;
    const a = F.armed;
    const ready = !a.need || (a.need === "point" ? !!a.point : a.need === "text" ? true : a.targets.length > 0);
    F.preview = ready ? previewCmd(assemble()) : null;
  }
  function confirmArmed() {
    if (!F.armed) { if (F.path.length) confirmMove(); return; }
    send(assemble());
  }
  function confirmMove() {
    if (!F.path.length || !S().active) return;
    send({ type: "move", actor: S().active, path: F.path.slice() });
  }

  // Shortest path on the grid for planning (geometry only: the engine prices and validates it).
  function planPath(from, to, actor) {
    const st = S(), map = st.map, c = cr(actor), n = c.size === "Large" ? 2 : c.size === "Huge" ? 3 : 1;
    const blocked = (x, y) => {
      for (let dx = 0; dx < n; dx++) for (let dy = 0; dy < n; dy++) {
        const X = x + dx, Y = y + dy;
        if (X < 0 || Y < 0 || X >= map.w || Y >= map.h || map.cells[X + "," + Y] === "wall") return true;
        for (const o of Object.values(st.creatures)) if (o.id !== actor && !o.dead && o.side !== c.side && occupies(o, X, Y)) return true;
      }
      return false;
    };
    const key = (p) => p[0] + "," + p[1], prev = new Map([[key(from), null]]), q = [from];
    while (q.length) {
      const p = q.shift();
      if (p[0] === to[0] && p[1] === to[1]) break;
      for (const [dx, dy] of STEPS) {
        const np = [p[0] + dx, p[1] + dy];
        if ( !prev.has(key(np)) && !blocked(np[0], np[1])) { prev.set(key(np), p); q.push(np); }
      }
    }
    if (!prev.has(key(to))) return null;
    const out = [];
    for (let p = to; p && key(p) !== key(from); p = prev.get(key(p))) out.unshift(p);
    return out;
  }
  const STEPS = [[1, 0], [-1, 0], [0, 1], [0, -1], [1, 1], [1, -1], [-1, 1], [-1, -1]];
  function occupies(o, x, y) {
    const n = o.size === "Large" ? 2 : o.size === "Huge" ? 3 : o.size === "Gargantuan" ? 4 : 1;
    return x >= o.pos[0] && x < o.pos[0] + n && y >= o.pos[1] && y < o.pos[1] + n;
  }
  function creatureAt(x, y) {
    return Object.values(S().creatures).find((o) => !o.dead && occupies(o, x, y)) || Object.values(S().creatures).find((o) => !o.fled && occupies(o, x, y));
  }
  function localArea(p, pt) {
    const out = [], n = Math.max(1, Math.round(p.area.size / 5));
    if (p.area.shape === "sphere") { for (let x = -n; x < n; x++) for (let y = -n; y < n; y++) out.push(pt[0] + x + 1 + "," + (pt[1] + y + 1)); }
    else { const o = Math.floor((n - 1) / 2); for (let x = 0; x < n; x++) for (let y = 0; y < n; y++) out.push(pt[0] - o + x + "," + (pt[1] - o + y)); }
    return out;
  }

  function onCell(x, y) {
    const st = S();
    if (A.fight.pending) return;
    const a = F.armed;
    if (a && a.need === "point") { a.point = [x, y]; refreshPreview(); render(); return; }
    const o = creatureAt(x, y);
    if (o) return onToken(o.id);
    if (!st.active || (a && a.need !== "path")) return;
    const c = cr(st.active);
    const last = F.path.length ? F.path[F.path.length - 1] : c.pos;
    if (F.path.length && last[0] === x && last[1] === y) return confirmMove();
    const seg = planPath(last, [x, y], c.id);
    if (!seg) return toast("No path there.", true);
    F.path = F.path.concat(seg);
    F.armed = null;
    F.preview = previewCmd({ type: "move", actor: c.id, path: F.path });
    render();
  }
  function onToken(id) {
    const st = S(), a = F.armed;
    if (a && (a.need === "target" || a.need === "targets" || a.need === "darts")) {
      if (a.need === "target") {
        if (a.targets[0] === id && F.preview && F.preview.ok) return confirmArmed();
        a.targets = [id];
      } else if (a.need === "darts") a.targets.push(id);
      else a.targets = a.targets.includes(id) ? a.targets.filter((t) => t !== id) : a.targets.concat(id);
      refreshPreview(); render(); return;
    }
    const o = cr(id);
    if (st.active && !a && o.side !== cr(st.active).side && !o.dead) {
      const atk = A.fight.legal(st.active).find((t) => t.type === "attack" && !t.thrown);
      if (atk) { F.sel = id; arm(atk); F.armed.targets = [id]; refreshPreview(); render(); return; }
    }
    F.sel = id; render();
  }

  function fightMap() {
    const st = S(), map = st.map, cs = cellSize(map.w, window.innerWidth - 400 - 340 - 60);
    const pathSet = new Map(F.path.map((p, i) => [p[0] + "," + p[1], i + 1]));
    const a = F.armed;
    let area = null;
    if (a && a.need === "point") {
      const info = F.preview && F.preview.info;
      area = new Set((info && Array.isArray(info.cells) && info.cells) || (F.hoverArea || []));
    } else if (F.armed && F.preview && F.preview.info && Array.isArray(F.preview.info.cells)) area = new Set(F.preview.info.cells);
    const zoneCells = new Map();
    for (const z of st.zones || []) for (const k of z.cells || []) zoneCells.set(k, z);
    const pw = a && a.tpl.type === "power" ? findPower(a.tpl.power, buildOf(a.tpl.actor)) : null;
    const grid = mapGrid(map, cs, {
      decorate: (cell, k, x, y) => {
        if (zoneCells.has(k)) { cell.classList.add("zone"); cell.title = sourceName(zoneCells.get(k).power) + " · " + (findPower(zoneCells.get(k).power) || {}).name; }
        if (pathSet.has(k)) { cell.classList.add("path"); cell.appendChild(h("span.step", pathSet.get(k))); }
        if (area && area.has(k)) cell.classList.add("area");
        if (a && a.point && a.point[0] === x && a.point[1] === y) cell.classList.add("point");
        cell.addEventListener("click", () => onCell(x, y));
        if (pw && pw.area && !a.point) cell.addEventListener("mouseenter", () => { F.hoverArea = localArea(pw, [x, y]); grid.querySelectorAll(".cell.area").forEach((e) => e.classList.remove("area")); F.hoverArea.forEach((kk) => { const e = grid.querySelector(`[data-k="${kk}"]`); if (e) e.classList.add("area"); }); });
      },
    });
    grid.addEventListener("contextmenu", (e) => { e.preventDefault(); resetFightUI(); render(); });
    // which tokens the armed command can target
    let valid = null;
    if (a && (a.need === "target" || a.need === "targets" || a.need === "darts")) {
      valid = new Set();
      for (const o of Object.values(st.creatures)) {
        if (o.dead) continue;
        const test = Object.assign({}, a.tpl); delete test.label; delete test.need;
        if (test.type === "power") test.targets = [o.id]; else test.target = o.id;
        if (a.level != null) test.level = a.level;
        if (previewCmd(test).ok) valid.add(o.id);
      }
    }
    for (const o of Object.values(st.creatures)) {
      if (o.fled) continue; // a fled foe has left the map
      const n = o.size === "Large" ? 2 : o.size === "Huge" ? 3 : o.size === "Gargantuan" ? 4 : 1;
      const hp = o.form ? o.form.hp : o.hp, max = o.form ? o.form.maxHp : o.maxHp;
      const pct = max ? Math.max(0, Math.min(100, (100 * hp) / max)) : 0;
      const tk = h("div.token", {
        class: [`side-${o.side}`, st.active === o.id ? "active" : "", F.sel === o.id ? "selected" : "", o.dead ? "dead" : o.down ? "down" : "",
          (st.done || []).includes(o.id) ? "done" : "", valid ? (valid.has(o.id) ? "targetable" : "untargetable") : "",
          a && a.targets.includes(o.id) ? "targeted" : "", buildOf(o.id) && buildOf(o.id).boss ? "is-boss" : ""].filter(Boolean).join(" "),
        style: { left: o.pos[0] * cs + "px", top: o.pos[1] * cs + "px", width: n * cs + "px", height: n * cs + "px" },
        title: `${o.name} · ${hp}/${max} HP${o.temp ? " +" + o.temp + " temp" : ""}${o.conds.length ? " · " + o.conds.map((x) => x.name).join(", ") : ""}`,
        onclick: (e) => { e.stopPropagation(); onToken(o.id); },
        ondblclick: (e) => { e.stopPropagation(); const bt = A.fight.legal(o.id).find((t) => t.type === "beginTurn" && !t.half); if (bt) send(bt); },
      },
        h("span.tk-name", shortName(o.name, n)),
        o.form ? h("span.tk-form", formName(o)) : null,
        a && a.need === "darts" && a.targets.filter((t) => t === o.id).length ? h("span.tk-darts", "×" + a.targets.filter((t) => t === o.id).length) : null,
        h("span.tk-hp", h("span", { style: { width: pct + "%" }, class: pct <= 25 ? "low" : pct <= 50 ? "mid" : null })),
        o.conds.length ? h("span.tk-conds", o.conds.map((x) => h("b", { title: x.name }, x.name.slice(0, 2)))) : null);
      grid.appendChild(tk);
    }
    return h("div.map-wrap.fight-map", { "data-scroll": "fmap" }, grid);
  }
  function formName(o) {
    const p = findPower(o.form.power, buildOf(o.id));
    return p ? p.name : "Form";
  }

  function turnPanel() {
    const st = S(), f = A.fight;
    const sideName = st.side === "pc" ? "Characters'" : "Foes'";
    const init = lastEvent("initiative");
    const out = [
      h("div.turnhead", { class: "side-" + st.side },
        st.phase === "setup" ? h("b", "Before the fight") : st.phase === "over" ? h("b", "Fight over: " + (st.winner ? SIDE[st.winner] + " win" : "no winner")) :
          [h("b", `Round ${st.round}`), h("span", ` · ${sideName} side`)],
        h("div.headtools",
          h("button", { onclick: undo, title: "Undo the last command (Ctrl+Z)" }, "↶ Undo"),
          h("label.check.small", h("input", { type: "checkbox", checked: A.prefs.manual, onchange: (e) => { A.prefs.manual = e.target.checked; store.set(LS.prefs, A.prefs); if (f.setManualDice) f.setManualDice(A.prefs.manual); } }), "Manual dice"),
          h("button", { onclick: () => { A.view = "summary"; render(); } }, "Summary"))),
      init ? h("div.init", init.text) : null,
    ];
    if (st.phase === "setup") out.push(h("button.primary", { onclick: () => send({ type: "start" }) }, st.surprise ? `Start: ambush (${st.surprise === "pc" ? "the Bearers are" : "the foes are"} surprised)` : "Roll initiative"));
    if (st.phase === "over") out.push(h("p.hint", "Undo to step back into the fight, or see the summary."));

    // Who acts
    if (st.phase === "fight") {
      const list = Object.values(st.creatures).filter((o) => o.side === st.side || (buildOf(o.id) && buildOf(o.id).boss));
      out.push(h("div.subhead", st.active ? "Acting" : "Choose who acts next"),
        h("div.who", list.map((o) => {
          const bt = st.active ? [] : f.legal(o.id).filter((t) => t.type === "beginTurn");
          const status = o.fled ? "fled" : o.dead ? "dead" : o.down ? "down" : st.active === o.id ? "acting" : (st.done || []).includes(o.id) ? "done" : o.side === st.side ? "ready" : "";
          return h("div.who-row", { class: (F.sel === o.id ? "on " : "") + "side-" + o.side + " st-" + status, onclick: () => { F.sel = o.id; render(); } },
            h("span.dot"), h("span.who-name", o.name), hpText(o), h("span.status", status),
            bt.map((t) => h("button", { class: t.half ? "half" : "go", onclick: (e) => { e.stopPropagation(); send(t); } }, t.label || (t.half ? "Half turn" : "Begin"))));
        })));
    }
    if (st.active) out.push(actionPanel(st.active));
    return out;
  }
  function hpText(o) {
    const hp = o.form ? o.form.hp : o.hp, max = o.form ? o.form.maxHp : o.maxHp;
    return h("span.hp", `${hp}/${max}${o.temp ? " +" + o.temp : ""}`);
  }
  function lastEvent(t) { const ev = A.fight.events; for (let i = ev.length - 1; i >= 0; i--) if (ev[i].t === t) return ev[i]; return null; }

  function actionPanel(id) {
    const f = A.fight, c = cr(id), t = c.turn || {};
    let legal = [];
    try { legal = f.legal(id) || []; } catch (e) { return h("p.errors", "legal() failed: " + e.message); }
    const btn = (tpl, label, sub) => h("button.act", {
      class: F.armed && F.armed.tpl === tpl ? "on" : null,
      onclick: () => (F.armed && F.armed.tpl === tpl ? (resetFightUI(), render()) : arm(tpl)),
    }, label || tpl.label || tpl.type, sub ? h("small", sub) : null);
    const by = (type) => legal.filter((x) => x.type === type);
    const pill = (label, used) => h("span.pill", { class: used ? "used" : null }, label);
    const left = (t.speed || 0) - (t.moved || 0);
    const groups = new Map();
    for (const p of by("power")) {
      const src = String(p.power).split("#")[0];
      if (!groups.has(src)) groups.set(src, []);
      groups.get(src).push(p);
    }
    const otherIdx = legal.findIndex((x) => x.type === "note");
    return h("div.action-panel",
      h("div.ap-head", h("b", `${c.name}`), t.half ? h("span.boss", "Half turn") : null, t.firstMover ? h("span.pill", "First mover: move or action") : null),
      h("div.pills", pill(`Move ${left}/${t.speed || 0} ft`, left <= 0), pill("Action", t.action), pill("Bonus", t.bonus), pill("Reaction", t.reaction), pill("Interaction", t.interact),
        t.disengaged ? pill("Disengaged") : null, t.dodging ? pill("Dodging") : null),
      armedBox(),
      by("move").length && !F.armed ? h("p.hint", "Click squares to plan a path; click the last square again (or Move) to go. Right-click clears.") : null,
      by("move").some((m) => m.stand) ? h("div.btns", by("move").filter((m) => m.stand).map((m) => h("button.act", { onclick: () => send(Object.assign({}, m, { label: undefined, path: m.path || [] })) }, m.label || "Stand up"))) : null,
      by("attack").length ? [h("div.subhead", "Attacks"), h("div.btns", by("attack").map((a) => btn(a, a.label || cardName(a.weapon) + (a.thrown ? " (thrown)" : "") + (a.offhand ? " (off-hand)" : ""), weaponSub(c, a))))] : null,
      (by("act").length || by("shove").length || by("grapple").length || by("escape").length) ? [h("div.subhead", "Actions"),
        h("div.btns", by("act").map((a) => btn(a, a.label || cap(a.action))), by("shove").map((a) => btn(a, a.label || "Shove" + (a.mode ? " (" + a.mode + ")" : ""))),
          by("grapple").map((a) => btn(a, a.label || "Grapple")), by("escape").map((a) => btn(a, a.label || "Escape")))] : null,
      [...groups].map(([src, list]) => h("div.power-group",
        h("div.subhead", sourceName(src), resourceText(c, src)),
        h("div.btns", list.map((p) => { const pw = findPower(p.power, buildOf(id)) || {}; return btn(p, p.label || pw.name, powerSub(c, pw)); })))),
      by("interact").length ? [h("div.subhead", "Free interaction"), h("div.btns", by("interact").map((a) => btn(a, a.label || interactLabel(a))))] : null,
      passiveList(id),
      h("div.subhead", "Other"),
      otherIdx >= 0 ? h("div.row.note",
        h("input.wide", { placeholder: "Describe another action (Ready, Hide, First Aid…)", id: "note-text", onkeydown: (e) => { if (e.key === "Enter") sendNote(legal[otherIdx]); } }),
        h("button", { onclick: () => sendNote(legal[otherIdx]) }, "Log it")) : null,
      by("endTurn").map((e) => h("button.endturn", { onclick: () => send(strip(e)) }, e.label || (t.half ? "End half turn" : "End turn"))));
  }
  const cap = (s) => (s ? s[0].toUpperCase() + s.slice(1) : s);
  const strip = (tpl) => { const c = Object.assign({}, tpl); delete c.label; delete c.need; return c; };
  function sendNote(tpl) {
    const el = document.getElementById("note-text");
    const text = el && el.value.trim();
    if (!text) return toast("Write what the creature does first.", true);
    send(Object.assign(strip(tpl), { text }));
  }
  function interactLabel(a) {
    if (a.draw && a.stow) return `Draw ${cardName(a.draw)}, stow ${cardName(a.stow)}`;
    if (a.draw) return `Draw ${cardName(a.draw)}`;
    if (a.stow) return `Stow ${cardName(a.stow)}`;
    return "Interact";
  }
  function weaponSub(c, a) {
    const cd = card(a.weapon);
    if (!cd || !cd.atk) return null;
    const k = cd.atk;
    const r = a.thrown && k.thrown ? `${k.thrown[0]}/${k.thrown[1]} ft` : k.range ? `${k.range[0]}/${k.range[1]} ft` : k.reach ? "reach 10 ft" : "melee";
    return `${sign(k.hit)} · ${k.dice}${k.two ? "/" + k.two : ""} · ${r}`;
  }
  function powerSub(c, pw) {
    const bits = [];
    if (pw.use) bits.push(USE_LABEL[pw.use] || pw.use);
    if (pw.cost) bits.push(`${pw.cost} ${pw.kind === "Spell" ? "SP" : "Resolve"}`);
    if (pw.uses && c.uses && c.uses[pw.id] != null) bits.push(`${c.uses[pw.id]} left`);
    if (pw.recharge) bits.push(`Recharge ${pw.recharge}–6`);
    if (pw.reach) bits.push(`${pw.reach} ft`);
    return bits.join(" · ");
  }
  function resourceText(c, src) {
    const base = A.base && A.base.creatures[c.id];
    const parts = [];
    if (c.sp && c.sp[src] != null) parts.push(`spell points ${c.sp[src]}/${base && base.sp ? base.sp[src] : "?"}`);
    if (c.resolve && c.resolve[src] != null) parts.push(`Resolve ${c.resolve[src]}/${base && base.resolve ? base.resolve[src] : "?"}`);
    return parts.length ? h("span.res", parts.join(" · ")) : null;
  }
  function passiveList(id) {
    const b = buildOf(id);
    if (!b) return null;
    const c = cr(id), list = [];
    const add = (p) => { if (p && ["reaction", "trigger", "passive"].includes(p.use)) list.push(p); };
    for (const cid of [b.armor, ...b.hands, ...b.jewelry, ...b.items.map((i) => i.id), ...b.aspects]) {
      const cd = card(cid);
      if (!cd) continue;
      (cd.fx || []).forEach(add);
      const d = cd.deck && CARDS.decks[cd.deck];
      if (d) d.powers.filter((p) => !b.powers.length || b.powers.includes(p.name)).forEach(add);
    }
    (b.ownFx || []).forEach(add);
    if (!list.length) return null;
    return h("details.passives", h("summary", `Reactions, triggers & passives (${list.length})`),
      h("ul", list.map((p) => h("li", h("b", p.name), " ", h("small", powerSub(c, p) + (p.on ? " · on " + p.on : ""))))));
  }

  function armedBox() {
    const a = F.armed;
    if (!a && !F.path.length) return null;
    const pv = F.preview;
    let title, hint = null, extra = null;
    if (a) {
      const pw = a.tpl.type === "power" ? findPower(a.tpl.power, buildOf(a.tpl.actor)) : null;
      title = a.tpl.label || (pw && pw.name) || cardName(a.tpl.weapon) || a.tpl.type;
      hint = { target: "Click a target.", targets: `Click targets${pw && pw.count ? " (up to " + pw.count + ")" : ""}; click again to remove.`,
        darts: `Click a target once per dart${pw && pw.count ? " (" + pw.count + " darts)" : ""}.`, point: "Click a square to aim the area.", text: null }[a.need] || null;
      if (pw && pw.kind === "Spell" && pw.cost) {
        const deck = CARDS.decks[String(pw.id).split("#")[0]];
        const max = (deck && deck.maxLevel) || pw.cost;
        if (max > pw.cost) extra = h("label.field", "Level", select(a.level, Array.from({ length: max - pw.cost + 1 }, (_, i) => [pw.cost + i, pw.cost + i]), (v) => { a.level = +v; refreshPreview(); render(); }));
      }
      if (a.targets.length) extra = [extra, h("div.targets", "Targets: ", a.targets.map((t) => cr(t).name).join(", "))];
    } else title = `Move (${F.path.length} square${F.path.length > 1 ? "s" : ""})`;
    return h("div.armed",
      h("div.armed-head", h("b", title), h("button.icon", { title: "Cancel (Esc)", onclick: () => { resetFightUI(); render(); } }, "✕")),
      hint ? h("div.hint", hint) : null, extra,
      pv ? previewBlock(pv) : null,
      h("div.btns",
        h("button.primary", { disabled: !(pv && pv.ok), onclick: confirmArmed }, a ? "Confirm" : "Move"),
        h("button", { onclick: () => { resetFightUI(); render(); } }, "Cancel")));
  }
  const INFO_LABEL = { toHit: "To hit", defense: "Defense", dice: "Dice", cost: "Cost", left: "Left after", provokes: "Provokes", outnumbered: "Outnumbered",
    cover: "Cover", distance: "Distance", damage: "Damage", why: "Why", vs: "Against", targets: "Targets", weapon: "Weapon", abil: "Ability", power: "Power", use: "Use", adv: "Advantage dice", dis: "Disadvantage dice", range: "Range", keep: "Keep" };
  function previewBlock(pv) {
    if (!pv.ok) return h("div.preview.bad", pv.error || "Not possible.", pv.info ? infoTable(pv.info) : null);
    return h("div.preview", infoTable(pv.info || {}));
  }
  function infoTable(info) {
    if (typeof info === "string") return h("div", info);
    const rows = [];
    if (info.text) rows.push(h("tr", h("td", { colspan: 2 }, info.text)));
    for (const [k, v] of Object.entries(info)) {
      if (k === "text" || k === "cells" || v == null || v === "" || (Array.isArray(v) && !v.length)) continue;
      let val = v;
      if (k === "outnumbered" && typeof v === "object") val = `${v.us} vs ${v.them}` + (v.n != null ? ` (${sign(v.n)})` : "");
      else if (k === "toHit") val = sign(v);
      else if (k === "cost" || k === "left" || k === "distance" || k === "range") val = typeof v === "number" ? v + " ft" : v;
      else if (k === "cover") val = v ? sign(v) + " Defense" : "none";
      else if (Array.isArray(v)) val = v.map((x) => (typeof x === "object" ? JSON.stringify(x) : (cr(x) ? cr(x).name : x))).join(", ");
      else if (typeof v === "object") val = Object.entries(v).map(([a, b]) => `${a} ${typeof b === "object" ? JSON.stringify(b) : b}`).join(" · ");
      else if (typeof v === "boolean") val = v ? "yes" : "no";
      rows.push(h("tr", { class: k === "provokes" ? "warn" : null }, h("th", INFO_LABEL[k] || k), h("td", String(val))));
    }
    return h("table.info", rows);
  }

  function creatureCard() {
    const id = F.sel || S().active;
    const c = id && cr(id);
    if (!c) return h("div.ccard.empty", h("p.hint", "Click a creature to see it. Double-click one on the acting side to begin its turn."));
    const t = (c.form && c.form.totals) || c.totals || {};
    const hp = c.form ? c.form.hp : c.hp, max = c.form ? c.form.maxHp : c.maxHp;
    let hpIn = hp, condPick = CONDS[0];
    return h("div.ccard", { class: "side-" + c.side },
      h("div.cc-head", h("b", c.name), h("span.tag", SIDE[c.side].slice(0, -1)), buildOf(id) && buildOf(id).boss ? h("span.boss", "Boss") : null,
        c.form ? h("span.tag", "Form: " + formName(c)) : null, c.fled ? h("span.tag", "fled") : c.dead ? h("span.tag.bad", "dead") : c.down ? h("span.tag.bad", c.stable ? "stable" : "down") : null),
      h("div.cc-grid",
        h("div", h("div.big", `${hp}/${max}`), h("small", "HP" + (c.temp ? ` · +${c.temp} temp` : "")), c.down && !c.dead ? h("small", ` · saves ${c.death.ok}✓ ${c.death.fail}✗`) : null),
        h("div", h("div.big", `${t.SPD != null ? t.SPD : "?"} ft`), h("small", "Speed · " + (c.size || ""))),
        h("table.mini", h("tr", ABIL.map((k) => h("th", k))), h("tr", ABIL.map((k) => h("td", sign(t[k] || 0)))), h("tr", ABIL.map((k) => h("td.def", t[k + "d"] != null ? t[k + "d"] : "–"))))),
      h("div.cc-line", h("small", "Hands: "), (c.hands || []).map(cardName).join(", ") || "empty", (c.carried || []).length ? h("small", " · carried: " + c.carried.map(cardName).join(", ")) : null),
      (c.items || []).length ? h("div.cc-line", h("small", "Items: "), c.items.map((i) => cardName(i.id) + (i.n > 1 ? " ×" + i.n : "")).join(", ")) : null,
      h("div.conds", c.conds.map((x) => h("span.cond", { class: x.lasting ? "lasting" : null, title: [x.source && cr(x.source) ? "from " + cr(x.source).name : "", x.until || "", x.lasting ? "lasting" : "", x.subdue ? "subdue" : ""].filter(Boolean).join(" · ") },
        x.name, h("button.icon", { title: "Remove (adjust)", onclick: () => send({ type: "adjust", actor: id, cond: x.name, remove: true }) }, "✕"))),
        (c.mods || []).map((m) => h("span.mod", { title: m.power ? findPowerName(m.power) : "" }, `${m.kind} ${m.n ? sign(m.n) : ""}${m.dice || ""}${m.next ? " (next)" : ""}`))),
      Object.keys(c.uses || {}).length ? h("div.cc-line", h("small", "Uses: "), Object.entries(c.uses).map(([p, n]) => `${findPowerName(p)} ${n}`).join(" · ")) : null,
      h("div.adjust", h("small", "Adjust: "),
        h("input.count", { type: "number", value: hp, onchange: (e) => (hpIn = +e.target.value) }),
        h("button", { onclick: () => send({ type: "adjust", actor: id, hp: hpIn }) }, "Set HP"),
        select(condPick, CONDS.map((x) => [x, x]), (v) => (condPick = v)),
        h("button", { onclick: () => send({ type: "adjust", actor: id, cond: condPick }) }, "Add condition")));
  }
  function findPowerName(id) { const p = findPower(id, null) || Object.values(A.sc.creatures).map((c) => findPower(id, c.build)).find(Boolean); return p ? p.name : id; }

  function logPanel() {
    const ev = A.fight.events || [];
    return h("aside.panel.log",
      h("div.panel-head", h("h2", "Log"), h("small", `${ev.length} events`)),
      h("div.log-list", { "data-scroll": "log" }, ev.map((e, i) => {
        const details = eventDetails(e);
        const open = A.logOpen.has(i);
        return h("div.ev", { class: "ev-" + e.t + (details ? " has-details" : "") + (open ? " open" : ""), onclick: details ? () => { open ? A.logOpen.delete(i) : A.logOpen.add(i); render(); } : null },
          e.t === "round" ? h("div.ev-round", e.text) : [details ? h("span.caret", open ? "▾" : "▸") : null, h("span.ev-text", e.text || `(${e.t})`)],
          open && details ? h("div.ev-details", details) : null);
      })));
  }
  const SKIP = new Set(["t", "round", "actor", "target", "text"]);
  function eventDetails(e) {
    if (e.t === "roll") {
      const bits = [];
      if (e.dice) bits.push(`d20s [${e.dice.join(", ")}] → kept ${e.kept}`);
      if (e.bonus != null) bits.push(`bonus ${sign(e.bonus)}`);
      if (e.total != null) bits.push(`total ${e.total}${e.vs != null ? " vs " + e.vs : ""}`);
      if (e.adv || e.dis) bits.push(`advantage ${e.adv || 0} · disadvantage ${e.dis || 0}`);
      const why = (e.why || []).map((w) => (typeof w === "string" ? w : JSON.stringify(w)));
      return h("div", bits.join(" · "), why.length ? h("ul", why.map((w) => h("li", w))) : null);
    }
    const rest = Object.entries(e).filter(([k]) => !SKIP.has(k));
    if (!rest.length) return null;
    return h("div", rest.map(([k, v]) => h("div", h("small", k + ": "), typeof v === "object" ? JSON.stringify(v) : String(v))));
  }

  function promptModal() {
    const p = A.fight.pending;
    let roll = "";
    const answer = (choice, r) => {
      const cmd = { type: "answer", choice };
      if (r != null) cmd.roll = r;
      send(cmd);
    };
    const die = p.die || (String(p.text).match(/d(\d+)/) || [])[1] || 20;
    return h("div.modal-bg",
      h("div.modal",
        h("div.modal-kind", p.kind === "reaction" ? "Reaction" : p.kind === "roll" ? "Roll" : "Choice"),
        h("p", p.text),
        p.kind === "roll" ? h("div.row",
          h("input.count", { type: "number", min: 1, max: die, id: "roll-in", onchange: (e) => (roll = e.target.value), onkeydown: (e) => { if (e.key === "Enter") answer(null, +e.target.value); } }),
          h("button.primary", { onclick: () => { const v = +(document.getElementById("roll-in").value || roll); if (v) answer(null, v); } }, "Enter roll"),
          h("button", { onclick: () => answer(null, 1 + Math.floor(Math.random() * die)) }, `Roll d${die} for me`)) :
          h("div.options",
            (p.options || []).map((o, i) => h("button.option", { onclick: () => answer(i) }, o.label || `${o.actor ? cr(o.actor).name + ": " : ""}${o.power || "option " + (i + 1)}`)),
            p.kind === "reaction" ? h("button.option.decline", { onclick: () => answer(null) }, "Decline") : null)));
  }

  // ---------- summary ----------
  const SUM_COLS = [["name", "Creature"], ["side", "Side"], ["dmgDealt", "Dmg dealt"], ["dmgTaken", "Dmg taken"], ["healed", "Healed"], ["attacks", "Attacks"], ["hits", "Hits"],
    ["crits", "Crits"], ["kills", "Kills"], ["downs", "Downs"], ["roundsAlive", "Rounds alive"], ["spent.sp", "Spell points"], ["spent.resolve", "Resolve"], ["spent.uses", "Uses"],
    ["spent.consumables", "Consumables"], ["endHp", "End HP"], ["fled", "Fled"]];
  const pick = (o, path) => path.split(".").reduce((x, k) => (x == null ? x : x[k]), o);
  function summaryView() {
    if (!A.fight) return h("main.empty", h("p", "No fight yet."));
    let s;
    try { s = A.fight.summary(); } catch (e) { return h("main.empty", h("p.errors", "summary() failed: " + e.message)); }
    const rows = Object.entries(s.creatures || {});
    const tot = (side, k) => rows.filter(([, c]) => c.side === side).reduce((n, [, c]) => n + (+pick(c, k) || 0), 0);
    return h("main.summary",
      h("div.sum-head",
        h("h2", s.winner ? `${SIDE[s.winner]} win` : A.fight.state.phase === "over" ? "No one stands" : "Fight in progress"),
        h("span", `${s.rounds} round${s.rounds === 1 ? "" : "s"} · seed ${s.seed}`),
        h("div.btns",
          h("button", { onclick: () => download(slug(A.sc.name) + "-fight.json", JSON.stringify(A.fight.export(), null, 1)) }, "Export fight (JSON)"),
          h("button", { onclick: () => download(slug(A.sc.name) + "-summary.csv", toCSV(s), "text/csv") }, "Export CSV"),
          h("button", { onclick: () => { A.view = "fight"; render(); } }, "Back to the fight"),
          h("button", { onclick: () => { startFight(); } }, "Rematch (same seed)"),
          h("button", { onclick: () => { A.setup.seed = randomSeed(); saveSetup(); startFight(); } }, "Rematch (new seed)"))),
      h("table.sum",
        h("tr", SUM_COLS.map(([, l]) => h("th", l)), h("th", "Hit %")),
        rows.map(([, c]) => h("tr", { class: "side-" + c.side }, SUM_COLS.map(([k]) => h("td", k === "side" ? SIDE[c.side] : k === "fled" ? (c.fled ? "fled" : "") : pick(c, k) == null ? "–" : pick(c, k))),
          h("td", c.attacks ? Math.round((100 * c.hits) / c.attacks) + "%" : "–"))),
        ["pc", "foe"].map((side) => h("tr.total", h("td", "Total"), h("td", SIDE[side]), SUM_COLS.slice(2).map(([k]) => h("td", k === "endHp" ? tot(side, k) : tot(side, k))), h("td", ""))))) ;
  }
  function toCSV(s) {
    const q = (v) => (/[",\n]/.test(String(v)) ? '"' + String(v).replace(/"/g, '""') + '"' : v);
    const lines = [["id", ...SUM_COLS.map(([k]) => k)].join(",")];
    for (const [id, c] of Object.entries(s.creatures || {})) lines.push([id, ...SUM_COLS.map(([k]) => (pick(c, k) == null ? "" : pick(c, k)))].map(q).join(","));
    return lines.join("\n") + "\n";
  }

  // ---------- keys ----------
  document.addEventListener("keydown", (e) => {
    if (e.target && /INPUT|SELECT|TEXTAREA/.test(e.target.tagName)) return;
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "z" && A.fight && A.view !== "setup") { e.preventDefault(); undo(); }
    else if (e.key === "Escape" && A.fight && !A.fight.pending) { resetFightUI(); render(); }
    else if (e.key === "Enter" && A.view === "fight" && A.fight && !A.fight.pending && ((F.preview && F.preview.ok) || F.path.length)) confirmArmed();
  });
  let resizeT;
  window.addEventListener("resize", () => { clearTimeout(resizeT); resizeT = setTimeout(render, 150); });

  // ---------- demo hooks (?dev&demo=name) for screenshots ----------
  function demo(name) {
    const samples = globalThis.BEARERS_SCENARIOS || [];
    const load = (i) => { A.setup = materialize(samples[i]); A.sel = A.setup.creatures[0].id; };
    const toPcSide = () => {
      let guard = 0;
      while (S().side !== "pc" && guard++ < 20) {
        const nxt = Object.values(S().creatures).find((o) => o.side === S().side && !(S().done || []).includes(o.id) && !o.dead);
        if (!nxt) break;
        send({ type: "beginTurn", actor: nxt.id }); send({ type: "endTurn", actor: nxt.id });
      }
    };
    if (name === "builder" || name === "selftest") { load(0); A.sel = "pc3"; }
    else if (name === "map") { load(1); A.sel = "foe1"; A.brush = "dark"; }
    else if (name === "fight" || name === "attack" || name === "area" || name === "summary" || name === "fled") {
      load(name === "area" ? 0 : 0);
      A.prefs.manual = false; startFight(); toPcSide();
      if (name === "fight") { send({ type: "beginTurn", actor: "pc1" }); F.sel = "pc1"; onCell(4, 5); onCell(6, 4); }
      if (name === "attack") { send({ type: "beginTurn", actor: "pc2" }); const t = A.fight.legal("pc2").find((x) => x.type === "attack" && x.weapon === "W-I-09"); arm(t); onToken("foe1"); }
      if (name === "area") {
        send({ type: "beginTurn", actor: "pc3" });
        const t = A.fight.legal("pc3").find((x) => x.type === "power" && /grease|web/.test(x.power));
        if (t) { arm(t); onCell(10, 5); }
      }
      if (name === "summary" || name === "fled") { // four foes fall: Morale (P 6.11) may make others flee
        for (const id of ["foe2", "foe3", "foe4", "foe5"]) send({ type: "adjust", actor: id, hp: 0 });
        send({ type: "adjust", actor: "foe1", hp: 1 });
        for (const pc of ["pc2", "pc3", "pc4", "pc1"]) {
          if (S().phase !== "fight") break;
          send({ type: "beginTurn", actor: pc });
          const t = A.fight.legal(pc).find((x) => x.type === "attack" && x.weapon !== "unarmed") || A.fight.legal(pc).find((x) => x.type === "power" && /fire-bolt|bane/.test(x.power));
          if (t) send(Object.assign(strip(t), t.type === "power" ? { targets: ["foe1"] } : { target: "foe1" }));
          if (S().phase === "fight") send({ type: "endTurn", actor: pc });
        }
        A.view = name === "fled" ? "fight" : "summary";
      }
    } else if (name === "manual") { load(0); A.prefs.manual = true; startFight(); }
    else if (name === "boss") { load(2); A.prefs.manual = false; startFight(); toPcSide(); F.sel = "foe1"; }
    else if (name === "prompt") {
      const sc = clone(samples[0]);
      sc.creatures.find((c) => c.id === "foe1").pos = [3, 5];
      A.setup = materialize(sc); A.prefs.manual = false; startFight();
      if (S().side === "pc") { for (const id of ["pc1", "pc2", "pc3", "pc4"]) { send({ type: "beginTurn", actor: id }); send({ type: "endTurn", actor: id }); } }
      send({ type: "beginTurn", actor: "foe1" });
      send({ type: "move", actor: "foe1", path: [[4, 5], [5, 5]] });
    }
    render();
  }

  // ---------- boot ----------
  function boot() {
    const app = document.getElementById("app");
    if (!CARDS || !Eng) {
      app.innerHTML = "";
      app.appendChild(h("div.boot-error", h("h1", "Bearers Combat Sim"),
        h("p", "Missing: " + [!CARDS ? "cards.js" : null, !Eng ? "engine.js" : null].filter(Boolean).join(", ") + "."),
        h("p", "Generate cards.js with tools/export_sim.py, or open ", h("a", { href: "index.html?dev" }, "index.html?dev"), " to use the stub engine.")));
      return;
    }
    const saved = store.get(LS.setup, null);
    try { A.setup = saved ? materialize(saved) : (globalThis.BEARERS_SCENARIOS || [])[0] ? materialize(globalThis.BEARERS_SCENARIOS[0]) : blankScenario(); }
    catch (e) { A.setup = blankScenario(); }
    A.sel = A.setup.creatures[0] ? A.setup.creatures[0].id : null;
    if (params.get("demo")) { try { demo(params.get("demo")); } catch (e) { console.error(e); toast("Demo failed: " + e.message, true); } }
    render();
    if ((globalThis.BEARERS_MISSING || []).length && !DEV) toast("Missing: " + globalThis.BEARERS_MISSING.join(", "), true);
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot); else boot();
})();
