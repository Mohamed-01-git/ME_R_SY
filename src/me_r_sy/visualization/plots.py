import numpy as np
import calendar
import warnings
warnings.filterwarnings("ignore")
import cartopy.crs as ccrs
import matplotlib.pyplot as plt

# I- NECESSARY TOOLS


def plot_it(fig ,ax , var , shp , year , month , cmap_dict) : 
    var_cmap = var.attrs["GRIB_shortName"]
    levels = np.linspace(var.min().values , var.max().values , 50 )
    im = ax.contourf(var.longitude , var.latitude , var , 
                     levels = levels , cmap = cmap_dict[var_cmap]) 
    shp.plot(ax = ax , facecolor = 'none')
    cb = fig.colorbar(im , ax = ax , shrink = 0.8)
    cb.ax.set_ylabel(f"{var.attrs['long_name']} ({var.attrs['units']})" , fontsize = 10)
    ax.set_title(f"{var.attrs['long_name']} ")
    plt.suptitle(f"AVERAGE DATA OVER MOROCCO FOR {year} / {calendar.month_name[month]}")

def plot_wind(fig , ax  , u , v , shp , year , month) : 
    
    u = u[::3,::3]
    v = v[::3,::3]
    w = np.sqrt(u**2 + v**2)
    im = ax.contourf(w.longitude , w.latitude , w , cmap = "YlOrRd")
    ax.barbs(u.longitude , v.latitude, u , v , sizes= {"emptybarb" : 0.01})
    cb = fig.colorbar(im , ax = ax , shrink = 0.8)
    cb.ax.set_ylabel("WIND SPEED (m/s)")
    shp.plot(ax = ax , facecolor = 'none')
    plt.suptitle(f"AVERAGE DATA OVER MOROCCO {year} / {calendar.month_name[month]}")
    ax.set_title(" Wind (m/s) ")


    
