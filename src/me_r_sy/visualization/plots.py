import numpy as np
import calendar
import warnings
import geopandas as gpd
import cartopy.crs as ccrs
import matplotlib.pyplot as plt

warnings.filterwarnings("ignore")

# I- NECESSARY TOOLS

# cmap_dict = {"2t": "RdYlBu_r", "tp": "GnBu", "msl": "viridis", "w": "YlOrRd"}

# cmap_dict_anom = {"2t": "bwr", "tp": "PuOr", "msl": "BrBG", "w": "RdGy"}

# shp_path = "/home/muhammed/METEO-REPORTING-SYSTEM/ME_R_SY/data/regions/regions.shp"
# shp = gpd.read_file(shp_path)


class Plotter:

    def __init__(self, shp, cmap_dict, cmap_dict_anom):
        self.shp = shp
        self.cmap_dict = cmap_dict
        self.cmap_dict_anom = cmap_dict_anom

    @staticmethod
    def create_map_figure():

        fig, ax = plt.subplots(
            figsize=(20, 15),
            ncols=2,
            nrows=2,
            subplot_kw={"projection": ccrs.PlateCarree()},
        )
        ax = ax.flatten()
        return fig, ax

    def plot_it(self, fig, ax, var):
        var_cmap = var.attrs["GRIB_shortName"]
        levels = np.linspace(var.min().values, var.max().values, 50)

        im = ax.contourf(
            var.longitude,
            var.latitude,
            var,
            levels=levels,
            cmap=self.cmap_dict[var_cmap],
        )

        self.shp.plot(ax=ax, facecolor="none")
        cb = fig.colorbar(im, ax=ax, shrink=0.8)
        cb.ax.set_ylabel(
            f"{var.attrs['long_name']} ({var.attrs['units']})", fontsize=10
        )
        ax.set_title(f"{var.attrs['GRIB_STAT']}  :  {var.attrs['long_name'].upper()} ")

    # plt.suptitle(f"AVERAGE DATA OVER MOROCCO FOR {year} / {calendar.month_name[month]}")

    def plot_wind(self, fig, ax, ds):

        u = ds["u10"][::3, ::3]
        v = ds["v10"][::3, ::3]
        w = ds["w"]
        im = ax.contourf(w.longitude, w.latitude, w, cmap="YlOrRd")
        self.shp.plot(ax=ax, facecolor="none")
        ax.barbs(u.longitude, v.latitude, u, v, sizes={"emptybarb": 0.01})
        cb = fig.colorbar(im, ax=ax, shrink=0.8)
        cb.ax.set_ylabel("WIND SPEED (m/s)")
        ax.set_title(f"{w.attrs['GRIB_STAT']} Wind (m/s) ")
        # plt.suptitle(f" AVERAGE DATA OVER MOROCCO {year} / {calendar.month_name[month]}")

    def plot_monthly_avg(self, statistics, year, month, output_dir):

        fig, ax = self.create_map_figure()
        self.plot_wind(fig, ax[0], statistics["mean"])
        self.plot_it(fig, ax[1], statistics["accum"]["tp"])
        for i, var in enumerate(["t2m", "msl"]):
            self.plot_it(fig, ax[i + 2], statistics["mean"][var])

        plt.suptitle(
            f"THE MONTHLY AVERAGE DATA OVER MOROCCO : {year} - {calendar.month_name[month].upper()}"
        )

        plt.savefig(f"{output_dir}/mean_{year}_{month:02d}.png")

    # The refreence period (1991-2020)

    def plot_reference(self, ref_variables, output_dir):
        fig, ax = self.create_map_figure()
        self.plot_wind(fig, ax[0], ref_variables)

        for i, var in enumerate(["t2m", "msl", "tp"]):
            self.plot_it(fig, ax[i + 1], ref_variables[var])

        plt.suptitle("THE MOROCCAN CLIMATOLOGY (1991-2020) ")
        plt.savefig(f"{output_dir}/reference_1991_2020.png")

    # the anomaly

    def plot_anomaly(self, anomaly, year, month, output_dir):
        fig, ax = self.create_map_figure()
        for i, var in enumerate(["t2m", "w", "msl", "tp"]):
            self.plot_it(fig, ax[i], anomaly[var])
        plt.suptitle(
            f"ANOMALY OVER MOROCCO FOR {year} - {calendar.month_name[month]} \n reference period (1991-2020)"
        )
        plt.savefig(f"{output_dir}/anom_{year}_{month:02d}.png")

    # max days vizualisation

    def plot_max_days(self, daily_stats, stat, year, month, output_dir):
        fig, ax = self.create_map_figure()
        in_dict = {
            "u10": daily_stats[stat]["u10"]["values"],
            "v10": daily_stats[stat]["v10"]["values"],
            "w": daily_stats[stat]["w"]["values"],
        }
        self.plot_wind(fig, ax[0], in_dict)
        ax[0].set_title(
            f"{stat.upper()} : {in_dict['w'].attrs['long_name'].upper()} \n {daily_stats[stat]['w']['values']['time'].dt.strftime('%Y-%d-%d').values}"
        )
        vars = ["t2m", "msl", "tp"]
        if stat == "min":
            vars = ["t2m", "msl"]
            ax[3].remove()

        for i, varname in enumerate(vars):
            var = daily_stats[stat][varname]["values"]
            self.plot_it(fig, ax[i + 1], var)
            ax[i + 1].set_title(
                f"{stat.upper()} : {var.attrs['long_name'].upper()} \n {var['time'].dt.strftime('%Y-%d-%d').values}"
            )
        plt.suptitle(
            f"{stat.upper()}IMUM OVER MOROCCO FOR {year} / {calendar.month_name[month]} \n reference period (1991-2020)"
        )
        plt.savefig(f"{output_dir}/{stat}_{year}_{month:02d}.png")


# # min days vizualisation

# fig, ax = create_map_figure()
# ax = ax.flatten()
# plot_wind(
#     fig,
#     ax[0],
#     daily_stats["min"]["u10"]["values"],
#     daily_stats["min"]["v10"]["values"],
#     daily_stats["min"]["w"]["values"],
#     shp,
#     year,
#     month,
# )
# ax[0].set_title(
#     f"MIN : {daily_stats['min']['w']['values'].attrs['long_name'].upper()} \n {daily_stats['min']['w']['values']['time'].dt.strftime('%Y-%d-%d').values}"
# )
# for i, varname in enumerate(["t2m", "msl", "tp"]):
#     var = daily_stats["min"][varname]["values"]
#     plot_it(fig, ax[i + 1], var, shp, year, month, cmap_dict)
#     ax[i + 1].set_title(
#         f"MIN : {var.attrs['long_name'].upper()} \n {var['time'].dt.strftime('%Y-%d-%d').values}"
#     )
# plt.suptitle(
#     f"MINIMUMS OVER MOROCCO FOR {year} / {calendar.month_name[month]} \n reference period (1991-2020)"
# )
# plt.savefig(f"{output_dir}/min_{year}_{month}.png")
