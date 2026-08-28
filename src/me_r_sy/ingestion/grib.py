import cfgrib
import numpy as np


def get_grib(path):
    ds_grib = cfgrib.open_datasets(path)
    # t2m to °C
    ds_grib[0]["t2m"] = ds_grib[0]["t2m"] - 273.15
    ds_grib[0]["t2m"].attrs["units"] = "°C"
    ds_grib[0]["t2m"].attrs["GRIB_units"] = "°C"
    # msl to hpa
    ds_grib[0]["msl"] = ds_grib[0]["msl"] / 100
    ds_grib[0]["msl"].attrs["units"] = "hpa"
    ds_grib[0]["msl"].attrs["GRIB_units"] = "HectoPascal"
    # wind speed
    ds_grib[0]["w"] = np.sqrt(ds_grib[0]["u10"] ** 2 + ds_grib[0]["v10"] ** 2)
    ds_grib[0]["w"].attrs["GRIB_shortName"] = "w"
    ds_grib[0]["w"].attrs["long_name"] = "wind speed"
    # tp to mm
    ds_grib[1]["tp"] = ds_grib[1]["tp"] * 1000
    ds_grib[1]["tp"].attrs["units"] = "mm"
    ds_grib[1]["tp"].attrs["GRIB_units"] = "mm"
    if "step" in ds_grib[1]["tp"].dims:
        ds_grib[1]["tp"].attrs["GRIB_STAT"] = "ACCUMULATION"
        ds_grib[1]["tp"] = ds_grib[1]["tp"].sum(dim="step")
    else:
        ds_grib[1]["tp"].attrs["GRIB_STAT"] = "AVERAGE MONTHLY ACCUMULATION"
    return ds_grib


def get_var(ds):
    dic_vars = {var: ds[0][var] for var in ["t2m", "u10", "v10", "msl", "w"]}
    dic_vars["tp"] = ds[1]["tp"]
    return dic_vars


def get_ref_var(ds, month_range):
    dic_vars = {var: ds[0][var] for var in ["t2m", "u10", "v10", "msl", "w"]}
    dic_vars["tp"] = ds[1]["tp"]
    dic_vars["tp"] = dic_vars["tp"] * month_range
    for var in ["t2m", "u10", "v10", "msl", "tp", "w"]:
        dic_vars[var].attrs["GRIB_STAT"] = "CLIMATOLOGY"

    return dic_vars
