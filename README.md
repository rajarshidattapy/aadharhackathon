# UIDAI Aadhaar Data Pipeline

## Biometric Integrity & Future Authentication Risk System

**Cleaned sample dataset:**
[https://huggingface.co/datasets/mrmarvelous/aadharclean/resolve/main/merged_aadhaar_data_sample.csv](https://huggingface.co/datasets/mrmarvelous/aadharclean/resolve/main/merged_aadhaar_data_sample.csv)

---

## Overview

This repository contains a **Python-based data pipeline and analytical framework** built on UIDAI Aadhaar data to **detect future authentication failures before they occur**.

It goes beyond dashboards and retrospective stats.

**Core idea:**

> Identify districts where children are enrolled into Aadhaar but are **not completing biometric activation**, creating a **predictable wave of authentication failure** in education, welfare, and financial systems.

---

## Data Sources

The pipeline processes and merges three official UIDAI datasets:

* **Enrolment** (`api_data_aadhar_enrolment/`)
* **Demographic Authentication** (`api_data_aadhar_demographic/`)
* **Biometric Authentication** (`api_data_aadhar_biometric/`)

All datasets are aggregated at:

```
(date, state, district, pincode)
```

---

## What the Pipeline Does

### 1. Load & Clean Raw CSV Chunks

* Reads all CSV files from each dataset folder
* Strips whitespace from `state` and `district`
* Parses `date` using `dayfirst=True` (UIDAI format)
* Drops invalid dates

### 2. Deduplicate & Aggregate

* Groups by `(date, state, district, pincode)`
* Sums all numeric columns to remove duplicate records

### 3. Merge Datasets

* Performs an **outer join** across Enrolment, Demographic, and Biometric datasets
* Preserves districts even if data exists in only one dataset
* Fills missing numeric values with `0`

### 4. Output

* Writes a single merged CSV
* Prints final DataFrame shape and output path

---

## Setup

From the repository root:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

## Run the Pipeline

```bash
python -m backend.uidai_pipeline.cli \
  --enrol-dir api_data_aadhar_enrolment \
  --demo-dir api_data_aadhar_demographic \
  --bio-dir api_data_aadhar_biometric \
  --output merged_aadhaar_data.csv
```

All arguments have defaults, so this also works:

```bash
python -m backend.uidai_pipeline.cli
```

---

## Analytical Framework: Detecting Future Failure

### 1️⃣ Missing Biometric Capture Hotspots

#### Hypothesis

> Children are being enrolled but are **not returning for mandatory biometric authentication**, creating a latent failure cohort.

#### Data Used

* Enrolment: `age_0_5`
* Biometric Authentication: `bio_age_5_17`

#### Metric — **Biometric Capture Gap (BCG)**

```
BCG = Enrol_0_5 − Bio_5_17
```

**Interpretation**

* High BCG = children enrolled but biometrically inactive
* Predicts:

  * exam authentication failure
  * scholarship DBT rejection
  * SIM/bank verification issues later

This identifies failures **before they surface**.

---

### 2️⃣ Biometric Usage Suppression Index

Since modality-level data (iris vs fingerprint) is unavailable, the system detects **suppressed biometric usage**.

#### Metric — **Biometric Utilization Ratio (BUR)**

```
BUR = bio_age_5_17 / demo_age_5_17
```

(Demographic auth is the baseline because it is easier and more accessible.)

**Thresholds**

* BUR < 0.30 → biometric avoidance
* BUR < 0.15 → critical integrity risk

Low BUR typically signals:

* device malfunction
* operator avoidance
* poor capture conditions
* lack of public awareness or trust

---

### 3️⃣ Child Time Bomb — FAFI (Flagship Signal)

#### Metric — **Future Authentication Failure Index (FAFI)**

```
FAFI = Enrol_0_5 − Bio_5_17
FAFI_rate = FAFI / Enrol_0_5
```

**Interpretation**

* FAFI_rate > 0.6 → near-guaranteed failure wave in 2–5 years

**Real-world impact**

* exam entry blocks
* scholarship exclusion
* welfare authentication failures

This directly links **Aadhaar → education → welfare → exclusion**.

---

### 4️⃣ Biometric Integrity Score (BIS)

A single, explainable risk score per district.

```
BIS = w1*(normalized BCG)
    + w2*(1 − BUR)
    + w3*(FAFI_rate)
```

Scaled to **0–100**:

| BIS Range | Interpretation         |
| --------- | ---------------------- |
| 0–30      | Healthy                |
| 30–60     | Emerging risk          |
| 60–100    | Future failure hotspot |

---

## 5️⃣ Prescriptive Government Actions

For **high BIS districts**, the system recommends:

### Immediate (0–6 months)

* school-based biometric update drives
* mobile Aadhaar vans
* parent awareness campaigns

### Medium-term

* operator retraining
* device audits
* improved appointment systems

### Long-term

* predictive Aadhaar infrastructure budgeting
* biometric update reminders tied to school records

---

## Notes & Assumptions

* All CSVs must contain: `date`, `state`, `district`, `pincode`
* Numeric columns are automatically aggregated
* Invalid dates are dropped during cleaning
* Outer joins ensure no district is silently excluded
* All metrics are **transparent, explainable, and policy-safe**

---

