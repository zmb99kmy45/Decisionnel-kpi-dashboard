import os

import pandas as pd

REQUIRED_COLUMNS = [
    "PO_ID",
    "Supplier",
    "Order_Date",
    "Delivery_Date",
    "Item_Category",
    "Order_Status",
    "Quantity",
    "Unit_Price",
    "Negotiated_Price",
    "Defective_Units",
    "Compliance",
]


def load_raw_csv(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)

    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Missing columns in dataset: {missing}")

    return df


def build_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # Convert dates
    df["Order_Date"] = pd.to_datetime(df["Order_Date"], errors="coerce")
    df["Delivery_Date"] = pd.to_datetime(df["Delivery_Date"], errors="coerce")

    # Lead time
    df["Lead_Time_Days"] = (df["Delivery_Date"] - df["Order_Date"]).dt.days
    df.loc[df["Lead_Time_Days"] < 0, "Lead_Time_Days"] = pd.NA

    # Numeric cleanup
    for col in ["Quantity", "Unit_Price", "Negotiated_Price", "Defective_Units"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Financial KPIs
    df["Total_Spend"] = df["Quantity"] * df["Negotiated_Price"]
    df["List_Spend"] = df["Quantity"] * df["Unit_Price"]
    df["Savings"] = (df["Unit_Price"] - df["Negotiated_Price"]) * df["Quantity"]
    df["Savings_Rate"] = df["Savings"] / df["List_Spend"]

    # Quality KPIs
    df["Defective_Units"] = df["Defective_Units"].fillna(0)
    df["Defect_Rate"] = df["Defective_Units"] / df["Quantity"]

    # Flags
    df["Is_Compliant"] = df["Compliance"].astype(str).str.lower().eq("yes")
    df["Is_Delivered"] = df["Order_Status"].astype(str).str.lower().eq("delivered")

    return df


def load_and_prepare(path: str) -> pd.DataFrame:
    raw = load_raw_csv(path)
    return build_features(raw)


# ==============================
# Parquet optimization
# ==============================


def build_processed_parquet(
    csv_path: str = "data/raw/procurement_kpi.csv",
    parquet_path: str = "data/processed/procurement_processed.parquet",
) -> str:

    os.makedirs("data/processed", exist_ok=True)

    df = load_and_prepare(csv_path)
    df.to_parquet(parquet_path, index=False)

    return parquet_path


def load_prepared(csv_path: str, parquet_path: str) -> pd.DataFrame:

    if os.path.exists(parquet_path):
        return pd.read_parquet(parquet_path)

    build_processed_parquet(csv_path, parquet_path)
    return pd.read_parquet(parquet_path)
