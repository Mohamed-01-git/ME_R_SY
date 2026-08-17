from me_r_sy.ingestion.grib import read_meteorological_excel


def test_read_excel():
    df = read_meteorological_excel("tests/data/sample.xlsx")

    assert not df.empty
