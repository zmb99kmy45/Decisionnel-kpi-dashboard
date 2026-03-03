import pandas as pd

df = pd.read_csv("data/raw/procurement_kpi.csv")

print("Colonnes :")
print(df.columns)

print("\nAperçu :")
print(df.head())
