"""Simulate the Shatter economy and compare Slot growth with fifth-edition levelling.

Usage: .venv/bin/python tools/shatter_sim.py [--keep 0.2] [--rest-every 3] [--runs 2000]

Model (one character):
- Each encounter drops randint(1, 3) Aspects for this character.
- Drop Rank depends on the character's effective level (Slots - 4), see RANK_TABLE.
- The player keeps a fraction `keep` of drops (equip/Stash) and treats the rest as Shatter fuel.
- A long rest happens every `rest_every` encounters; at most ONE Slot opens per long rest.
- Shattering uses the smallest Aspects first, so little value is wasted.

Benchmark: encounters a 5e character needs to reach each level, fighting
moderate encounters (SRD 5.2.1 XP budget per character, standard XP-to-level thresholds).
Effective level = Slots - 4, so 5 Slots = level 1 and 15 Slots = level 11-12.
"""
import argparse
import random
import statistics

# 5e XP thresholds for levels 1..12 and moderate XP budget per character per encounter
XP_FOR_LEVEL = [0, 300, 900, 2700, 6500, 14000, 23000, 34000, 48000, 64000, 85000, 100000]
MODERATE_XP = [75, 150, 225, 375, 750, 1000, 1300, 1700, 2000, 2300, 2900, 3700]

# Probability of each Rank (I, II, III, IV) for a drop, by effective level band
RANK_TABLE = [
    (2, (0.95, 0.05, 0.00, 0.00)),
    (4, (0.80, 0.20, 0.00, 0.00)),
    (6, (0.60, 0.35, 0.05, 0.00)),
    (8, (0.45, 0.40, 0.15, 0.00)),
    (10, (0.35, 0.40, 0.22, 0.03)),
    (99, (0.25, 0.40, 0.28, 0.07)),
]

CURVES = {
    "current (106)": [2, 3, 4, 6, 8, 10, 13, 16, 20, 24],
    "flat (50)": [2, 2, 3, 3, 4, 5, 6, 7, 8, 10],
}


def benchmark():
    """Cumulative encounters for a 5e character to reach levels 2..12."""
    out, total = [], 0.0
    for lvl in range(1, 12):
        total += (XP_FOR_LEVEL[lvl] - XP_FOR_LEVEL[lvl - 1]) / MODERATE_XP[lvl - 1]
        out.append(total)
    return out  # index i -> encounters to reach level i + 2


def roll_rank(level, rng):
    for max_level, probs in RANK_TABLE:
        if level <= max_level:
            return rng.choices((1, 2, 3, 4), weights=probs)[0]


def simulate(costs, keep, rest_every, rng, max_encounters=400):
    """Return the encounter number at which each new Slot (6th..15th) opened."""
    slots, fuel, reached = 5, [], []
    for enc in range(1, max_encounters + 1):
        level = slots - 4
        for _ in range(rng.randint(1, 3)):
            rank = roll_rank(level, rng)
            if rng.random() >= keep:
                fuel.append(rank)
        if enc % rest_every == 0 and slots < 15:
            cost = costs[slots - 5]
            if sum(fuel) >= cost:
                fuel.sort()
                paid = 0
                while paid < cost:
                    paid += fuel.pop(0)
                slots += 1
                reached.append(enc)
        if slots == 15:
            break
    return reached


def slot_level(slot):
    """Equivalent 5e level of a Slot count: Slots - 4, with 15 Slots stretched to level 12."""
    return 12 if slot >= 15 else slot - 4


def target_encounters(slot, bench):
    return 0.0 if slot <= 5 else bench[slot_level(slot) - 2]


def fit_curve(keep, rest_every, rng, runs):
    """Cost per Slot = average fuel earned while a 5e character spends that level's encounters."""
    bench = benchmark()
    costs = []
    for slot in range(6, 16):
        lo, hi = target_encounters(slot - 1, bench), target_encounters(slot, bench)
        level = slot_level(slot - 1)
        samples = []
        for _ in range(runs):
            fuel = 0
            for _ in range(round(hi - lo)):
                for _ in range(rng.randint(1, 3)):
                    rank = roll_rank(level, rng)
                    if rng.random() >= keep:
                        fuel += rank
            samples.append(fuel)
        costs.append(max(1, round(statistics.mean(samples))))
    return costs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--keep", type=float, default=0.2, help="fraction of drops kept, not shattered")
    ap.add_argument("--rest-every", type=int, default=3, help="encounters per long rest")
    ap.add_argument("--runs", type=int, default=2000)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--curve", help="extra cost curve to test: 10 comma-separated costs for Slots 6..15")
    args = ap.parse_args()
    rng = random.Random(args.seed)

    bench = benchmark()
    curves = dict(CURVES)
    if args.curve:
        curves["custom"] = [int(x) for x in args.curve.split(",")]
    curves["fitted to 5e"] = fit_curve(args.keep, args.rest_every, rng, max(200, args.runs // 10))

    print(f"keep={args.keep}  long rest every {args.rest_every} encounters  runs={args.runs}\n")
    header = "Slot  Lvl  5e enc |" + "".join(f" {name:>15}" for name in curves)
    print(header)
    print("-" * len(header))
    results = {}
    for name, costs in curves.items():
        runs = [simulate(costs, args.keep, args.rest_every, rng) for _ in range(args.runs)]
        results[name] = [
            statistics.median(r[i] for r in runs if len(r) > i) if any(len(r) > i for r in runs) else None
            for i in range(10)
        ]
    for i in range(10):
        slot = i + 6
        level = slot_level(slot)
        bench_enc = target_encounters(slot, bench)
        row = f"{slot:>4}  {level:>3}  {bench_enc:>6.0f} |"
        for name in curves:
            v = results[name][i]
            row += f" {('—' if v is None else f'{v:.0f}'):>15}"
        print(row)
    print("\nCosts:")
    for name, costs in curves.items():
        print(f"  {name:>15}: {costs}  (total {sum(costs)})")
    print("\nCells = median encounter at which the Slot opens. Compare with the 5e column.")


if __name__ == "__main__":
    main()
