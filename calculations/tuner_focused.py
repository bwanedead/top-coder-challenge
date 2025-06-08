import pandas as pd
import numpy as np
import json
import sys
import os
from itertools import product
import time

# Add parent directory to path to import basecalculation
sys.path.append('..')
sys.path.append('.')

# Load public_cases.json
with open('../public_cases.json', 'r') as f:
    cases_data = json.load(f)

# Convert to DataFrame
data_rows = []
for case in cases_data:
    data_rows.append({
        'trip_duration_days': case['input']['trip_duration_days'],
        'miles_traveled': case['input']['miles_traveled'],
        'total_receipts_amount': case['input']['total_receipts_amount'],
        'reimbursement': case['expected_output']
    })

df = pd.DataFrame(data_rows)
print(f"Loaded {len(df)} test cases from public_cases.json")

# Import our production basecalculation module
import basecalculation as prod

# Focused parameter grid around our hand-tuned values
param_grid = {
    'per_diem_base_short': [190, 210],
    'per_diem_rate_short': [40, 42],
    'per_diem_base_long': [160, 180],
    'per_diem_rate_long': [35, 38],
    'mileage_peak': [0.55, 0.60],
    'short_trip_mult': [0.60, 0.65, 0.70],
    'vacation_mult': [0.03, 0.05]
}

def score_params(params):
    """Score a parameter set by temporarily modifying the production module."""
    base_s, rate_s, base_l, rate_l, peak, st_mult, vac_mult = params
    
    # Store original functions
    orig_per_diem = prod.per_diem
    orig_mileage_rate = prod.mileage_rate
    orig_receipt_mult = prod.receipt_mult
    
    try:
        # Temporarily replace functions with parameterized versions
        def new_per_diem(days):
            bump = {5: 50, 6: 60, 7: 100}.get(days, 0)
            if days <= 7:
                return base_s + rate_s * days + bump
            return base_l + rate_l * days + bump
        
        def new_mileage_rate(mpd):
            if mpd < 50:
                return 0.36
            if mpd < 100:
                return 0.40 + 0.0008 * (mpd - 50)
            if mpd < 125:
                return 0.44 + 0.0012 * (mpd - 100)
            if mpd <= 175:
                return peak
            if mpd <= 250:
                return 0.50 - 0.0004 * (mpd - 175)
            return 0.40
        
        def new_receipt_mult(spend, days):
            if days >= 8:
                return max(0.25, vac_mult * prod.base_mult(spend))
            if days <= 3 and spend > 500:
                return st_mult
            return prod.base_mult(spend)
        
        # Monkey patch
        prod.per_diem = new_per_diem
        prod.mileage_rate = new_mileage_rate
        prod.receipt_mult = new_receipt_mult
        
        # Calculate errors
        errors = []
        for _, row in df.iterrows():
            pred = prod.legacy_reimbursement(
                int(row['trip_duration_days']),
                int(row['miles_traveled']),
                row['total_receipts_amount'],
                row['miles_traveled']
            )
            error = abs(pred - row['reimbursement'])
            errors.append(error)
        
        mae = np.mean(errors)
        max_error = max(errors)
        return mae, max_error
        
    finally:
        # Restore original functions
        prod.per_diem = orig_per_diem
        prod.mileage_rate = orig_mileage_rate
        prod.receipt_mult = orig_receipt_mult

# Grid search
combinations = list(product(
    param_grid['per_diem_base_short'],
    param_grid['per_diem_rate_short'],
    param_grid['per_diem_base_long'],
    param_grid['per_diem_rate_long'],
    param_grid['mileage_peak'],
    param_grid['short_trip_mult'],
    param_grid['vacation_mult']
))

print(f"Testing {len(combinations)} focused combinations...")

best_mae = float('inf')
best_params = None
best_max_error = float('inf')

start_time = time.time()

for idx, params in enumerate(combinations):
    mae, max_error = score_params(params)
    
    # Prioritize MAE < 200 and max_error < 700
    if mae < best_mae and max_error < 700:
        best_mae = mae
        best_params = params
        best_max_error = max_error
        print(f"New best: MAE={mae:.2f}, Max={max_error:.2f}")
    
    if idx % 50 == 0:
        print(f"Processed {idx}/{len(combinations)}")

print(f"\nFocused tuning complete in {time.time() - start_time:.2f} seconds")
print(f"Best MAE: {best_mae:.2f}")
print(f"Best Max Error: {best_max_error:.2f}")
print("Best Parameters:")
print(f"per_diem_base_short: {best_params[0]}")
print(f"per_diem_rate_short: {best_params[1]}")
print(f"per_diem_base_long: {best_params[2]}")
print(f"per_diem_rate_long: {best_params[3]}")
print(f"mileage_peak: {best_params[4]}")
print(f"short_trip_mult: {best_params[5]}")
print(f"vacation_mult: {best_params[6]}")

# Show expected score improvement
expected_score = best_mae * len(df)
print(f"Expected score: ~{expected_score:.0f}") 