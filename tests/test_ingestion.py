from me_r_sy.ingestion.grib import get_grib , get_var


def test_read_grib():
    df = get_grib("tests/data" , 2026 , 7)

    assert not df.empty
