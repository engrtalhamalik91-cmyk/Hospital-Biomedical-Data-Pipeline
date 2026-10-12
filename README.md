# Hospital Biomedical Data Pipeline Automation Engine

> **Enterprise-Grade ETL Data Engineering Framework** built with Python, Pandas, NumPy, and ReportLab.

---

##  Project Overview
This project is a high-performance data analytics pipeline designed to ingest, clean, and analyze hospital medical equipment logs. It replaces manual spreadsheet work with **automated Python scripts** that process maintenance records in milliseconds using vectorized operations.

**Key Engineering Capabilities:**
*   **Ingest:** Loads raw CSV logs (Maintenance Logs & Equipment Registry).
*   **Clean:** Uses **Pandas Vectorized Operations** (SIMD) to trim whitespace and standardize IDs without slow loops.
*   **Merge:** Performs **Relational Inner Joins** to cross-reference equipment metadata with failure logs.
*   **Report:** Automatically generates 4 synchronized production outputs: CSV, Excel (Auto-sized), PNG Charts, and Executive PDF Reports.

---

## Live Visual Analytics Output
*This chart is generated automatically by the Matplotlib engine during the pipeline run:*

<img width="2000" height="900" alt="image" src="https://github.com/user-attachments/assets/a52195d8-4e9f-408a-9c69-4167c2623b19" />


---

## 🛠️ Tech Stack & Engineering Logic
*   **🐍 Python 3.x**: Core Automation Logic.
*   **🐼 Pandas & NumPy**: High-speed Data Cleaning, Type-Casting & Statistical Aggregation.
*   **📉 Matplotlib**: Data Visualization & Vector Plotting.
*   **📑 ReportLab**: Low-level Vector PDF Document Generation.
*   **📗 OpenPyXL**: Binary Excel Workbook Generation with Auto-Fit Column Scaling.

---

## 🗂️ Automated Output Artifacts
The pipeline automatically generates and freezes these files to your hard drive:

| File Type | Filename | Description |
| :--- | :--- | :--- |
| **Executive Report** | `Executive_AI_Clinical_Risk_Report.pdf` | Full vector PDF with dynamic AI-driven text interpretation. |
| **Excel Dashboard** | `cleaned_service_operations_audit.xlsx` | Auto-formatted Excel sheet with embedded charts. |
| **Visual Chart** | `clinical_risk_chart.png` | High-res risk analysis plot. |
| **Cleaned Data** | `cleaned_service_operations_audit.csv` | Raw processed dataset for DB storage. |

---

### 👤 Author
**M. Talha Malik**
*Biomedical Data Engineer & Python Developer*
