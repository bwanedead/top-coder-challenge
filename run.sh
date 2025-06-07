#!/usr/bin/env bash

# Black Box Challenge - Your Implementation
# This script should take three parameters and output the reimbursement amount
# Usage: ./run.sh <trip_duration_days> <miles_traveled> <total_receipts_amount>

exec python3 "$(dirname "$0")/calculations/basecalculation.py" "$@" 