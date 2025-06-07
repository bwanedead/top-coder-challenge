#!/usr/bin/env python3
"""
Black Box Challenge - Reimbursement System
Reverse-engineer the legacy travel reimbursement calculation
"""

import sys
import os

# Import our calculation logic
sys.path.append(os.path.join(os.path.dirname(__file__), 'calculations'))
from basecalculation import legacy_reimbursement

def calculate_reimbursement(trip_duration_days, miles_traveled, total_receipts_amount):
    """
    Calculate travel reimbursement using the reverse-engineered legacy system logic.
    
    Args:
        trip_duration_days (int): Number of days spent traveling
        miles_traveled (float): Total miles traveled (can be fractional)
        total_receipts_amount (float): Total dollar amount of receipts
    
    Returns:
        float: Reimbursement amount (rounded to 2 decimal places)
    """
    days = int(trip_duration_days)
    miles_raw = float(miles_traveled)
    miles_int = int(miles_raw)
    receipts = float(total_receipts_amount)
    
    return legacy_reimbursement(days, miles_int, receipts, miles_raw)

def main():
    """Main function to handle command line arguments and output result."""
    if len(sys.argv) != 4:
        print("Usage: python3 main.py <trip_duration_days> <miles_traveled> <total_receipts_amount>", file=sys.stderr)
        sys.exit(1)
    
    try:
        trip_duration_days = int(float(sys.argv[1]))
        miles_traveled = float(sys.argv[2])
        total_receipts_amount = float(sys.argv[3])
        
        result = calculate_reimbursement(trip_duration_days, miles_traveled, total_receipts_amount)
        
        # Output only the result (no extra text for the evaluation script)
        print(result)
        
    except ValueError as e:
        print(f"Error: Invalid input format - {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
