#!/usr/bin/env python3
"""
Black Box Challenge - Reimbursement System
Reverse-engineer the legacy travel reimbursement calculation
"""

import sys

def calculate_reimbursement(trip_duration_days, miles_traveled, total_receipts_amount):
    """
    Calculate travel reimbursement based on the legacy system logic.
    
    Args:
        trip_duration_days (int): Number of days spent traveling
        miles_traveled (int): Total miles traveled
        total_receipts_amount (float): Total dollar amount of receipts
    
    Returns:
        float: Reimbursement amount (rounded to 2 decimal places)
    """
    
    # TODO: Implement the actual logic based on your analysis of:
    # - PRD.md (business requirements)
    # - INTERVIEWS.md (employee hints)
    # - public_cases.json (historical patterns)
    
    # Placeholder calculation - replace with actual logic
    reimbursement = 0.0
    
    # Example components you might need to consider:
    # - Base daily allowance
    # - Mileage reimbursement
    # - Receipt reimbursement (full or partial)
    # - Special rules for different trip lengths
    # - Caps or limits on certain categories
    
    # Simple placeholder formula (replace this!)
    reimbursement = trip_duration_days * 50 + miles_traveled * 0.5 + total_receipts_amount
    
    return round(reimbursement, 2)

def main():
    """Main function to handle command line arguments and output result."""
    if len(sys.argv) != 4:
        print("Usage: python3 main.py <trip_duration_days> <miles_traveled> <total_receipts_amount>", file=sys.stderr)
        sys.exit(1)
    
    try:
        trip_duration_days = int(sys.argv[1])
        miles_traveled = int(sys.argv[2])
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
