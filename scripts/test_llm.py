from me_r_sy.llm.generator import MeteorologicalReportGenerator


data = {
    "period": "Janvier 2026",
    "temperature": {
        "mean": 15.8,
        "anomaly": 1.7
    },
    "precipitation": {
        "accumulated": 42.5,
        "reference": 68.3,
        "anomaly_percent": -37.8
    },
    "extreme_temperature": {
        "maximum": 29.4,
        "minimum": 2.8
    }
}


generator = MeteorologicalReportGenerator()

report = generator.generate(data)

print("\n")
print("=" * 80)
print("RAPPORT METEOROLOGIQUE")
print("=" * 80)
print(report)
