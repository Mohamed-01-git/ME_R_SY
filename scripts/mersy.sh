#!/bin/sh


config=$1
echo "DOWNLOADING THE DATA"

python get_input.py --config "$config"

echo "GENERATING THE REPORT"

python generate_report.py --config "$config"




