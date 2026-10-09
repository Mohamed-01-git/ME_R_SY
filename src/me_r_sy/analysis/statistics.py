# this functions aims to return the needed statistic
#  in the required frequency ( monthly , daily ...).
import numpy as np


class Statistics:

    @staticmethod
    def get_stat(var, stat, freq):
        out = var.resample(time=freq).reduce(stat).squeeze()
        out.attrs["GRIB_STAT"] = stat.__name__.upper()
        return out

    @staticmethod
    def ref_avg(ds, month):
        return ds.groupby("time.month").mean().sel(month=month)

    # @staticmethod
    # def get_stat_day(var, stat):
    #     dims = [x for x in var.dims if (x != "time")]
    #     day = var.reduce(stat, dims).idxmax("time")
    #     out = var.sel(time=day)
    #     out.attrs["GRIB_STAT"] = stat.__name__.upper()
    #     lon = out.where(out == out.reduce(stat), drop=True)["longitude"].values
    #     lat = out.where(out == out.reduce(stat), drop=True)["latitude"].values
    #     dict_out = {"lon": lon, "lat": lat, "day": day, "values": out}
    #     return dict_out

    @staticmethod
    def get_stat_day(var, stat):
        dims = [dim for dim in var.dims if dim != "time"]

        # Find the time of the overall spatial maximum or minimum.
        spatial_extreme = var.reduce(stat, dim=dims)

        if stat is np.max:
            day = spatial_extreme.idxmax("time")
        elif stat is np.min:
            day = spatial_extreme.idxmin("time")
        else:
            raise ValueError("stat must be np.max or np.min")

        # Select the spatial grid for that day.
        out = var.sel(time=day)

        # Find one actual grid point containing the extreme.
        values = out.values
        flat_idx = np.nanargmax(values) if stat is np.max else np.nanargmin(values)
        lat_idx, lon_idx = np.unravel_index(flat_idx, values.shape)

        lon = float(out["longitude"].values[lon_idx])
        lat = float(out["latitude"].values[lat_idx])

        out.attrs["GRIB_STAT"] = stat.__name__.upper()

        return {
            "lon": lon,
            "lat": lat,
            "day": day,
            "values": out,
        }

    def calculate_statistics(self, variables):

        statistics = {
            "mean": {
                name: self.get_stat(var, np.mean, "ME")
                for name, var in variables.items()
            },
            "max": {
                name: self.get_stat(var, np.max, "ME")
                for name, var in variables.items()
            },
            "min": {
                name: self.get_stat(var, np.min, "ME")
                for name, var in variables.items()
                if name != "tp"
            },
            "accum": {"tp": variables["tp"].sum(dim="time")},
        }
        for var in ["t2m", "u10", "v10", "msl", "tp", "w"]:
            statistics["mean"][var].attrs["GRIB_STAT"] = "AVERAGE"
            statistics["max"][var].attrs["GRIB_STAT"] = "MAXIMUM"
            if var != "tp":
                statistics["min"][var].attrs["GRIB_STAT"] = "MINIMUM"

        return statistics

    def calculate_daily(self, variables):

        daily_stats = {
            "min": {
                name: self.get_stat_day(var, np.min)
                for name, var in variables.items()
                if name != "tp"
            },
            "max": {
                name: self.get_stat_day(var, np.max) for name, var in variables.items()
            },
        }
        return daily_stats

    def calculate_anomaly(self, statistics, ref_variables):
        anomaly = {
            name: statistics["mean"][name] - ref_variables[name]
            for name in statistics["mean"]
        }
        anomaly["tp"] = statistics["accum"]["tp"] - ref_variables["tp"]
        for var in ["t2m", "u10", "v10", "msl", "tp", "w"]:
            anomaly[var].attrs["GRIB_STAT"] = "ANOMALY"

        return anomaly
