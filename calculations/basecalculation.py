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
    """Per diem with adjusted rates."""
    bump = {5: 50, 6: 60, 7: 100}.get(days, 0)
    if days <= 7:
        return 250 + 50 * days + bump          # unchanged short-trip rate
    return 150 + 35 * days + bump              # lower long-trip rate

def mileage_rate(mpd: float) -> float:
    """$/mile peaking at 125-175 mpd."""
    if mpd < 50:
        return 0.36
    if mpd < 100:
        return 0.40 + 0.0008 * (mpd - 50)
    if mpd < 125:
        return 0.44 + 0.0012 * (mpd - 100)
    if mpd <= 175:
        return 0.60  # Increased peak
    if mpd <= 250:
        return 0.50 - 0.0004 * (mpd - 175)
    return 0.40

def base_mult(spend: float) -> float:
    """Base multiplier curve without penalties."""
    if spend < 30:
        return 0.10
    if spend < 60:
        return 0.10 + 0.0233 * (spend - 30)  # 0.10→0.80
    if spend < 120:
        return 0.80 + 0.0017 * (spend - 60)  # 0.80→0.90
    if spend < 200:
        return 0.90 - 0.0015 * (spend - 120)  # 0.90→0.78
    return max(0.20, 0.78 - 0.001 * (spend - 200))

def receipt_mult(spend: float, days: int) -> float:
    """Multiplier with penalties for high spending."""
    # vacations: always chop in half once trip is long, regardless of spend
    if days >= 8:
        return max(0.20, 0.5 * base_mult(spend))

    # 1-3 day blow-outs: use gentler 0.40 floor instead of 0.30
    if days <= 3 and spend > 500:
        return 0.40

    return base_mult(spend)

def jitter(core: float, days: int, miles_seed: float, receipts: float) -> float:
    """±2% deterministic jitter via LCG."""
    seed = (31 * days + 17 * int(miles_seed) + int(receipts * 100)) % 97
    rand = ((seed * 61) % 101) / 100.0
    return (rand - 0.5) * 0.04 * core

# ---------- main calculation ----------

def legacy_reimbursement(days: int, miles_int: int, receipts: float,
                         miles_float_for_seed: float) -> float:
    # 1-day, R > 1500 – pay per-diem + juicy mileage + flat bonus
    if days == 1 and receipts > 1500:
        core = (
            per_diem(days)
            + 0.95 * miles_int                 # mileage premium
            + 0.8 * min(receipts, 600)         # up to $480 extra
        )
        total = core + jitter(core, days, miles_int, receipts)
        return round(total, 2)

    mpd = miles_int / days
    spend = receipts / days
    # allow a bit more head-room on 2-3 day monsters
    receipt_cap = 100 * days if days <= 3 else 150 * days

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
