#!/usr/bin/env python3
"""
Replica of ACME's black-box reimbursement logic.
Inputs: <days:int> <miles:int|float-ish> <receipts:float>
Outputs: single float, 2-decimals.  No external deps.
"""

import sys

# ──────────────────────── Per-diem ──────────────────────────
def per_diem(days: int) -> float:
    bump = {5: 50, 6: 60, 7: 100}.get(days, 0)
    return 200 + 50 * days + bump                      # flat $50/day

# ───────────────── Mileage rate $/mi ───────────────────────
def mileage_rate(mpd: float) -> float:
    if mpd < 50:   return 0.36
    if mpd < 100:  return 0.40 + 0.0006 * (mpd - 50)
    if mpd < 125:  return 0.43 + 0.0010 * (mpd - 100)
    if mpd <= 175: return 0.55                          # higher plateau
    if mpd <= 250: return 0.45 - 0.0004 * (mpd - 175)
    return 0.30

# ───────────── Receipt multiplier vs spend/day ─────────────
def receipt_mult(spend: float) -> float:
    # under-spend penalty
    if spend < 30:  return 0.10
    if spend < 60:  return 0.10 + 0.02  * (spend - 30) / 30    # 0.10→0.70
    if spend < 120: return 0.70 + 0.005 * (spend - 60)         # 0.70→1.00
    if spend < 200: return 1.00 - 0.003 * (spend - 120)        # 1.00→0.76
    return 0.76 - 0.002 * (spend - 200)                        # asymptote ~0.36

# ─────────────────────── Jitter ±2 % ───────────────────────
def jitter(core: float, days: int, miles_seed: float, receipts: float) -> float:
    seed = (31 * days + 17 * int(miles_seed) + int(receipts * 100)) % 97
    rand = (seed * 61) % 101 / 100
    return (rand - 0.5) * 0.04 * core

# ─────────────────── Main calculator ───────────────────────
def legacy_reimbursement(days: int,
                         miles_int: int,
                         receipts: float,
                         miles_float_for_seed: float) -> float:
    # 1-day mega-receipt quirk
    if days == 1 and receipts > 1500:
        receipts = 0
        base = per_diem(days) + mileage_rate(miles_int / days) * miles_int
        total = base + jitter(base, days, miles_float_for_seed, receipts)
        return round(total * 0.5, 2)                     # **now actually halves**

    mpd   = miles_int / days
    spend = receipts / days

    total = (
        per_diem(days)
        + mileage_rate(mpd) * miles_int
        + receipt_mult(spend) * min(receipts, 150 * days)  # higher cap
    )

    # 49 / 99-cent rounding surprise
    if int(receipts * 100) % 100 in (49, 99):
        total += 50

    total += jitter(total, days, miles_float_for_seed, receipts)
    return round(total, 2)

# ──────────────────── CLI wrapper ──────────────────────────
if __name__ == "__main__":
    if len(sys.argv) != 4:
        sys.exit("Usage: basecalculation.py <days> <miles> <receipts>")
    try:
        days = int(float(sys.argv[1]))                   # accept "5.0"
        m_float = float(sys.argv[2])
        miles = int(m_float)                             # spec-compliant math
        receipts = float(sys.argv[3])
        if days < 1 or miles < 0 or receipts < 0:
            sys.exit("Error: inputs must be non-negative and days ≥ 1")
    except ValueError as e:
        sys.exit(f"Error: invalid numeric input – {e}")

    print(legacy_reimbursement(days, miles, receipts, m_float))
