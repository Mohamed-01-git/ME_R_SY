import cfgrib

def get_grib(path) :
    ds_grib = cfgrib.open_datasets(path)
    #t2m to °C
    ds_grib[0]["t2m"] = ds_grib[0]["t2m"] - 273.15 
    ds_grib[0]["t2m"].attrs["units"] = "°C"
    ds_grib[0]["t2m"].attrs["GRIB_units"] = "°C"
    #msl to hpa
    ds_grib[0]["msl"] = ds_grib[0]["msl"]/100 
    ds_grib[0]["msl"].attrs["units"] = "hpa"
    ds_grib[0]["msl"].attrs["GRIB_units"] = "HectoPascal"
    #tp to mm
    ds_grib[1]["tp"] = ds_grib[1]["tp"]*1000 
    ds_grib[1]["tp"].attrs["units"] = "mm"
    ds_grib[1]["tp"].attrs["GRIB_units"] = "mm"
    return ds_grib

def get_var(ds , var) :
    i=0
    if var == "tp" :
        i = 1 
    variable = ds[i][var]
    return variable


