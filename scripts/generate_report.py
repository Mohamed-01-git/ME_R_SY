from me_r_sy.ingestion.grib import get_grib , get_var
from me_r_sy.visualization.plots import plot_it , plot_wind
from me_r_sy.analysis.statistics import get_stat , ref_avg , get_stat_day
import geopandas as gpd
import numpy as np
import yaml
import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import calendar
import argparse
import os

parser = argparse.ArgumentParser(description="The configuration file for the reporting system")
parser.add_argument("--config" , required=True)
args = parser.parse_args()
config = args.config

with open(config , "r") as f : 
    config = yaml.safe_load(f)

cmap_dict = {
    "2t" : "RdYlBu_r" , 
    "tp"  : "GnBu" , 
    "msl" : "viridis" , 
    "w"   : "YlOrRd"
}


cmap_dict_anom = {
    "2t" : "bwr" , 
    "tp"  : "PuOr" , 
    "msl" : "BrBG" , 
    "w"   : "RdGy"
}
#====================================================================================================================

year       = config["date"]["year"]
month      = config["date"]["month"]
input_dir  = config["data"]["input"] 
ref_dir    = f"{input_dir}/reference_1991_2020.grib"
out_dir = config["data"]["output"] 
shp_path   = config["data"]["shapefile"]
year       = config["date"]["year"]
month      = config["date"]["month"]

output_dir = f"{out_dir}/report_{year}_{month}"
os.makedirs(output_dir , exist_ok = True)
# II- READ DATA

# read the shapefile
grib_path = f"{input_dir}/input_{year}_{month:02d}.grib"
ref_path  = f"{input_dir}/reference_1991_2020.grib"
shp = gpd.read_file(shp_path)
ds        = get_grib(grib_path)
ds_ref    = get_grib(ref_path)
ref_mean  = list(map(ref_avg , ds_ref))


#==============================================================================================================================

month_range = calendar.monthrange(year , month)[1]
# get vars
t   = get_var(ds , "t2m")
u   = get_var(ds , "u10")
v   = get_var(ds , "v10")
w   = np.sqrt(u**2 + v**2) 
tp  = get_var(ds , "tp").sum(dim = "step")
w.attrs["GRIB_shortName"] = "w"
w.attrs["long_name"] = "wind speed"
p   = get_var(ds , "msl") 

# # get monthly vars
# MEAN

t_mean  = get_stat(t , np.mean , "ME") 
u_mean  = get_stat(u , np.mean , "ME") 
v_mean  = get_stat(v , np.mean , "ME") 
w_mean  = get_stat(w , np.mean , "ME")
p_mean  = get_stat(p , np.mean , "ME") 
tp_accm = tp.sum(dim = "time")
tp_accm.attrs['GRIB_STAT'] = "ACCUMULATION"

# MAX (the day of max variable)
t_max   = get_stat_day(t , np.max) 
u_max   = get_stat_day(u , np.max) 
v_max   = get_stat_day(v , np.max) 
w_max   = get_stat_day(w , np.max) 
tp_max  = get_stat_day(tp, np.max) 
p_max   = get_stat_day(p, np.max) 

#  MIN (same as max)
t_min   = get_stat_day(t , np.min) 
u_min   = get_stat_day(u , np.min) 
v_min   = get_stat_day(v , np.min) 
w_min   = get_stat_day(w , np.min) 
tp_min  = get_stat_day(tp, np.min) 
p_min   = get_stat_day(p , np.min) 

# REF PERIOD AVERAGE
t_ref   = get_var(ref_mean , "t2m").sel(month = month)

u_ref   = get_var(ref_mean , "u10").sel(month = month)

v_ref   = get_var(ref_mean , "v10").sel(month = month)

w_ref   = np.sqrt(u_ref**2 + v_ref**2)
w_ref.attrs["GRIB_shortName"] = "w"
w_ref.attrs["long_name"] = "wind speed"

tp_ref_accm  = get_var(ref_mean , "tp").sel(month = month)* month_range
tp_ref_accm.attrs["GRIB_STAT"] =  "AVERAGE MONTHLY ACCUMULATION"

p_ref   = get_var(ref_mean , "msl").sel(month = month)

for var in [t_ref , u_ref , v_ref , w_ref , p_ref] : 
    var.attrs["GRIB_STAT"] = "MONTHLY AVERAGE CLIMATOLOGY"

# calculate the anomaly

t_anom  = t_mean  - t_ref 

p_anom  = p_mean  - p_ref

tp_anom = tp_accm - tp_ref_accm 

u_anom  = u_mean  - u_ref

v_anom  = v_mean  - v_ref 

w_anom  = w_mean  - w_ref

for var in [t_anom , p_anom , tp_anom , u_anom , v_anom , w_anom] : 
    var.attrs["GRIB_STAT"] = "ANOMALY"


#==============================================================================================================================
# PLOTS 

# The monthly average data 
 
fig , ax = plt.subplots(figsize = (20,15) , ncols = 2 , nrows = 2 , subplot_kw = {"projection" : ccrs.PlateCarree()})
ax = ax.flatten()
plot_wind(fig , ax[0] , u_mean , v_mean  , shp , year , month)
for i , var in enumerate([t_mean , p_mean , tp_accm]) : 
    plot_it(fig , ax[i+1] , var , shp , year , month , cmap_dict ) 
plt.savefig(f"{output_dir}/mean_{year}_{month}.png")

# The refreence period (1991-2020)

fig , ax = plt.subplots(figsize = (20,15) , ncols = 2 , nrows = 2 , subplot_kw = {"projection" : ccrs.PlateCarree()})
ax = ax.flatten()
for i , var in enumerate([w_ref , t_ref , p_ref , tp_ref_accm]) : 
    plot_it(fig , ax[i] , var , shp , year , month , cmap_dict) 
plt.suptitle(f"REFERENCE DATA OVER MOROCCO FOR {year} / {calendar.month_name[month]} \n reference period (1991-2020)")
plt.savefig(f"{output_dir}/ref_{year}_{month}.png")

# the anomaly 

fig , ax = plt.subplots(figsize = (20,15) , ncols = 2 , nrows = 2 , subplot_kw = {"projection" : ccrs.PlateCarree()})
ax = ax.flatten()
for i , var in enumerate([w_anom , t_anom , p_anom , tp_anom]) : 
    plot_it(fig , ax[i] , var , shp , year , month , cmap_dict_anom) 
plt.suptitle(f"ANOMALY OVER MOROCCO FOR {year} / {calendar.month_name[month]} \n reference period (1991-2020)")
plt.savefig(f"{output_dir}/anom_{year}_{month}.png")


# max days vizualisation

fig , ax = plt.subplots(figsize = (20,15) , ncols = 2 , nrows = 2 , subplot_kw = {"projection" : ccrs.PlateCarree()})
ax = ax.flatten()
plot_wind(fig , ax[0] , u_max , v_max  , shp , year , month)
ax[0].set_title(f"MAX : {w_max.attrs['long_name'].upper()} \n {w_max['time'].dt.strftime('%Y-%d-%d').values}")
for i , var in enumerate([t_max , p_max , tp_max]) : 
    plot_it(fig , ax[i+1] , var , shp , year , month , cmap_dict ) 
    ax[i+1].set_title(f"MAX : {var.attrs['long_name'].upper()} \n {var['time'].dt.strftime('%Y-%d-%d').values}")
plt.suptitle(f"MAXIMUM OVER MOROCCO FOR {year} / {calendar.month_name[month]} \n reference period (1991-2020)")
plt.savefig(f"{output_dir}/max_{year}_{month}.png")

# min days vizualisation

fig , ax = plt.subplots(figsize = (20,15) , ncols = 2 , nrows = 2 , subplot_kw = {"projection" : ccrs.PlateCarree()})
ax = ax.flatten()
plot_wind(fig , ax[0] , u_min , v_min  , shp , year , month)
ax[0].set_title(f"MIN : {w_min.attrs['long_name'].upper()} \n {var['time'].dt.strftime('%Y-%d-%d').values}")
for i , var in enumerate([t_min , p_min , tp_min]) : 
    plot_it(fig , ax[i+1] , var , shp , year , month , cmap_dict ) 
    ax[i+1].set_title(f"MIN : {var.attrs['long_name'].upper()} \n {var['time'].dt.strftime('%Y-%d-%d').values}")
plt.suptitle(f"MINIMUMS OVER MOROCCO FOR {year} / {calendar.month_name[month]} \n reference period (1991-2020)")
plt.savefig(f"{output_dir}/min_{year}_{month}.png")

