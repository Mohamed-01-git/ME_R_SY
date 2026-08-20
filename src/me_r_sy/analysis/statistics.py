
# this functions aims to return the needed statistic in the required frequency ( monthly , daily ...).
def get_stat(var , stat ,freq) : 
    out = var.resample(time = freq).reduce(stat).squeeze() 
    return out
    
def ref_avg(ds) : 
    return ds.groupby(f"time.month").mean()
