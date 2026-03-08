# Aadhar Data - Visualization Guide

## Overview

This dataset contains Aadhar (Indian unique identification) registration and authentication data across three main categories: **Biometric Authentication**, **Demographic Authentication**, and **Enrolment Statistics**. The data spans March 2025 and covers all Indian states and union territories.

---

## Dataset Summary

| Dataset | Records | Files | Date Range | Geographic Coverage |
|---------|---------|-------|------------|---------------------|
| **Biometric Authentication** | 1,861,108 | 4 CSV files | March 2025 | Pan-India (36 states/UTs) |
| **Demographic Authentication** | 2,071,700 | 5 CSV files | March 2025 | Pan-India (36 states/UTs) |
| **Enrolment** | 1,006,029 | 3 CSV files | March 2025 | Pan-India (36 states/UTs) |
| **Total** | **4,938,837** | **12 CSV files** | March 2025 | **Pan-India** |

---

## Data Structure

### 1. Biometric Authentication Data
**Location:** `data/api_data_aadhar_biometric/`

**Schema:**
| Column | Type | Description |
|--------|------|-------------|
| `date` | Date (DD-MM-YYYY) | Transaction date |
| `state` | String | Indian state or union territory |
| `district` | String | District within the state |
| `pincode` | Integer | 6-digit postal code |
| `bio_age_5_17` | Integer | Biometric authentications for age group 5-17 years |
| `bio_age_17_` | Integer | Biometric authentications for age group 18+ years |

**Files:**
- `api_data_aadhar_biometric_0_500000.csv` (500,000 records)
- `api_data_aadhar_biometric_500000_1000000.csv` (500,000 records)
- `api_data_aadhar_biometric_1000000_1500000.csv` (500,000 records)
- `api_data_aadhar_biometric_1500000_1861108.csv` (361,108 records)

**Sample Data:**
```
01-03-2025,Haryana,Mahendragarh,123029,280,577
01-03-2025,Bihar,Madhepura,852121,144,369
01-03-2025,Tamil Nadu,Madurai,625514,271,815
```

---

### 2. Demographic Authentication Data
**Location:** `data/api_data_aadhar_demographic/`

**Schema:**
| Column | Type | Description |
|--------|------|-------------|
| `date` | Date (DD-MM-YYYY) | Transaction date |
| `state` | String | Indian state or union territory |
| `district` | String | District within the state |
| `pincode` | Integer | 6-digit postal code |
| `demo_age_5_17` | Integer | Demographic authentications for age group 5-17 years |
| `demo_age_17_` | Integer | Demographic authentications for age group 18+ years |

**Files:**
- `api_data_aadhar_demographic_0_500000.csv` (500,000 records)
- `api_data_aadhar_demographic_500000_1000000.csv` (500,000 records)
- `api_data_aadhar_demographic_1000000_1500000.csv` (500,000 records)
- `api_data_aadhar_demographic_1500000_2000000.csv` (500,000 records)
- `api_data_aadhar_demographic_2000000_2071700.csv` (71,700 records)

**Sample Data:**
```
01-03-2025,Uttar Pradesh,Gorakhpur,273213,49,529
01-03-2025,Andhra Pradesh,Chittoor,517132,22,375
01-03-2025,Gujarat,Rajkot,360006,65,765
```

---

### 3. Enrolment Data
**Location:** `data/api_data_aadhar_enrolment/`

**Schema:**
| Column | Type | Description |
|--------|------|-------------|
| `date` | Date (DD-MM-YYYY) | Enrolment date |
| `state` | String | Indian state or union territory |
| `district` | String | District within the state |
| `pincode` | Integer | 6-digit postal code |
| `age_0_5` | Integer | New enrolments for age group 0-5 years |
| `age_5_17` | Integer | New enrolments for age group 5-17 years |
| `age_18_greater` | Integer | New enrolments for age group 18+ years |

**Files:**
- `api_data_aadhar_enrolment_0_500000.csv` (500,000 records)
- `api_data_aadhar_enrolment_500000_1000000.csv` (500,000 records)
- `api_data_aadhar_enrolment_1000000_1006029.csv` (6,029 records)

**Sample Data:**
```
02-03-2025,Meghalaya,East Khasi Hills,793121,11,61,37
09-03-2025,Karnataka,Bengaluru Urban,560043,14,33,39
09-03-2025,Uttar Pradesh,Kanpur Nagar,208001,29,82,12
```

---

## Geographic Coverage

### States and Union Territories (36 total):
- Andhra Pradesh
- Assam
- Bihar
- Chandigarh
- Chhattisgarh
- Delhi
- Goa
- Gujarat
- Haryana
- Himachal Pradesh
- Jammu and Kashmir
- Jharkhand
- Karnataka
- Kerala
- Madhya Pradesh
- Maharashtra
- Manipur
- Meghalaya
- Nagaland
- Odisha/Orissa
- Pondicherry/Puducherry
- Punjab
- Rajasthan
- Sikkim
- Tamil Nadu
- Telangana
- Uttar Pradesh
- Uttarakhand
- West Bengal
- *(and more)*

---

## Data Visualization Opportunities

### 1. **Time-Series Analysis**
- Daily/weekly trends in authentication requests
- Enrolment patterns over time
- Peak usage hours/days identification

### 2. **Geographic Visualizations**

#### State-Level Analysis
- **Choropleth Maps:** Show authentication density by state
- **Heat Maps:** Identify high-activity regions
- **Bar Charts:** Compare states by total authentications

#### District-Level Analysis
- **Detailed Maps:** District-wise breakdown
- **Top Districts:** Rankings by authentication volume
- **Rural vs Urban:** Pincode-based analysis

### 3. **Age Group Analysis**
- **Stacked Bar Charts:** Age distribution across states
- **Pie Charts:** Proportion of authentications by age group
- **Line Charts:** Age group trends over time

**Age Groups:**
- **Enrolment:** 0-5 years, 5-17 years, 18+ years
- **Authentication:** 5-17 years, 18+ years

### 4. **Authentication Type Comparison**
- **Biometric vs Demographic:** Comparative analysis
- **Preference Patterns:** Which authentication method is preferred by region
- **Dual Charts:** Side-by-side comparison by state/district

### 5. **Pincode-Level Insights**
- **Granular Heat Maps:** Detailed location-based activity
- **Urban Clusters:** Identify major urban authentication centers
- **Coverage Maps:** Areas with high/low Aadhar usage

### 6. **Statistical Dashboards**

#### Key Metrics:
- Total authentications (by type, age, region)
- Average daily authentications
- New enrolments by age group
- Growth rate calculations
- State-wise penetration rates

#### Visualizations:
- **KPI Cards:** Summary statistics
- **Gauge Charts:** Performance indicators
- **Trend Lines:** Growth trajectories
- **Comparison Tables:** State rankings

### 7. **Correlation Analysis**
- Relationship between enrolment and authentication rates
- Demographic vs biometric authentication patterns
- Age group preferences by region
- Temporal patterns (weekday vs weekend)

### 8. **Regional Deep Dives**

#### Focus Areas:
- **High-Volume States:** Uttar Pradesh, Bihar, Maharashtra, Karnataka
- **Metropolitan Centers:** Delhi, Mumbai, Bengaluru, Chennai
- **Rural Regions:** District-level rural analysis
- **Special Territories:** Union territories analysis

### 9. **Performance Metrics**
- Authentication success indicators
- Service adoption rates
- Regional coverage gaps
- Age group engagement levels

---

## Data Processing Recommendations

### 1. **Data Loading Strategy**
```python
# For large datasets, use chunking
import pandas as pd

def load_dataset(file_pattern, chunksize=50000):
    """Load large CSV files in chunks"""
    chunks = []
    for file in glob.glob(file_pattern):
        for chunk in pd.read_csv(file, chunksize=chunksize):
            chunks.append(chunk)
    return pd.concat(chunks, ignore_index=True)
```

### 2. **Data Cleaning Steps**
- Convert date strings to datetime objects
- Standardize state names (handle Orissa/Odisha, Pondicherry/Puducherry)
- Handle missing values
- Validate pincode format (6 digits)
- Remove duplicate records

### 3. **Aggregation Strategies**
- **Daily aggregates:** Sum by date
- **State-level:** Group by state
- **District-level:** Group by state + district
- **Age-based:** Sum age group columns
- **Multi-level:** Combine dimensions (state + age + type)

### 4. **Derived Metrics**
```python
# Calculate total authentications
df['total_bio'] = df['bio_age_5_17'] + df['bio_age_17_']
df['total_demo'] = df['demo_age_5_17'] + df['demo_age_17_']
df['total_enrol'] = df['age_0_5'] + df['age_5_17'] + df['age_18_greater']

# Authentication ratio
df['bio_demo_ratio'] = df['total_bio'] / df['total_demo']

# Youth percentage
df['youth_percentage'] = (df['age_5_17'] / df['total_enrol']) * 100
```

---

## Visualization Tools Recommendations

### Python Libraries
- **Pandas:** Data manipulation and analysis
- **Matplotlib/Seaborn:** Static visualizations
- **Plotly:** Interactive charts and dashboards
- **Folium/Geopandas:** Geographic visualizations
- **Dash/Streamlit:** Web dashboards

### Example Visualizations

#### 1. State-wise Authentication Heat Map
```python
import plotly.express as px

state_totals = df.groupby('state').agg({
    'bio_age_5_17': 'sum',
    'bio_age_17_': 'sum'
}).reset_index()
state_totals['total'] = state_totals['bio_age_5_17'] + state_totals['bio_age_17_']

fig = px.bar(state_totals, x='state', y='total', 
             title='Total Biometric Authentications by State')
fig.show()
```

#### 2. Time Series Analysis
```python
import matplotlib.pyplot as plt

df['date'] = pd.to_datetime(df['date'], format='%d-%m-%Y')
daily_trend = df.groupby('date')['total_bio'].sum()

plt.figure(figsize=(12, 6))
plt.plot(daily_trend.index, daily_trend.values)
plt.title('Daily Biometric Authentication Trend')
plt.xlabel('Date')
plt.ylabel('Total Authentications')
plt.xticks(rotation=45)
plt.show()
```

#### 3. Age Distribution
```python
age_data = {
    'Age Group': ['0-5', '5-17', '18+'],
    'Enrolments': [
        df['age_0_5'].sum(),
        df['age_5_17'].sum(),
        df['age_18_greater'].sum()
    ]
}

fig = px.pie(age_data, values='Enrolments', names='Age Group',
             title='Enrolment Distribution by Age Group')
fig.show()
```

---

## Data Quality Notes

### Considerations:
1. **Date Format:** Consistent DD-MM-YYYY format
2. **State Names:** Minor variations exist (Orissa/Odisha, Pondicherry/Puducherry)
3. **Missing Age Labels:** Column names appear truncated (e.g., `bio_age_17_` likely means 18+)
4. **File Splits:** Data is split by row ranges for easier handling
5. **Numeric Fields:** All count fields are integers

### Validation Checks:
- ✅ No null values expected in key fields
- ✅ All pincodes should be 6 digits
- ✅ All counts should be non-negative
- ✅ Date range should be within March 2025

---

## Quick Start Dashboard Ideas

### Dashboard 1: **Executive Summary**
- Total authentications (all types)
- Daily/weekly trends
- Top 10 states by volume
- Age distribution pie chart

### Dashboard 2: **Geographic Analysis**
- India map with state-level heat map
- District rankings
- Urban vs rural comparison
- Regional penetration rates

### Dashboard 3: **Authentication Insights**
- Biometric vs demographic split
- Age-based preferences
- Peak activity times
- Growth trajectories

### Dashboard 4: **Enrolment Tracker**
- New registrations by age
- State-wise enrolment rates
- Trend analysis
- Coverage gaps identification

---

## File Size and Performance Notes

- **Total Dataset Size:** ~5 million records
- **Memory Requirements:** Estimated 500MB-1GB RAM for full dataset
- **Processing:** Consider chunking for large-scale analysis
- **Indexing:** Create indexes on `state`, `district`, and `date` for faster queries

---

## Data Update Frequency

Based on file naming and date ranges, this appears to be **daily data** collected throughout **March 2025**. For ongoing analysis:
- Monitor for new files
- Aggregate historical data
- Maintain incremental processing pipelines

---

## Contact & Support

For questions about data structure or visualization approaches, refer to this documentation or consult the data engineering team.

---

**Last Updated:** January 19, 2026  
**Data Period:** March 2025  
**Version:** 1.0
