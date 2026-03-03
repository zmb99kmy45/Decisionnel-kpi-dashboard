from pipeline import load_and_prepare

CSV_PATH = "data/raw/procurement_kpi.csv"

df = load_and_prepare(CSV_PATH)
print(
    df[
        ["Lead_Time_Days", "Total_Spend", "Savings", "Defect_Rate", "Is_Compliant"]
    ].head()
)
print(df.shape)
