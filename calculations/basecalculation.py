#!/usr/bin/env python3
"""
Replica of ACME's legacy reimbursement logic.
Accepts: <days:int> <miles:int|float-ish> <receipts:float>
Coerces days & miles to int for calculations.
No dependencies; deterministic ±2% jitter.
"""

import sys

# ---------- piece-wise helpers ----------

def per_diem(days: int) -> float:
    """Per diem with lower rate for long trips."""
    bump = {5: 50, 6: 60, 7: 100}.get(days, 0)
    daily = 50 if days <= 7 else 40  # Reduced for long trips
    return 200 + daily * days + bump

def mileage_rate(mpd: float) -> float:
    """$/mile peaking at 125-175 mpd."""
    if mpd < 50:
        return 0.36
    if mpd < 100:
        return 0.40 + 0.0006 * (mpd - 50)
    if mpd < 125:
        return 0.43 + 0.0010 * (mpd - 100)
    if mpd <= 175:
        return 0.55
    if mpd <= 250:
        return 0.45 - 0.0004 * (mpd - 175)
    return 0.35

def receipt_mult(spend: float, days: int) -> float:
    """Multiplier with vacation penalty and non-negative values."""
    if days >= 8 and spend > 120:  # Vacation penalty
        return 0.15
    if days <= 3 and spend > 1000/days:  # Short-trip high-receipt penalty
        return 0.1
    if spend < 30:
        return 0.10
    if spend < 60:
        return 0.10 + 0.0167 * (spend - 30)  # 0.10→0.60
    if spend < 120:
        return 0.60 + 0.0025 * (spend - 60)  # 0.60→0.75
    if spend < 200:
        return 0.75 - 0.0015 * (spend - 120)  # 0.75→0.63
    return max(0.20, 0.63 - 0.001 * (spend - 200))  # Asymptote ~0.20

def jitter(core: float, days: int, miles_seed: float, receipts: float) -> float:
    """±2% deterministic jitter via LCG."""
    seed = (31 * days + 17 * int(miles_seed) + int(receipts * 100)) % 97
    rand = ((seed * 61) % 101) / 100.0
    return (rand - 0.5) * 0.04 * core

# ---------- main calculation ----------

def legacy_reimbursement(days: int, miles_int: int, receipts: float,
                         miles_float_for_seed: float) -> float:
    # 1-day mega-receipt edge-case
    if days == 1 and receipts > 1500:
        receipts = 0
        mpd = miles_int / days
        core = per_diem(days) + mileage_rate(mpd) * miles_int
        total = core + jitter(core, days, miles_float_for_seed, receipts)
        return round(total * 0.5, 2)

    mpd = miles_int / days
    spend = receipts / days
    receipt_cap = 100 * days if days <= 3 else 150 * days  # Tighter for short trips

    total = (
        per_diem(days) +
        mileage_rate(mpd) * miles_int +
        receipt_mult(spend, days) * min(receipts, receipt_cap)
    )

    # Rounding-cents bonus
    if int(receipts * 100) % 100 in (49, 99):
        total += 50

    total += jitter(total, days, miles_float_for_seed, receipts)
    return round(total, 2)

# ---------- CLI wrapper ----------

if __name__ == "__main__":
    if len(sys.argv) != 4:
        sys.exit("Usage: basecalculation.py <days> <miles> <receipts>")
    try:
        days = int(float(sys.argv[1]))
        m_float = float(sys.argv[2])
        miles = int(m_float)
        receipts = float(sys.argv[3])
        if days < 1 or miles < 0 or receipts < 0:
            sys.exit("Error: inputs must be non-negative and days ≥ 1")
    except ValueError as e:
        sys.exit(f"Error: invalid numeric input – {e}")
    print(legacy_reimbursement(days, miles, receipts, m_float))
