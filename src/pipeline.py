from __future__ import annotations

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
    """Load raw procurement CSV and validate expected columns."""
    df = pd.read_csv(path)

    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Missing columns in dataset: {missing}")

    return df


def build_features(df: pd.DataFrame) -> pd.DataFrame:
    """Clean data types and create decision-support features/KPIs."""
    out = df.copy()

    # Dates
    out["Order_Date"] = pd.to_datetime(out["Order_Date"], errors="coerce")
    out["Delivery_Date"] = pd.to_datetime(out["Delivery_Date"], errors="coerce")

    # Core features
    out["Lead_Time_Days"] = (out["Delivery_Date"] - out["Order_Date"]).dt.days

    # Numerical hygiene
    for col in ["Quantity", "Unit_Price", "Negotiated_Price", "Defective_Units"]:
        out[col] = pd.to_numeric(out[col], errors="coerce")

    # Financial KPIs
    out["Total_Spend"] = out["Quantity"] * out["Negotiated_Price"]
    out["List_Spend"] = out["Quantity"] * out["Unit_Price"]
    out["Savings"] = (out["Unit_Price"] - out["Negotiated_Price"]) * out["Quantity"]
    out["Savings_Rate"] = out["Savings"] / out["List_Spend"]

    # Quality KPIs
    out["Defective_Units"] = out["Defective_Units"].fillna(0)
    out["Defect_Rate"] = out["Defective_Units"] / out["Quantity"]

    # Compliance (Yes/No -> boolean)
    out["Is_Compliant"] = (
        out["Compliance"].astype(str).str.strip().str.lower().eq("yes")
    )

    # Delivered flag
    out["Is_Delivered"] = (
        out["Order_Status"].astype(str).str.strip().str.lower().eq("delivered")
    )

    # Cleanup: avoid inf values from division by 0
    out["Savings_Rate"] = out["Savings_Rate"].replace(
        [pd.NA, float("inf"), float("-inf")], pd.NA
    )
    out["Defect_Rate"] = out["Defect_Rate"].replace(
        [pd.NA, float("inf"), float("-inf")], pd.NA
    )

    return out


def load_and_prepare(path: str) -> pd.DataFrame:
    """Convenience function: load raw CSV + build features."""
    raw = load_raw_csv(path)
    clean = build_features(raw)
    return clean


def export_processed(
    df: pd.DataFrame, out_path: str = "data/processed/procurement_processed.parquet"
) -> str:
    """Export processed dataset for faster loading in Streamlit."""
    import os

    os.makedirs("data/processed", exist_ok=True)
    df.to_parquet(out_path, index=False)
    return out_path
