import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import openpyxl
from openpyxl.drawing.image import Image as OpenpyxlImage
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors


registry_file = "equipment_registry.csv"
logs_file = "maintenance_failure_logs.csv"

output_csv_file = "cleaned_service_operations_audit.csv"
output_excel_file = "cleaned_service_operations_audit.xlsx"
output_pdf_report = "Executive_AI_Clinical_Risk_Report.pdf"
output_standalone_chart = "clinical_risk_chart.png"


registry_df = pd.read_csv(registry_file)
logs_df = pd.read_csv(logs_file)

registry_df['Device ID'] = registry_df['Device ID'].str.strip().str.upper()
registry_df['Equipment Name'] = registry_df['Equipment Name'].str.strip()
registry_df['Base Contract Value'] = pd.to_numeric(registry_df['Base Contract Value'], errors='coerce').fillna(0.0)

logs_df['Device ID'] = logs_df['Device ID'].str.strip().str.upper()
logs_df['Downtime Hours'] = pd.to_numeric(logs_df['Downtime Hours'], errors='coerce')
logs_df['Patients Delayed'] = pd.to_numeric(logs_df['Patients Delayed'], errors='coerce')
logs_df['Part Replacement Cost'] = pd.to_numeric(logs_df['Part Replacement Cost'], errors='coerce')
logs_df['Service Repair Charge'] = pd.to_numeric(logs_df['Service Repair Charge'], errors='coerce')


data_corruption_leaks = int(logs_df['Device ID'].isin(registry_df['Device ID']).value_counts().get(False, 0))

merged_df = pd.merge(registry_df, logs_df, on='Device ID', how='inner')

merged_df['Operational Audit Status'] = np.where(
    (merged_df['Downtime Hours'].isna()) | (merged_df['Downtime Hours'] <= 0) | (merged_df['Downtime Hours'] > 168),
    "FAILED QUALITY AUDIT: OPERATIONAL ANOMALY",
    "OPERATIONAL PERFORMANCE MONITORED: PASSED"
)

merged_df['Downtime Hours'] = np.where(merged_df['Operational Audit Status'].str.contains("FAILED"), 0, merged_df['Downtime Hours']).astype(int)
merged_df['Patients Delayed'] = np.where(merged_df['Operational Audit Status'].str.contains("FAILED"), 0, merged_df['Patients Delayed']).astype(int)
merged_df['Part Replacement Cost'] = np.where(merged_df['Operational Audit Status'].str.contains("FAILED"), 0.0, merged_df['Part Replacement Cost'])
merged_df['Service Repair Charge'] = np.where(merged_df['Operational Audit Status'].str.contains("FAILED"), 0.0, merged_df['Service Repair Charge'])


valid_records_processed = int(merged_df[merged_df['Operational Audit Status'].str.contains("PASSED")].shape[0])
total_downtime_hours = int(merged_df['Downtime Hours'].sum())
total_patients_impacted = int(merged_df['Patients Delayed'].sum())
total_parts_cost = float(merged_df['Part Replacement Cost'].sum())
total_repair_service_cost = float(merged_df['Service Repair Charge'].sum())
total_earned_service_contracts = float(merged_df[merged_df['Operational Audit Status'].str.contains("PASSED")]['Base Contract Value'].sum())


if valid_records_processed > 0:
    worst_down_row = merged_df.loc[merged_df['Downtime Hours'].idxmax()]
    highest_downtime_val = int(worst_down_row['Downtime Hours'])
    worst_performing_device = f"{worst_down_row['Device ID']} ({worst_down_row['Equipment Name']})"
    
    worst_patient_row = merged_df.loc[merged_df['Patients Delayed'].idxmax()]
    highest_patient_impact_val = int(worst_patient_row['Patients Delayed'])
    worst_patient_impact_device = f"{worst_patient_row['Device ID']} ({worst_patient_row['Equipment Name']})"
else:
    highest_downtime_val, worst_performing_device = 0, "N/A"
    highest_patient_impact_val, worst_patient_impact_device = 0, "N/A"


final_headers = ["Device ID", "Equipment Name", "Downtime (Hours)", "Patients Suffered", "Part Replacement Cost ($)", "Direct Service Cost ($)", "Contract Portfolio Return ($)", "Operational Audit Status"]
export_df = merged_df.rename(columns={
    "Downtime Hours": "Downtime (Hours)",
    "Patients Delayed": "Patients Suffered",
    "Part Replacement Cost": "Part Replacement Cost ($)",
    "Service Repair Charge": "Direct Service Cost ($)",
    "Base Contract Value": "Contract Portfolio Return ($)"
})[final_headers]


passed_df = merged_df[merged_df['Operational Audit Status'].str.contains("PASSED")]

plt.figure(figsize=(10, 4.5))
plt.bar(passed_df['Device ID'], passed_df['Downtime Hours'], color='crimson', alpha=0.6, label='Hardware Downtime (Hours)')
plt.plot(passed_df['Device ID'], passed_df['Patients Delayed'], color='navy', marker='o', linewidth=2, label='Patients Suffering')
plt.xticks(rotation=45, ha='right')
plt.title('Clinical Risk Vector: Device Failures vs Healthcare Downtime Metrics', fontsize=11, fontweight='bold')
plt.grid(axis='y', linestyle='--', alpha=0.5)
plt.legend()
plt.tight_layout()
plt.savefig(output_standalone_chart, dpi=200)
plt.close()


export_df.to_csv(output_csv_file, index=False)


export_df.to_excel(output_excel_file, index=False, sheet_name="Operational Audit")

wb = openpyxl.load_workbook(output_excel_file)
ws = wb["Operational Audit"]

for col_num in range(1, len(final_headers) + 1):
    ws.cell(row=1, column=col_num).font = openpyxl.styles.Font(bold=True)

excel_img_target = OpenpyxlImage(output_standalone_chart)
ws.add_image(excel_img_target, "J3")


for col in ws.columns:
    max_len = max(len(str(cell.value or '')) for cell in col)
    col_letter = openpyxl.utils.get_column_letter(col[0].column)
    ws.column_dimensions[col_letter].width = max(max_len + 3, 12)

wb.save(output_excel_file)


avg_downtime_per_device = total_downtime_hours / valid_records_processed if valid_records_processed > 0 else 0
total_hardware_expenses = total_parts_cost + total_repair_service_cost
net_service_yield = total_earned_service_contracts - total_hardware_expenses
financial_drain_ratio = (total_hardware_expenses / total_earned_service_contracts) * 100 if total_earned_service_contracts > 0 else 0

risk_profile_status = "STABLE OPERATIONAL RANGE"
if avg_downtime_per_device > 40:
    risk_profile_status = "CRITICAL RISK PROFILE: HIGH WORKFLOW VOLATILITY DETECTED"
elif avg_downtime_per_device > 20:
    risk_profile_status = "ELEVATED RISK STATUS: REQUIRING MONITORING ADJUSTMENTS"

dynamic_ai_interpretation = f"""
[LIVE DATA-DRIVEN AI DISPATCH DICTIONARY INTERPRETATION]
An active algorithmic scan of the hospital's clinical asset infrastructure reveals a system operating under an executive risk score classified as: {risk_profile_status}.

Operational Vitals Vector Analysis: The database processed a cumulative network loss of {total_downtime_hours} hours of hardware disruption across {valid_records_processed} authenticated medical systems. This operational blockage directly disrupted treatments, forcing a severe delay vector that compromised {total_patients_impacted} live patients. The absolute peak operational crisis was recorded at {worst_performing_device}, which triggered a record maximum downtime limit spike of {highest_downtime_val} hours in a single logging incident. Additionally, the asset responsible for the most severe clinical treatment delay bottleneck was {worst_patient_impact_device}, which compromised {highest_patient_impact_val} patients simultaneously before engineering recovery.

Financial Portfolio Risk Evaluation: While gross service contract assets generated a solid financial volume of ${total_earned_service_contracts:,.2f}, hardware failure overheads extracted a direct combined strain of ${total_hardware_expenses:,.2f} (comprising ${total_parts_cost:,.2f} in replacement costs and ${total_repair_service_cost:,.2f} in engineering service fees). This means that maintenance expenses have consumed exactly {financial_drain_ratio:.1f}% of the entire gross contract ledger return, leaving a strict net operational yield of ${net_service_yield:,.2f}.

Targeted Clinical Engineering Interventions:
1. Isolate Peak Defect Node: Immediately deploy field technicians to audit {worst_performing_device}, as its statistical variance is the absolute highest drain on the current ward uptime KPIs.
2. Mitigate Patient Vulnerability Loops: Restructure backup deployment schedules specifically for {worst_patient_impact_device} to reduce the maximum patient disruption ceiling of {highest_patient_impact_val} delays.
3. Enforce Data Collection Shielding: The system successfully trapped and isolated {data_corruption_leaks} structural data outliers (Leaks) at the source interface level. Maintain current validation code profiles to block human formatting failures from corrupting standard corporate dashboards.
"""

doc = SimpleDocTemplate(output_pdf_report, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
story = []
styles = getSampleStyleSheet()
title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=15, textColor=colors.HexColor('#002B49'), spaceAfter=12, alignment=1)
header_style = ParagraphStyle('HeaderStyle', parent=styles['Heading2'], fontSize=11, textColor=colors.HexColor('#C8102E'), spaceBefore=15, spaceAfter=8, leading=14)
body_style = ParagraphStyle('BodyStyle', parent=styles['Normal'], fontSize=9, leading=13, textColor=colors.HexColor('#333333'))
ai_style = ParagraphStyle('AIStyle', parent=styles['Normal'], fontSize=9, leading=14, textColor=colors.HexColor('#002B49'), backColor=colors.HexColor('#F4F6F8'), borderPadding=12, borderWidth=0.5, borderColor=colors.HexColor('#D1D5DB'), spaceBefore=8)
story.append(Paragraph("EXECUTIVE BIOMEDICAL SERVICE & CLINICAL RISK AUDIT REPORT", title_style))
story.append(Paragraph(f"Data Pipeline Profile: Live Real-Time Integration  |  Lead Analyst: M. Talha Malik, BME", body_style))
story.append(Spacer(1, 12))
story.append(Paragraph("1. Systemic Core KPI Operational Parameters", header_style))
table_rows = [
["Clinical Operational Metric Identifier", "System Output Value Parameters"],
["Total Validated Biomedical Devices Audited", f"{valid_records_processed} Systems Checked"],
["Cumulative Network Hardware Downtime", f"{total_downtime_hours} Total Hours"],
["Total Critical Patient Workflow Delays", f"{total_patients_impacted} Impacted Patients"],
["Invested Parts Replacement Cost", f"${total_parts_cost:,.2f} USD"],
["Direct Technical Service Fees Paid", f"${total_repair_service_cost:,.2f} USD"],
["Gross Earned Service Contracts Ledger", f"${total_earned_service_contracts:,.2f} USD"],
["Anomalous Database Outliers Intercepted", f"{data_corruption_leaks} Data Leaks Blocked"]
]


pdf_table = Table(table_rows, colWidths=[260, 220])
pdf_table.setStyle(TableStyle([
('BACKGROUND', (0,0), (1,0), colors.HexColor('#002B49')),
('TEXTCOLOR', (0,0), (1,0), colors.white),
('FONTNAME', (0,0), (1,0), 'Helvetica-Bold'),
('FONTSIZE', (0,0), (1,0), 9.5),
('BOTTOMPADDING', (0,0), (-1,-1), 5),
('TOPPADDING', (0,0), (-1,-1), 5),
('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#F9FAFB')),
('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E5E7EB')),
('FONTNAME', (0,1), (0,-1), 'Helvetica-Bold'),
('TEXTCOLOR', (1,1), (1,-1), colors.HexColor('#C8102E')),
]))
story.append(pdf_table)
story.append(Spacer(1, 12))
story.append(Paragraph("2. Asset Risk Matrix Visualization Chart", header_style))
story.append(Spacer(1, 4))
story.append(Image(output_standalone_chart, width=480, height=216))
story.append(Spacer(1, 12))
story.append(Paragraph("3. Real-Time AI Analytical Interpretation & Engineering Insights", header_style))
story.append(Spacer(1, 4))
story.append(Paragraph(dynamic_ai_interpretation.replace('\n', ''), ai_style))



doc.build(story)

print("\n" + "="*65)
print("       HOSPITAL BIOMEDICAL SERVICE & RISK AUDIT DASHBOARD        ")
print("="*65)
print(f"Total Operational Devices Audited     : {valid_records_processed} Systems")
print(f"Total Cumulative Hardware Downtime    : {total_downtime_hours} Hours")
print(f"Total Critical Patient Delays Suffered: {total_patients_impacted} Patients")
print(f"Total Invested Parts Replacement Cost : ${total_parts_cost:,.2f}")
print(f"Total Direct Technical Service Fees   : ${total_repair_service_cost:,.2f}")
print(f"Total Gross Earned Service Contracts  : ${total_earned_service_contracts:,.2f}")
print(f"Anomalous Operational Data Leaks Blocked: {data_corruption_leaks} Outliers")
print("="*65)
print(f"[PANDAS PIPELINE SUCCESS] 1. Data Extractor Flat File compiled : {output_csv_file}")
print(f"[PANDAS PIPELINE SUCCESS] 2. Workbook Frame with inside chart  : {output_excel_file}")
print(f"[PANDAS PIPELINE SUCCESS] 3. Permanent High-Res Image Plot Chart: {output_standalone_chart}")
print(f"[PANDAS PIPELINE SUCCESS] 4. AI Dynamic Reported Executive PDF  : {output_pdf_report}")
print("=================================================================")
print("[SUCCESS] All 4 data formats synchronized based on live records successfully!\n")