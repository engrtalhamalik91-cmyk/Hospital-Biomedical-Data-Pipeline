import csv
import os
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
total_downtime_hours = 0
total_patients_impacted = 0
total_parts_cost = 0.0
total_repair_service_cost = 0.0
total_earned_service_contracts = 0.0
valid_records_processed = 0
data_corruption_leaks = 0
compiled_audit_rows = []
graph_device_ids = []
graph_downtimes = []
graph_patients = []
highest_downtime_val = 0
worst_performing_device = "N/A"
highest_patient_impact_val = 0
worst_patient_impact_device = "N/A"
registry_lookup_map = {}
with open(registry_file, mode='r', encoding='utf-8') as reg_stream:
    reg_parser = csv.DictReader(reg_stream)
    for reg_row in reg_parser:
        clean_id = reg_row["Device ID"].strip().upper()
        registry_lookup_map[clean_id] = {
            "Name": reg_row["Equipment Name"].strip(),
            "Contract": float(reg_row["Base Contract Value"].strip())
        }
with open(logs_file, mode='r', encoding='utf-8') as logs_stream:
    logs_parser = csv.DictReader(logs_stream)
    
    for log_row in logs_parser:
        raw_id = log_row.get("Device ID", "")
        clean_device_id = raw_id.strip().upper()
        
        equipment_meta = registry_lookup_map.get(clean_device_id, None)
        if equipment_meta is None:
            data_corruption_leaks += 1
            continue
            
        raw_down = log_row.get("Downtime Hours", "").strip()
        raw_patients = log_row.get("Patients Delayed", "").strip()
        raw_part = log_row.get("Part Replacement Cost", "").strip()
        raw_service = log_row.get("Service Repair Charge", "").strip()
        
        if not raw_down or int(raw_down) <= 0 or int(raw_down) > 168:
            data_corruption_leaks += 1
            status = "FAILED QUALITY AUDIT: OPERATIONAL ANOMALY"
            parsed_down, parsed_patients, parsed_part, parsed_service = 0, 0, 0.0, 0.0
        else:
            status = "OPERATIONAL PERFORMANCE MONITORED: PASSED"
            parsed_down = int(raw_down)
            parsed_patients = int(raw_patients)
            parsed_part = float(raw_part)
            parsed_service = float(raw_service)
            
            if parsed_down > highest_downtime_val:
                highest_downtime_val = parsed_down
                worst_performing_device = f"{clean_device_id} ({equipment_meta['Name']})"
                
            if parsed_patients > highest_patient_impact_val:
                highest_patient_impact_val = parsed_patients
                worst_patient_impact_device = f"{clean_device_id} ({equipment_meta['Name']})"
            
            valid_records_processed += 1
            total_downtime_hours += parsed_down
            total_patients_impacted += parsed_patients
            total_parts_cost += parsed_part
            total_repair_service_cost += parsed_service
            total_earned_service_contracts += equipment_meta["Contract"]
            
            graph_device_ids.append(clean_device_id)
            graph_downtimes.append(parsed_down)
            graph_patients.append(parsed_patients)

        processed_audit_record = {
            "Device ID": clean_device_id,
            "Equipment Name": equipment_meta["Name"],
            "Downtime (Hours)": parsed_down,
            "Patients Suffered": parsed_patients,
            "Part Replacement Cost ($)": parsed_part,
            "Direct Service Cost ($)": parsed_service,
            "Contract Portfolio Return ($)": equipment_meta["Contract"],
            "Operational Audit Status": status
        }
        compiled_audit_rows.append(processed_audit_record)

plt.figure(figsize=(10, 4.5))
plt.bar(graph_device_ids, graph_downtimes, color='crimson', alpha=0.6, label='Hardware Downtime (Hours)')
plt.plot(graph_device_ids, graph_patients, color='navy', marker='o', linewidth=2, label='Patients Suffering')
plt.xticks(rotation=45, ha='right')
plt.title('Clinical Risk Vector: Device Failures vs Healthcare Downtime Metrics', fontsize=11, fontweight='bold')
plt.grid(axis='y', linestyle='--', alpha=0.5)
plt.legend()
plt.tight_layout()
plt.savefig(output_standalone_chart, dpi=200)
plt.close()

final_headers = ["Device ID", "Equipment Name", "Downtime (Hours)", "Patients Suffered", "Part Replacement Cost ($)", "Direct Service Cost ($)", "Contract Portfolio Return ($)", "Operational Audit Status"]
with open(output_csv_file, mode='w', newline='', encoding='utf-8') as out_stream:
    writer = csv.DictWriter(out_stream, fieldnames=final_headers)
    writer.writeheader()
    writer.writerows(compiled_audit_rows)

wb = openpyxl.Workbook()
ws = wb.active
ws.title = "Operational Audit"

ws.append(final_headers)
for col_num in range(1, len(final_headers) + 1):
    ws.cell(row=1, column=col_num).font = openpyxl.styles.Font(bold=True)


for row_dict in compiled_audit_rows:
    ws.append(list(row_dict.values()))

excel_img_target = OpenpyxlImage(output_standalone_chart)
ws.add_image(excel_img_target, "J3")

for col in ws.columns:
    max_len = 0
    # Safe Coordinate Mapping: Fetching the letter directly from the first cell matrix coordinate
    col_letter = openpyxl.utils.get_column_letter(col[0].column)
    for cell in col:
        if cell.value:
            max_len = max(max_len, len(str(cell.value)))
    ws.column_dimensions[col_letter].width = max(max_len + 3, 12)

wb.save(output_excel_file)


print("[SYSTEM] Executing Live Data-Driven AI Analytical Interpretation Engine...")

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
<b>[LIVE DATA-DRIVEN AI DISPATCH DICTIONARY INTERPRETATION]</b><br/>
An active algorithmic scan of the hospital's clinical asset infrastructure reveals a system operating under an executive risk score classified as: 
<b><u>{risk_profile_status}</u></b>.<br/><br/>
<b>Operational Vitals Vector Analysis:</b> The database processed a cumulative network loss of <b>{total_downtime_hours} hours</b> of hardware disruption across <b>{valid_records_processed} authenticated medical systems</b>. This operational blockage directly disrupted treatments, forcing a severe delay vector that compromised <b>{total_patients_impacted} live patients</b>. The absolute peak operational crisis was recorded at <b>{worst_performing_device}</b>, which triggered a record maximum downtime limit spike of <b>{highest_downtime_val} hours</b> in a single logging incident. Additionally, the asset responsible for the most severe clinical treatment delay bottleneck was <b>{worst_patient_impact_device}</b>, which compromised <b>{highest_patient_impact_val} patients</b> simultaneously before engineering recovery.<br/><br/>
<b>Financial Portfolio Risk Evaluation:</b> While gross service contract assets generated a solid financial volume of <b>${total_earned_service_contracts:,.2f}</b>, hardware failure overheads extracted a direct combined strain of <b>${total_hardware_expenses:,.2f}</b> (comprising <b>${total_parts_cost:,.2f}</b> in replacement costs and <b>${total_repair_service_cost:,.2f}</b> in engineering service fees). This means that maintenance expenses have consumed exactly <b>{financial_drain_ratio:.1f}%</b> of the entire gross contract ledger return, leaving a strict net operational yield of <b>${net_service_yield:,.2f}</b>.<br/><br/>
<b>Targeted Clinical Engineering Interventions:</b><br/>
1. <b>Isolate Peak Defect Node:</b> Immediately deploy field technicians to audit <b>{worst_performing_device}</b>, as its statistical variance is the absolute highest drain on the current ward uptime KPIs.<br/>
2. <b>Mitigate Patient Vulnerability Loops:</b> Restructure backup deployment schedules specifically for <b>{worst_patient_impact_device}</b> to reduce the maximum patient disruption ceiling of <b>{highest_patient_impact_val} delays</b>.<br/>
3. <b>Enforce Data Collection Shielding:</b> The system successfully trapped and isolated <b>{data_corruption_leaks} structural data outliers (Leaks)</b> at the source interface level. Maintain current validation code profiles to block human formatting failures from corrupting standard corporate dashboards.
"""
print("[SYSTEM] Synthesizing consolidated canvas components into permanent PDF layout...")
doc = SimpleDocTemplate(output_pdf_report, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
story = []

styles = getSampleStyleSheet()


title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=16, textColor=colors.HexColor('#002B49'), spaceAfter=15, alignment=1)
header_style = ParagraphStyle('HeaderStyle', parent=styles['Heading2'], fontSize=12, textColor=colors.HexColor('#C8102E'), spaceBefore=18, spaceAfter=10, leading=16)
body_style = ParagraphStyle('BodyStyle', parent=styles['Normal'], fontSize=9, leading=14, textColor=colors.HexColor('#333333'))


ai_style = ParagraphStyle('AIStyle', parent=styles['Normal'], fontSize=9.5, leading=15, textColor=colors.HexColor('#002B49'), backColor=colors.HexColor('#F4F6F8'), borderPadding=14, borderWidth=1, borderColor=colors.HexColor('#D1D5DB'), spaceBefore=10)

story.append(Paragraph("EXECUTIVE BIOMEDICAL SERVICE & CLINICAL RISK AUDIT REPORT", title_style))
story.append(Paragraph(f"<b>Data Pipeline Profile:</b> Live Real-Time Integration &nbsp;|&nbsp; <b>Lead Analyst:</b> M. Talha Malik, BME", body_style))
story.append(Spacer(1, 15))

story.append(Paragraph("1. Systemic Core KPI Operational Parameters", header_style))
table_data = [
    ["Clinical Operational Metric Identifier", "System Output Value Parameters"],
    ["Total Validated Biomedical Devices Audited", f"{valid_records_processed} Systems Checked"],
    ["Cumulative Network Hardware Downtime", f"{total_downtime_hours} Total Hours"],
    ["Total Critical Patient Workflow Delays", f"{total_patients_impacted} Impacted Patients"],
    ["Invested Parts Replacement Cost", f"${total_parts_cost:,.2f} USD"],
    ["Direct Technical Service Fees Paid", f"${total_repair_service_cost:,.2f} USD"],
    ["Gross Earned Service Contracts Ledger", f"${total_earned_service_contracts:,.2f} USD"],
    ["Anomalous Database Outliers Intercepted", f"{data_corruption_leaks} Data Leaks Blocked"]
]

pdf_table = Table(table_data, colWidths=[260, 220])
pdf_table.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (1,0), colors.HexColor('#002B49')),
    ('TEXTCOLOR', (0,0), (1,0), colors.white),
    ('FONTNAME', (0,0), (1,0), 'Helvetica-Bold'),
    ('FONTSIZE', (0,0), (1,0), 9.5),
    ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ('TOPPADDING', (0,0), (-1,-1), 6),
    ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#F9FAFB')),
    ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E5E7EB')),
    ('FONTNAME', (0,1), (0,-1), 'Helvetica-Bold'),
    ('TEXTCOLOR', (1,1), (1,-1), colors.HexColor('#C8102E')),
]))
story.append(pdf_table)
story.append(Spacer(1, 15))

story.append(Paragraph("2. Asset Risk Matrix Visualization Chart", header_style))
story.append(Spacer(1, 5)) # Added buffer before chart image
story.append(Image(output_standalone_chart, width=480, height=216))
story.append(Spacer(1, 15))

story.append(Paragraph("3. Real-Time AI Analytical Interpretation & Engineering Insights", header_style))
story.append(Spacer(1, 5)) # 🌟 FIXED: Clear structural spacer added to force grey box away from heading!
story.append(Paragraph(dynamic_ai_interpretation, ai_style))


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
print(f"[SUCCESS] 1. Data Extractor Flat File compiled : {output_csv_file}")
print(f"[SUCCESS] 2. Workbook Frame with inside chart  : {output_excel_file}")
print(f"[SUCCESS] 3. Permanent High-Res Image Plot Chart: {output_standalone_chart}")
print(f"[SUCCESS] 4. AI Dynamic Reported Executive PDF  : {output_pdf_report}")
print("=================================================================")
print("[SUCCESS] All 4 data formats synchronized based on live records successfully!\n")

print("[SYSTEM] Synthesizing consolidated canvas components into permanent PDF layout...")
doc = SimpleDocTemplate(output_pdf_report, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
story = []

styles = getSampleStyleSheet()


title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=16, textColor=colors.HexColor('#002B49'), spaceAfter=15, alignment=1)
header_style = ParagraphStyle('HeaderStyle', parent=styles['Heading2'], fontSize=12, textColor=colors.HexColor('#C8102E'), spaceBefore=18, spaceAfter=10, leading=16)
body_style = ParagraphStyle('BodyStyle', parent=styles['Normal'], fontSize=9, leading=14, textColor=colors.HexColor('#333333'))


ai_style = ParagraphStyle('AIStyle', parent=styles['Normal'], fontSize=9.5, leading=15, textColor=colors.HexColor('#002B49'), backColor=colors.HexColor('#F4F6F8'), borderPadding=14, borderWidth=1, borderColor=colors.HexColor('#D1D5DB'), spaceBefore=10)

story.append(Paragraph("EXECUTIVE BIOMEDICAL SERVICE & CLINICAL RISK AUDIT REPORT", title_style))
story.append(Paragraph(f"<b>Data Pipeline Profile:</b> Live Real-Time Integration &nbsp;|&nbsp; <b>Lead Analyst:</b> M. Talha Malik, BME", body_style))
story.append(Spacer(1, 15))

story.append(Paragraph("1. Systemic Core KPI Operational Parameters", header_style))
table_data = [
    ["Clinical Operational Metric Identifier", "System Output Value Parameters"],
    ["Total Validated Biomedical Devices Audited", f"{valid_records_processed} Systems Checked"],
    ["Cumulative Network Hardware Downtime", f"{total_downtime_hours} Total Hours"],
    ["Total Critical Patient Workflow Delays", f"{total_patients_impacted} Impacted Patients"],
    ["Invested Parts Replacement Cost", f"${total_parts_cost:,.2f} USD"],
    ["Direct Technical Service Fees Paid", f"${total_repair_service_cost:,.2f} USD"],
    ["Gross Earned Service Contracts Ledger", f"${total_earned_service_contracts:,.2f} USD"],
    ["Anomalous Database Outliers Intercepted", f"{data_corruption_leaks} Data Leaks Blocked"]
]

pdf_table = Table(table_data, colWidths=[260, 220])
pdf_table.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (1,0), colors.HexColor('#002B49')),
    ('TEXTCOLOR', (0,0), (1,0), colors.white),
    ('FONTNAME', (0,0), (1,0), 'Helvetica-Bold'),
    ('FONTSIZE', (0,0), (1,0), 9.5),
    ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ('TOPPADDING', (0,0), (-1,-1), 6),
    ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#F9FAFB')),
    ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E5E7EB')),
    ('FONTNAME', (0,1), (0,-1), 'Helvetica-Bold'),
    ('TEXTCOLOR', (1,1), (1,-1), colors.HexColor('#C8102E')),
]))
story.append(pdf_table)
story.append(Spacer(1, 15))

story.append(Paragraph("2. Asset Risk Matrix Visualization Chart", header_style))
story.append(Spacer(1, 5)) # Added buffer before chart image
story.append(Image(output_standalone_chart, width=480, height=216))
story.append(Spacer(1, 15))

story.append(Paragraph("3. Real-Time AI Analytical Interpretation & Engineering Insights", header_style))
story.append(Spacer(1, 5)) # 🌟 FIXED: Clear structural spacer added to force grey box away from heading!
story.append(Paragraph(dynamic_ai_interpretation, ai_style))

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
print(f"[SUCCESS] 1. Data Extractor Flat File compiled : {output_csv_file}")
print(f"[SUCCESS] 2. Workbook Frame with inside chart  : {output_excel_file}")
print(f"[SUCCESS] 3. Permanent High-Res Image Plot Chart: {output_standalone_chart}")
print(f"[SUCCESS] 4. AI Dynamic Reported Executive PDF  : {output_pdf_report}")
print("=================================================================")
print("[SUCCESS] All 4 data formats synchronized based on live records successfully!\n")
