import cdsapi
import argparse
import os
import sys
import numpy as np
import yaml


# get the configuration file
parser = argparse.ArgumentParser(description="Download ERA5 single-level data from CDS")
parser.add_argument("--config", required=True)
args = parser.parse_args()

config = args.config

with open(config , "r") as f : 
    config = yaml.safe_load(f)

# extract required parameters from the config file

in_dir = config["data"]["input"]
os.makedirs(in_dir, exist_ok=True)

variables = config["era5"]["vars"]
area      = config["era5"]["area"] 
output_filename = f"{in_dir}/trailar_2026.grib"

if os.path.exists(output_filename):
    print(f"✅ File already exists: {output_filename}")
    sys.exit(0)

try:
    client = cdsapi.Client()
    client.retrieve(
    "reanalysis-era5-single-levels-monthly-means",
    {
    "product_type": ["monthly_averaged_reanalysis"],
    "variable": variables,
    "year": 2026,
    "month": [
        "01", "02", "03",
        "04" 
    ],
    "time": ["00:00"],
    "data_format": "grib",
    "download_format": "unarchived",
    "area": area
        }
                    ).download(output_filename)

    print(f"✅ Download complete: {output_filename}")

except Exception as e:
    print(f"❌ Error during download: {e}")
    sys.exit(1)

