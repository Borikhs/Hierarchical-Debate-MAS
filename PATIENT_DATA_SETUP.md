# Patient Data Analysis Setup Guide

## Overview
The CodeWriter and CodeExecutor agents have been optimized for emergency room patient data analysis.

## What Changed

### 1. CodeWriter Agent
**Updated**: System prompt now includes complete patient_data.csv schema

**Key Improvements**:
- Full dataset schema embedded (51 columns, 17,201 rows)
- Medical data-specific coding guidelines
- Examples for common ER data analysis tasks
- Missing data handling instructions (especially initial_spo2 ~39%)
- Medical terminology and units awareness

**Schema Included**:
- Demographics: gender, age, er_year
- ER Info: er_stay_hours, entry, ems, disposition_type
- Triage: triage_level, initial_avpu
- Initial Vitals: initial_sbp, initial_dbp, initial_hr, initial_rr, initial_bt, initial_spo2
- Diagnosis: primary_dx_code, primary_dx_name, injury, num_secondary_dx, total_diagnoses
- Interventions: stroke_cp, stemi_cp, cag, transfusion, intubation, ventilator, vasopressor
- Treatment: num_medications, num_lab_tests, num_imaging_tests, num_consultations
- Vital Statistics: sbp/dbp/hr/bt/spo2 mean/max/min
- Records: num_vital_records, num_medical_records, num_initial_nursing, num_discharge_nursing

### 2. CodeExecutor Agent
**Updated**: System prompt now includes medical data execution guidelines

**Key Improvements**:
- Data file location awareness (patient_data.csv)
- Common medical data issues (missing values, data types)
- Enhanced error reporting for medical analysis
- Result formatting with medical context

## Setup Instructions

### Step 1: Copy Patient Data File

```bash
# Copy the CSV file to each group's work directory
# Replace {group_name} with actual group names (e.g., group_a, group_b)

cp /home/hyesung/multi-agent/source/data/data_for_agent/patient_data.csv \
   /path/to/work_dir/{group_name}/patient_data.csv
```

Or use this Python script:

```python
import shutil
from pathlib import Path

# Source file
source_file = Path('/home/hyesung/multi-agent/source/data/data_for_agent/patient_data.csv')

# Destination directories (adjust as needed)
work_dirs = [
    Path('./work_dir/group_a'),
    Path('./work_dir/group_b'),
    Path('./work_dir/group_c'),
]

for work_dir in work_dirs:
    work_dir.mkdir(parents=True, exist_ok=True)
    dest_file = work_dir / 'patient_data.csv'
    shutil.copy(source_file, dest_file)
    print(f"✓ Copied to {dest_file}")
```

### Step 2: Verify Data File

```python
import pandas as pd

# Test loading
df = pd.read_csv('work_dir/group_a/patient_data.csv')
print(f"Shape: {df.shape}")  # Should be (17201, 51)
print(f"Columns: {len(df.columns)}")  # Should be 51
print(f"First patient_id: {df['patient_id'].iloc[0]}")
```

### Step 3: Test with Sample Query

Example query to test the agents:

```
Analyze the average ER stay hours by triage level and gender.
Show the results in a clear table format.
```

Expected behavior:
1. **CodeWriter** will generate code like:
```python
import pandas as pd

df = pd.read_csv('patient_data.csv')

# Analyze by triage level and gender
result = df.groupby(['triage_level', 'gender'])['er_stay_hours'].agg(['mean', 'count'])
result = result.round(2)

gender_map = {0: 'Female', 1: 'Male'}
print("Average ER Stay Hours by Triage Level and Gender:")
print(result)
```

2. **CodeExecutor** will run the code and return results

3. **Analyst** will interpret the medical significance

## Schema Reference

Quick reference for the most common columns:

### Patient Demographics
- `gender`: 0=Female, 1=Male
- `age`: 0-102 years
- `er_year`: 2018-2020

### Triage & Severity
- `triage_level`: 1=Resuscitation, 2=Emergent, 3=Urgent, 4=Less urgent, 5=Non-urgent
- `initial_avpu`: 1=Alert, 2=Voice, 3=Pain, 4=Unresponsive

### Outcomes
- `er_stay_hours`: Length of stay (hours)
- `disposition_type`: 0=Normal discharge, 1=Transfer, 2=Against medical advice

### Interventions (Binary 0/1)
- `intubation`, `ventilator`, `vasopressor`
- `transfusion`, `stroke_cp`, `stemi_cp`, `cag`

### Data Quality Notes
- **Missing values**: Especially in `initial_spo2` (~39%)
- **Primary key**: `patient_id` (no duplicates)
- **Data types**: 48 numeric, 3 text columns

## Example Analysis Tasks

1. **ER Stay Analysis**
   - "What is the average ER stay by triage level?"
   - "Compare ER stay hours between genders"

2. **Intervention Analysis**
   - "What percentage of patients required intubation by triage level?"
   - "Calculate intervention rates for patients over 65"

3. **Vital Signs Analysis**
   - "Find patients with abnormal initial vitals (outside normal ranges)"
   - "Analyze blood pressure trends during ER stay"

4. **Diagnosis Analysis**
   - "What are the top 10 most common diagnoses?"
   - "Compare injury vs non-injury patient characteristics"

## Troubleshooting

### File Not Found Error
```
Error: FileNotFoundError: patient_data.csv
```
**Solution**: Copy patient_data.csv to the group's work directory

### Missing Column Error
```
Error: KeyError: 'column_name'
```
**Solution**: Check column name spelling against schema (case-sensitive)

### Missing Value Warning
```
Warning: NaN values in initial_spo2
```
**Solution**: This is expected (~39% missing). Use `.dropna()` or `.fillna()`

## Advanced Usage

### Custom Schema Location
If you want to use the full schema file:

```bash
# Schema files are available at:
/home/hyesung/multi-agent/source/data/data_for_agent/patient_data_schema_compact.txt
/home/hyesung/multi-agent/source/data/data_for_agent/patient_data_schema.txt
/home/hyesung/multi-agent/source/data/data_for_agent/patient_data_schema.json
```

### Loading Schema in Code
```python
# Read schema for reference
with open('patient_data_schema_compact.txt', 'r') as f:
    schema = f.read()
    print(schema)
```

## Next Steps

1. ✅ Copy patient_data.csv to work directories
2. ✅ Test with simple query
3. ✅ Verify agents can access and analyze data
4. ✅ Start real analysis tasks!

---

**Last Updated**: 2025-11-26
**Version**: 2.0 (Medical Data Optimized)
