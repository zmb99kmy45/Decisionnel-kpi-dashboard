# Procurement KPI Dashboard

## Project Overview

This project demonstrates my ability to transform raw operational data into a structured decision-support dashboard.

Using a public Procurement KPI dataset (Kaggle), I built an end-to-end analytics workflow including:

* Data cleaning & feature engineering
* KPI structuring and business logic definition
* Operational and financial performance tracking
* Data quality monitoring
* Interactive dashboard development (Streamlit + Matplotlib)

The objective is to simulate a real-world procurement performance monitoring tool used by Operations and Finance teams.

---

## Key Performance Indicators (KPIs)

### Financial KPIs

* **Total Spend** = Quantity × Negotiated Price
* **Total Savings** = (Unit Price − Negotiated Price) × Quantity
* **Savings Rate**
* Spend by Supplier
* Spend by Category

### Operational KPIs

* **Average Lead Time (Delivered only)**
  → Calculated only on delivered orders to avoid bias
* Delivered Rate (%)
* Lead Time by Supplier

### Quality & Compliance KPIs

* Compliance Rate (%)
* Defect Rate (%)
* Top Suppliers requiring investigation (high lead time)

---

## Data Quality Monitoring

Data quality checks are integrated directly into the dashboard:

* Total number of records
* Global missing value rate
* Duplicate PO_ID rate
* Missing values by column

### Interpretation

Missing values are primarily observed in:

* `Delivery_Date`
* `Lead_Time_Days`

These correspond to orders not yet delivered.
Lead time is therefore calculated **only on delivered orders**, ensuring business-relevant KPIs.

---

## Technical Stack

* Python
* Pandas
* Streamlit
* Matplotlib
* Feature engineering pipeline (`pipeline.py`)
* Kaggle dataset (Procurement KPI Analysis Dataset)

---

## How to Run

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app/app.py
```

---

## What This Project Demonstrates

* Translation of business needs into measurable KPIs
* Decision-oriented modeling
* Robust data cleaning & feature engineering
* Operational performance monitoring
* Embedded data governance logic
* End-to-end dashboard delivery

---

