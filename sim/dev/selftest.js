// DEV: clicks through the page like a user (index.html?dev&demo=selftest) and prints what passed.
(function () {
  const results = [], errors = [];
  window.addEventListener("error", (e) => errors.push(e.message));
  const $ = (s) => document.querySelector(s);
  const $$ = (s) => [...document.querySelectorAll(s)];
  const click = (el) => el && el.dispatchEvent(new MouseEvent("click", { bubbles: true }));
  const change = (el, v) => { if (!el) return; el.value = v; el.dispatchEvent(new Event("change", { bubbles: true })); };
  const check = (name, ok) => results.push([name, !!ok]);
  const byText = (sel, re) => $$(sel).find((e) => re.test(e.textContent));
  const logText = () => $$(".ev").map((e) => e.textContent).join("\n");

  function run() {
    // Setup: select, edit, paint, add foes
    click(byText(".roster-row", /Isolde/));
    check("select creature in roster", $(".builder input.name") && $(".builder input.name").value === "Isolde");
    change($(".builder .row select"), "C-I-01");
    check("change Core updates the tally", /\+3/.test($(".tally td").textContent));
    const hand2 = $$(".frame").find((f) => /Hand 2/.test(f.textContent));
    change(hand2 && hand2.querySelector("select"), "W-I-01");
    check("fill Hand 2 with a Dagger", /Dagger/.test($$(".frame")[2].querySelector("select").selectedOptions[0].textContent));
    click(byText("button.brush", /^Wall$/));
    const cell = $('.map .cell[data-k="0,0"]');
    cell.dispatchEvent(new MouseEvent("mousedown", { bubbles: true }));
    $(".map").dispatchEvent(new MouseEvent("mouseup", { bubbles: true }));
    check("paint a wall", $('.map .cell[data-k="0,0"]').classList.contains("wall"));
    click(byText("button.brush", /Move tokens/));
    const before = $$(".roster-row").length;
    change($(".add-foe select"), "Wolf");
    change($(".add-foe input"), "2");
    click(byText(".add-foe button", /Add/));
    check("add 2 Wolves", $$(".roster-row").length === before + 2 && /Wolf 2/.test($(".roster").textContent));
    // Fight
    click(byText("button", /Start fight/));
    check("start fight", !!$(".turnhead") && /Initiative/.test(logText()));
    click($(".who-row button.go"));
    check("begin a turn", !!$(".action-panel"));
    const tok = $(".token.active");
    const cs = parseFloat(getComputedStyle($(".fight-map .cell")).width);
    let x = Math.round(parseFloat(tok.style.left) / cs), y = Math.round(parseFloat(tok.style.top) / cs);
    const target = [[x, y + 1], [x, y - 1], [x - 1, y], [x + 1, y]].find(([a, b]) => { const c = $(`.fight-map .cell[data-k="${a},${b}"]`); return c && !c.classList.contains("wall"); });
    click($(`.fight-map .cell[data-k="${target[0]},${target[1]}"]`));
    check("plan a path (preview shows cost)", /Cost/.test(($(".armed") || {}).textContent || ""));
    click($(`.fight-map .cell[data-k="${target[0]},${target[1]}"]`));
    check("move by clicking the last square again", /moves/.test(logText()));
    const n = $$(".ev").length;
    click(byText("button", /^↶ Undo$/));
    check("undo button", $$(".ev").length < n);
    click($(".ev.has-details"));
    check("expand roll details", !!$(".ev.open .ev-details"));
    change($(".adjust input"), "3");
    click(byText(".adjust button", /Set HP/));
    check("adjust HP", /Adjust/.test(logText()));
    document.dispatchEvent(new KeyboardEvent("keydown", { key: "z", ctrlKey: true, bubbles: true }));
    check("Ctrl+Z undoes the adjust", !/Adjust/.test(logText()));
    click(byText("button", /^End turn$/));
    check("end turn", /ends its turn/.test(logText()));
    click(byText(".tab", /Summary/));
    check("summary table", !!$("table.sum"));
    click(byText("button", /Back to the fight/));
    check("back to the fight", !!$(".fight"));
    check("no script errors", !errors.length);
    const box = document.createElement("div");
    box.style.cssText = "position:fixed;right:10px;bottom:10px;z-index:99;background:#fff;border:2px solid #333;padding:8px;font:13px monospace;max-width:520px";
    box.innerHTML = results.map(([k, ok]) => `<div style="color:${ok ? "green" : "red"}">${ok ? "PASS" : "FAIL"} ${k}</div>`).join("") + errors.map((e) => `<div style="color:red">${e}</div>`).join("");
    document.body.appendChild(box);
    document.title = results.every((r) => r[1]) ? "SELFTEST PASS" : "SELFTEST FAIL";
  }
  setTimeout(() => { try { run(); } catch (e) { errors.push(e.stack); check("selftest crashed: " + e.message, false); run.done = 1; const b = document.createElement("pre"); b.textContent = errors.join("\n") + "\n" + JSON.stringify(results); b.style.cssText = "position:fixed;right:0;bottom:0;background:#fff;z-index:99"; document.body.appendChild(b); } }, 50);
})();
