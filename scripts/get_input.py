import cdsapi
import argparse
import os
import sys
import numpy as np
import calendar
import yaml

# get the configuration file
parser = argparse.ArgumentParser(description="Download ERA5 single-level data from CDS")
parser.add_argument("--config", required=True)
args = parser.parse_args()

config = args.config

with open(config, "r") as f:
    config = yaml.safe_load(f)

# extract required parameters from the config file

in_dir = config["data"]["input"]
os.makedirs(in_dir, exist_ok=True)

variables = config["era5"]["vars"]
area = config["era5"]["area"]
year = config["date"]["year"]
month = config["date"]["month"]
output_filename = f"{in_dir}/input_{year}_{month:02d}.grib"

if os.path.exists(output_filename):
    print(f"✅ File already exists: {output_filename}")
    sys.exit(0)

try:
    client = cdsapi.Client()
    client.retrieve(
        "reanalysis-era5-single-levels",
        {
            "product_type": "reanalysis",
            "variable": variables,
            "year": year,
            "month": month,
            "day": [f"{x+1:02d}" for x in range(calendar.monthrange(year, month)[1])],
            "time": [f"{x:02d}:00" for x in np.arange(0, 24)],
            "data_format": "grib",
            "area": [37, -18, 20, 0],
        },
    ).download(output_filename)

    print(f"✅ Download complete: {output_filename}")

except Exception as e:
    print(f"❌ Error during download: {e}")
    sys.exit(1)
