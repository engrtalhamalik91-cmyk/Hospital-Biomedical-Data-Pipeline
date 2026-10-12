# Clinical Operations & Medical Equipment Risk Analysis Pipeline

![Python](https://img.shields.io/badge/Python-3.x-blue?logo=python&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-Data%20Analysis-150458?logo=pandas&logoColor=white)
![NumPy](https://img.shields.io/badge/NumPy-Numerical%20Computing-013243?logo=numpy&logoColor=white)
![Matplotlib](https://img.shields.io/badge/Matplotlib-Visualization-11557c)


A Python-based healthcare analytics project that processes medical equipment registry and maintenance/failure records to generate operational audit data, risk visualizations, and executive reports.

This project combines my **Biomedical Engineering background** with my developing skills in **Python-based data analysis and healthcare operations reporting**.

## Project Overview

Hospitals depend on medical equipment availability to support clinical workflows. Maintenance and failure records can help biomedical engineering teams understand equipment downtime, patient delays, repair expenses, and service-contract performance.

This pipeline takes two CSV files, standardizes equipment identifiers, matches maintenance records to the equipment registry, applies basic downtime validation rules, calculates summary metrics, and exports results in multiple formats.

> **Project scope:** This is a batch-processing analytics prototype. It processes files provided locally; it is not a live hospital integration system, and its rule-based risk classification is not a machine-learning model or a clinical decision-support system.

## Visual Overview

### Pipeline workflow

![Clinical operations pipeline workflow](assets/pipeline_workflow.png)

### Example risk-analysis chart

> **Note:** The chart below uses illustrative values only because the real input CSV files were not supplied. It demonstrates the type of visualization this project can produce; it is not a result from actual hospital or equipment data.

![Illustrative equipment downtime and patient delays chart](assets/risk_analysis_example.png)

### Expected report outputs

![Pipeline output files preview](assets/output_files_preview.png)

## Objectives

- Read medical equipment registry and maintenance/failure records.
- Standardize device IDs by trimming whitespace and converting IDs to uppercase.
- Match maintenance records with registered equipment.
- Flag records with missing, non-positive, or greater-than-168-hour downtime values.
- Summarize downtime, reported patient delays, parts costs, service charges, and service-contract values.
- Identify records with the highest downtime and patient-delay counts.
- Generate a chart and export the audit results to CSV, Excel, and PDF.

## Technologies Used

- **Python** — pipeline logic and calculations
- **Pandas** — tabular data ingestion, cleaning, merging, and aggregation *(Pandas version)*
- **NumPy** — rule-based conditional processing *(Pandas version)*
- **CSV** — flat-file input/output *(standard-library version)*
- **Matplotlib** — chart generation
- **OpenPyXL** — Excel workbook formatting and chart insertion
- **ReportLab** — PDF report generation

Two implementations are included:
1. **Standard-library CSV version:** uses Python's `csv` module for row-by-row processing.
2. **Pandas/NumPy version:** uses DataFrames, numeric coercion, merging, and vectorized conditional operations.

## Input Files

Place the following files in the same directory as the Python script:

### `equipment_registry.csv`

Expected columns:

| Column | Description |
|---|---|
| `Device ID` | Unique equipment identifier |
| `Equipment Name` | Medical equipment name |
| `Base Contract Value` | Base service-contract value |

### `maintenance_failure_logs.csv`

Expected columns:

| Column | Description |
|---|---|
| `Device ID` | Equipment identifier recorded in the log |
| `Downtime Hours` | Reported equipment downtime in hours |
| `Patients Delayed` | Reported number of patients delayed |
| `Part Replacement Cost` | Parts replacement cost |
| `Service Repair Charge` | Service or repair charge |

Use synthetic or appropriately de-identified sample data. Do not upload patient-identifiable, confidential hospital, or commercially sensitive information to a public repository.

## How the Pipeline Works

1. **Load the source data** from the equipment registry and maintenance/failure logs.
2. **Normalize identifiers** so that values such as ` dev-001 ` and `DEV-001` can be matched.
3. **Match equipment and logs** using the device ID.
4. **Validate downtime** using a basic rule: downtime must be present, greater than zero, and no more than 168 hours.
5. **Calculate summary metrics**, including total downtime, reported patient delays, parts costs, repair charges, contract values, and expense-to-contract ratio.
6. **Identify high-impact records** by downtime and reported patient delays.
7. **Create a visualization** comparing downtime and patient-delay counts.
8. **Export the results** to CSV and Excel, then create an executive-style PDF report.

## Generated Outputs

The script is designed to create the following files:

| Output | Purpose |
|---|---|
| `cleaned_service_operations_audit.csv` | Processed audit records |
| `cleaned_service_operations_audit.xlsx` | Excel audit workbook with embedded chart |
| `clinical_risk_chart.png` | Standalone visualization |
| `Executive_AI_Clinical_Risk_Report.pdf` | Executive-style summary report |

The actual metrics and findings depend on the input CSV data.

## Key Metrics

The pipeline calculates or reports:

- Number of records passing the downtime quality rule
- Total reported downtime hours
- Total reported patient delays
- Total parts replacement cost
- Total service/repair charges
- Service-contract values associated with valid records
- Net service yield estimate
- Maintenance expense-to-contract ratio
- Highest downtime and patient-delay records
- Count of unmatched device IDs and/or flagged downtime records

## Setup and Run

### 1. Clone the repository

```bash
git clone https://github.com/engrtalhamalik91-cmyk/Hospital-Database-Project.git
cd Hospital-Database-Project
```

If this script is stored in a different repository or folder, use that repository's URL and directory instead.

### 2. Create and activate a virtual environment (recommended)

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

macOS/Linux:

```bash
source .venv/bin/activate
```

### 3. Install dependencies

For the Pandas/NumPy implementation:

```bash
pip install pandas numpy matplotlib openpyxl reportlab
```

The standard-library CSV implementation does not require Pandas or NumPy, but it still uses Matplotlib, OpenPyXL, and ReportLab.

### 4. Add the input CSV files

Put `equipment_registry.csv` and `maintenance_failure_logs.csv` next to the script. Make sure the column names match the expected names listed above.

### 5. Run the script

Run the filename corresponding to the version you want to use. For example:

```bash
python clinical_operations_pipelinepd.py
```

Or, for the standard-library implementation:

```bash
python clinical_operations_pipeline.py
```

The filenames above should match the names in your repository. The pipeline writes its output files to the current working directory.

## Data Quality and Interpretation Notes

- The downtime rule is a simple validation rule, not a complete audit of all data quality issues.
- In the current implementations, nonnumeric values in fields other than downtime may still need additional validation, depending on the version.
- The Pandas version coerces invalid numeric values to missing values, but downstream handling should be reviewed before relying on the results.
- The service-contract calculation assumes the contract value can be summed across valid log rows. If a device has multiple maintenance logs but only one contract value, this can overcount contract value. The calculation should be adjusted to match the actual business definition.
- The chart places downtime hours and patient-delay counts on the same plot, even though they use different units. Separate charts or a clearly labeled secondary axis may be easier to interpret.
- Patient-delay counts are operational indicators; they do not establish that patients experienced clinical harm.
- The rule-based risk bands use average downtime thresholds. These thresholds are illustrative and should be validated with domain experts before operational use.
- The generated report is an analytical prototype, not a validated AI system or a clinical risk prediction model.

## Potential Improvements

- Add robust validation for every numeric input field.
- Report unmatched IDs, missing values, and invalid records separately.
- Avoid counting the same device's contract value multiple times when appropriate.
- Separate charts for downtime and patient delays.
- Add automated tests and a reproducible sample dataset.
- Refactor repeated report-generation code into reusable functions.
- Improve configuration, logging, and error messages.
- Add SQL storage and a dashboard as future learning extensions.

## Learning Outcomes

This project provides practical experience with:

- Reading and processing CSV files
- Data cleaning and identifier standardization
- Joining related datasets
- Numeric conversion and validation
- Aggregation and KPI calculations
- Visualizing operational data
- Exporting reports to CSV, Excel, and PDF
- Applying Python to a healthcare technology use case

## Author

**Muhammad Talha Malik**  
Biomedical Engineer | Healthcare Technology | Aspiring Data Analyst

- GitHub: [engrtalhamalik91-cmyk](https://github.com/engrtalhamalik91-cmyk)

## Disclaimer

This project uses operational data structures for educational and portfolio purposes. It is not intended for direct clinical use, patient-care decisions, or regulatory reporting without appropriate validation, governance, and expert review.
