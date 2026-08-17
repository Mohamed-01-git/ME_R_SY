import cfgrib

def get_grib(root , year , month ) :
    path = f"{root}/input_{year}_{month:02d}.grib"
    ds_grib = cfgrib.open_datasets(path)
    ds_grib[0]["t2m"] = ds_grib[0]["t2m"] - 273.15 
    ds_grib[0]["t2m"].attrs["units"] = "°C"
    ds_grib[0]["t2m"].attrs["GRIB_units"] = "°C"
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


