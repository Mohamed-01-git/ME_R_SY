# ME-R-SY

## Meteorological Reporting System

**ME-R-SY** is an open-source meteorological reporting system designed to transform daily meteorological observations into structured data, quality-controlled datasets, statistical analyses, visualizations, and automated reports.

### Workflow

```text
Meteorological observations
            │
            ▼
       Excel ingestion
            │
            ▼
      SQLite database
            │
            ▼
     Quality control
            │
            ▼
         Analysis
            │
            ▼
      Visualization
            │
            ▼
        Reporting
```

### Main goals

* 📥 Ingest daily meteorological observations
* 🗄️ Store historical observations in SQLite
* 🔍 Perform automated quality control
* 📊 Calculate meteorological statistics
* 📈 Generate meteorological visualizations
* 📄 Generate automated reports
* ⚙️ Automate the complete workflow
* 🌍 Provide an extensible open-source platform for meteorological applications

### Technology

* Python
* Bash
* SQLite
* Pandas
* NumPy
* Matplotlib
* PyYAML
* Conda

### Project status

🚧 **Early development**

ME-R-SY is currently under active development. The project architecture and APIs may change as new functionality is introduced.

### Installation

Clone the repository:

```bash
git clone git@github.com:YOUR_USERNAME/ME_R_SY.git
cd ME_R_SY
```

Create the Conda environment:

```bash
conda env create -f environment.yml
```

Activate it:

```bash
conda activate me_r_sy
```

### Development

Run the test suite:

```bash
pytest
```

Run the linter:

```bash
ruff check .
```

### License

ME-R-SY is released under the Apache License 2.0.

### Vision

ME-R-SY aims to provide a reproducible and extensible open-source framework for transforming operational meteorological observations into reliable information and automated meteorological reports.

> **ME-R-SY — From meteorological observations to automated reports.**

