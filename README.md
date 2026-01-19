# UIDAI Aadhaar Data Pipeline

This repository contains a small Python pipeline to clean and merge the three UIDAI Aadhaar datasets:

- Enrolment (`api_data_aadhar_enrolment/`)
- Demographic (`api_data_aadhar_demographic/`)
- Biometric (`api_data_aadhar_biometric/`)

## What the script does

1. **Load CSV chunks** from each of the three folders.
2. **Clean each dataset separately**:
   - Strip whitespace from `state` and `district`.
   - Parse `date` with `dayfirst=True`.
   - Group by `(date, state, district, pincode)` and **sum numeric columns** to deduplicate.
3. **Merge the three cleaned datasets** on `(date, state, district, pincode)` using an **outer** join.
4. **Fill missing numeric values** with `0`.
5. **Write the final merged dataset** to a CSV file.

## Setup

From the repository root:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run the pipeline

From the repository root, run:

```bash
python -m uidai_pipeline.cli \
  --enrol-dir api_data_aadhar_enrolment \
  --demo-dir api_data_aadhar_demographic \
  --bio-dir api_data_aadhar_biometric \
  --output merged_aadhaar_data.csv
```

All arguments have sensible defaults, so this is equivalent to:

```bash
python -m uidai_pipeline.cli
```

The script will print the final DataFrame shape and the output file path.

## Notes

- The script assumes each CSV has at least these columns: `date`, `state`, `district`, `pincode`, plus one or more numeric columns to aggregate.
- Date parsing uses `dayfirst=True` as per UIDAI formats, and invalid dates are dropped during cleaning.
- The outer join ensures that if a `(date, state, district, pincode)` combination appears in only one dataset, it is still preserved in the final output, with missing numeric values filled as `0`.

