#!/usr/bin/env python3
"""
Replica of ACME's legacy reimbursement logic.
 – Accepts:  <days:int> <miles:int|float-ish> <receipts:float>
 – Internally coerces days & miles to INT (spec-compliant math).
 – No external dependencies; deterministic ±2 % "jitter".
"""

import sys

# ────────────────────────── Per-diem ──────────────────────────
def per_diem(days: int) -> float:
    bump = {5: 50, 6: 60, 7: 100}.get(days, 0)
    daily = 50 if days <= 7 else 40               # long-trip haircut
    return 200 + daily * days + bump

# ───────────────────────── Mileage $/mi ───────────────────────
def mileage_rate(mpd: float) -> float:
    if mpd < 50:   return 0.36
    if mpd < 100:  return 0.40 + 0.0006*(mpd-50)
    if mpd < 125:  return 0.43 + 0.0010*(mpd-100)
    if mpd <=175:  return 0.50                    # sweet-spot
    if mpd <=250:  return 0.40 - 0.0004*(mpd-175)
    return 0.30                                   # marathon

# ───────────────────── Receipt multiplier ─────────────────────
def receipt_mult(spend: float, days: int) -> float:
    if days >= 8 and spend > 90:          # "vacation" penalty
        return 0.05
    if spend < 30:    return 0.00
    if spend < 60:    return 0.25 + 0.008*(spend-30)
    if spend < 120:   return 0.49 + 0.003*(spend-60)
    if spend < 200:   return 0.67 - 0.0015*(spend-120)
    if spend < 250:   return 0.55 - 0.004*(spend-200)
    return max(0.20, 0.35 - 0.001*(spend-250))

# ────────────────────────── Jitter ────────────────────────────
def jitter(core: float, days: int, miles_seed: float, receipts: float) -> float:
    seed = (31*days + 17*int(miles_seed) + int(receipts*100)) % 97
    rand = (seed*61) % 101 / 100
    return (rand - 0.5) * 0.04 * core            # ±2 %

# ───────────────────── Master calculation ─────────────────────
def legacy_reimbursement(days: int, miles_int: int, receipts: float,
                         miles_float_for_seed: float) -> float:
    # 1-day mega-receipt edge-case
    if days == 1 and receipts > 1500:
        receipts = 0

    mpd   = miles_int / days
    spend = receipts / days

    total = (
        per_diem(days)
        + mileage_rate(mpd) * miles_int
        + receipt_mult(spend, days) * min(receipts, 100 * days)  # dynamic cap
    )

    # Rounding-cents bonus
    if int(receipts * 100) % 100 in (49, 99):
        total += 50

    total += jitter(total, days, miles_float_for_seed, receipts)
    return round(total, 2)

# ────────────────────────── CLI glue ──────────────────────────
if __name__ == "__main__":
    if len(sys.argv) != 4:
        sys.exit("Usage: basecalculation.py <days> <miles> <receipts>")

    try:
        # days: forced integer (even if evaluator sends "5.0")
        days = int(float(sys.argv[1]))
        # miles: keep both int (for math) and float (for seed uniqueness)
        miles_raw = float(sys.argv[2])
        miles_int = int(miles_raw)         # spec says integer math
        # receipts
        receipts = float(sys.argv[3])

        if days < 1 or miles_int < 0 or receipts < 0:
            sys.exit("Error: inputs must be non-negative and days ≥ 1")

    except ValueError as e:
        sys.exit(f"Error: invalid numeric input – {e}")

    print(legacy_reimbursement(days, miles_int, receipts, miles_raw))
