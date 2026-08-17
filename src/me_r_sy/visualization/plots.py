import numpy as np
import geopandas as gpd
import warnings
warnings.filterwarnings("ignore")
import cartopy.crs as ccrs
import matplotlib.pyplot as plt

# I- NECESSARY TOOLS

cmap_dict = {
    "2t" : "RdYlBu_r" , 
    "tp"  : "GnBu" , 
    "msl" : "viridis" , 
    "w"   : "YlOrRd"
}

def plot_it(fig ,ax , var , shp , year , month) : 
    var_cmap = var.attrs["GRIB_shortName"]
    levels = np.linspace(var.min().values , var.max().values , 50 )
    im = ax.contourf(var.longitude , var.latitude , var , levels = levels , cmap = cmap_dict[var_cmap]) 
    shp.plot(ax = ax , facecolor = 'none')
    cb = fig.colorbar(im , ax = ax , shrink = 0.8)
    cb.ax.set_ylabel(f"{var.attrs['long_name']} ({var.attrs['units']})" , fontsize = 10)
    ax.set_title(f"{var.attrs['long_name']} ")
    plt.suptitle(f"AVERAGE DATA OVER MOROCCO FOR {year} / {month:02d}")

def plot_wind(fig , ax  , u , v , w , shp , year , month) : 
    
    im = ax.contourf(w.longitude , w.latitude , w)
    u = u[::3,::3]
    v = v[::3,::3]
    ax.barbs(u.longitude , v.latitude, u , v , sizes= {"emptybarb" : 0.01})
    cb = fig.colorbar(im , ax = ax , shrink = 0.8)
    cb.ax.set_ylabel(f"WIND SPEED (m/s)")
    shp.plot(ax = ax , facecolor = 'none')
    plt.suptitle(f"AVERAGE DATA OVER MOROCCO {year} / {month}")
    ax.set_title(f" Wind (m/s) ")


    
