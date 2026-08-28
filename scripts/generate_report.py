from me_r_sy.ingestion.grib import get_grib, get_var, get_ref_var
from me_r_sy.visualization.plots import Plotter
from me_r_sy.analysis.statistics import Statistics
import geopandas as gpd
import yaml
import calendar
import argparse
import os

# =========A- GET THE PARAMETERS READY FOR THE SYSTEM===========================================================================================================

parser = argparse.ArgumentParser(
    description="The configuration file for the reporting system"
)
parser.add_argument("--config", required=True)
args = parser.parse_args()
config = args.config

with open(config, "r") as f:
    config = yaml.safe_load(f)

cmap_dict = {"2t": "RdYlBu_r", "tp": "GnBu", "msl": "viridis", "w": "YlOrRd"}

cmap_dict_anom = {"2t": "bwr", "tp": "PuOr", "msl": "BrBG", "w": "RdGy"}

year = config["date"]["year"]
month = config["date"]["month"]
input_dir = config["data"]["input"]
ref_dir = f"{input_dir}/reference_1991_2020.grib"
out_dir = config["data"]["output"]
shp_path = config["data"]["shapefile"]
year = config["date"]["year"]
month = config["date"]["month"]
output_dir = f"{out_dir}/report_{year}_{month}"
os.makedirs(output_dir, exist_ok=True)


# =========B- READ THE DATA ===========================================================================================================

# get vars

grib_path = f"{input_dir}/input_{year}_{month:02d}.grib"

ref_path = f"{input_dir}/reference_1991_2020.grib"

cmap_dict = {"2t": "RdYlBu_r", "tp": "GnBu", "msl": "viridis", "w": "YlOrRd"}

cmap_dict_anom = {"2t": "bwr", "tp": "PuOr", "msl": "BrBG", "w": "RdGy"}

shp = gpd.read_file(shp_path)
ds = get_grib(grib_path)
ds_ref = get_grib(ref_path)
ref_mean = list(map(lambda ds: Statistics.ref_avg(ds, month), ds_ref))
month_range = calendar.monthrange(year, month)[1]

variables = get_var(ds)
ref_variables = get_var(ref_mean)
ref_variables["tp"] = ref_variables["tp"] * month_range

Statistics = Statistics()
Plotter = Plotter(shp, cmap_dict, cmap_dict_anom)
statistics = Statistics.calculate_statistics(variables=variables)
daily_stats = Statistics.calculate_daily(variables)
anomaly = Statistics.calculate_anomaly(statistics, ref_variables)

# ======== C - VIZUALISATION ==============================================================================


## 1 MONTHLY AVERAGE

Plotter.plot_monthly_avg(statistics, year, month, output_dir)

## 2 MONTHLY MAX

Plotter.plot_max_days(daily_stats, "max", year, month, output_dir)

## 3 MONTHLY MIN

Plotter.plot_max_days(daily_stats, "min", year, month, output_dir)

## 4 ANOMALY

Plotter.plot_anomaly(anomaly, year, month, output_dir)
