import os
import sys

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

# Import pipeline from src/
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))
from pipeline import load_prepared


def format_currency(x: float) -> str:
    if pd.isna(x):
        return "N/A"
    return f"{x:,.0f} €"


def safe_mean(series: pd.Series) -> float:
    if series is None or series.dropna().empty:
        return float("nan")
    return float(series.mean())


def main():
    st.set_page_config(page_title="Procurement KPI Dashboard", layout="wide")
    st.title("Procurement KPI Dashboard")

    # ------------------------------
    # Load data (Parquet preferred)
    # ------------------------------
    CSV_PATH = "data/raw/procurement_kpi.csv"
    PARQUET_PATH = "data/processed/procurement_processed.parquet"

    @st.cache_data
    def get_data(csv_path: str, parquet_path: str) -> pd.DataFrame:
        return load_prepared(csv_path, parquet_path)

    df = get_data(CSV_PATH, PARQUET_PATH)

    # ------------------------------
    # Sidebar filters
    # ------------------------------
    st.sidebar.header("Filters")

    supplier_options = sorted(df["Supplier"].dropna().unique().tolist())
    category_options = sorted(df["Item_Category"].dropna().unique().tolist())
    status_options = sorted(df["Order_Status"].dropna().unique().tolist())

    selected_suppliers = st.sidebar.multiselect(
        "Supplier",
        supplier_options,
        default=supplier_options,
    )

    selected_categories = st.sidebar.multiselect(
        "Item category",
        category_options,
        default=category_options,
    )

    selected_statuses = st.sidebar.multiselect(
        "Order status",
        status_options,
        default=status_options,
    )

    delivered_only = st.sidebar.checkbox(
        "Delivered only (requires Delivery_Date)",
        value=True,
    )

    # Date filter on Order_Date
    min_date = df["Order_Date"].min()
    max_date = df["Order_Date"].max()

    if pd.isna(min_date) or pd.isna(max_date):
        # If dates are missing for any reason, fallback to no date filter.
        date_range = None
    else:
        date_range = st.sidebar.date_input(
            "Order date range",
            value=(min_date.date(), max_date.date()),
            min_value=min_date.date(),
            max_value=max_date.date(),
        )

    # Base filter (context for Delivered Rate)
    base = df[
        df["Supplier"].isin(selected_suppliers)
        & df["Item_Category"].isin(selected_categories)
        & df["Order_Status"].isin(selected_statuses)
    ].copy()

    if date_range is not None:
        start_date = pd.to_datetime(date_range[0])
        end_date = pd.to_datetime(date_range[1])
        base = base[
            (base["Order_Date"] >= start_date) & (base["Order_Date"] <= end_date)
        ].copy()

    # Delivered filter (analysis set)
    if delivered_only:
        f = base[base["Is_Delivered"] & base["Delivery_Date"].notna()].copy()
    else:
        f = base.copy()

    # ------------------------------
    # KPI calculations
    # ------------------------------
    total_spend = float(f["Total_Spend"].sum()) if not f.empty else 0.0
    total_savings = float(f["Savings"].sum()) if not f.empty else 0.0

    avg_lead_delivered = safe_mean(f["Lead_Time_Days"])
    compliance_rate = safe_mean(f["Is_Compliant"]) * 100.0
    delivered_rate = safe_mean(base["Is_Delivered"]) * 100.0

    defect_rate = safe_mean(f["Defect_Rate"]) * 100.0

    # ------------------------------
    # KPI display
    # ------------------------------
    st.subheader("Key metrics")

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric("Total spend", format_currency(total_spend))
    c2.metric("Total savings", format_currency(total_savings))
    c3.metric(
        "Average lead time (delivered)",
        "N/A" if pd.isna(avg_lead_delivered) else f"{avg_lead_delivered:.1f} days",
    )
    c4.metric(
        "Compliance rate",
        "N/A" if pd.isna(compliance_rate) else f"{compliance_rate:.1f}%",
    )
    c5.metric(
        "Delivered rate", "N/A" if pd.isna(delivered_rate) else f"{delivered_rate:.1f}%"
    )
    c6.metric(
        "Average defect rate", "N/A" if pd.isna(defect_rate) else f"{defect_rate:.2f}%"
    )

    st.divider()

    # ------------------------------
    # Charts
    # ------------------------------
    left, right = st.columns(2)

    with left:
        st.subheader("Spend by supplier (top 10)")
        spend_supplier = (
            f.groupby("Supplier")["Total_Spend"]
            .sum()
            .sort_values(ascending=False)
            .head(10)
            if not f.empty
            else pd.Series(dtype=float)
        )

        fig1, ax1 = plt.subplots()
        if spend_supplier.empty:
            ax1.text(0.5, 0.5, "No data for current filters", ha="center", va="center")
            ax1.set_axis_off()
        else:
            ax1.bar(spend_supplier.index, spend_supplier.values)
            ax1.set_ylabel("Spend (€)")
            ax1.tick_params(axis="x", rotation=45)
        st.pyplot(fig1)

    with right:
        st.subheader("Average lead time by supplier (top 10)")
        lead_supplier = (
            f.groupby("Supplier")["Lead_Time_Days"]
            .mean()
            .sort_values(ascending=False)
            .head(10)
            if not f.empty
            else pd.Series(dtype=float)
        )

        fig2, ax2 = plt.subplots()
        if lead_supplier.empty:
            ax2.text(0.5, 0.5, "No data for current filters", ha="center", va="center")
            ax2.set_axis_off()
        else:
            ax2.bar(lead_supplier.index, lead_supplier.values)
            ax2.set_ylabel("Lead time (days)")
            ax2.tick_params(axis="x", rotation=45)
        st.pyplot(fig2)

    st.subheader("Monthly trend (spend and savings)")

    trend = f.copy()
    if not trend.empty and "Order_Date" in trend.columns:
        trend["Month"] = trend["Order_Date"].dt.to_period("M").dt.to_timestamp()
        trend_agg = trend.groupby("Month", as_index=False)[
            ["Total_Spend", "Savings"]
        ].sum()

        fig3, ax3 = plt.subplots()
        if trend_agg.empty:
            ax3.text(0.5, 0.5, "No data for current filters", ha="center", va="center")
            ax3.set_axis_off()
        else:
            ax3.plot(trend_agg["Month"], trend_agg["Total_Spend"], label="Spend")
            ax3.plot(trend_agg["Month"], trend_agg["Savings"], label="Savings")
            ax3.set_xlabel("Month")
            ax3.set_ylabel("€")
            ax3.legend()
        st.pyplot(fig3)
    else:
        st.write("No data for current filters.")

    st.divider()

    # ------------------------------
    # Suppliers to investigate table
    # ------------------------------
    st.subheader("Suppliers to investigate (high lead time)")

    if f.empty:
        st.write("No data for current filters.")
        table = pd.DataFrame()
    else:
        table = (
            f.groupby("Supplier")
            .agg(
                avg_lead_time=("Lead_Time_Days", "mean"),
                orders=("PO_ID", "nunique"),
                spend=("Total_Spend", "sum"),
                compliance_rate=("Is_Compliant", "mean"),
                defect_rate=("Defect_Rate", "mean"),
            )
            .reset_index()
        )

        table["avg_lead_time"] = table["avg_lead_time"].round(1)
        table["spend"] = table["spend"].round(0)
        table["compliance_rate"] = (table["compliance_rate"] * 100).round(1)
        table["defect_rate"] = (table["defect_rate"] * 100).round(2)

        table = table.sort_values("avg_lead_time", ascending=False).head(10)

        st.dataframe(table, use_container_width=True)

    if not table.empty:
        worst = table.iloc[0]
        st.caption(
            f"Insight: {worst['Supplier']} has the highest average lead time "
            f"({worst['avg_lead_time']} days) across {int(worst['orders'])} orders."
        )

    st.divider()

    # ------------------------------
    # Export
    # ------------------------------
    st.subheader("Export")

    if f.empty:
        st.write("No data to export for current filters.")
    else:
        csv_bytes = f.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Download filtered dataset (CSV)",
            data=csv_bytes,
            file_name="procurement_filtered.csv",
            mime="text/csv",
        )

    st.divider()

    # ------------------------------
    # Data quality
    # ------------------------------
    st.subheader("Data quality")

    total_rows = len(base)
    missing_global = float(base.isna().mean().mean() * 100) if total_rows > 0 else 0.0
    duplicate_rate = (
        float(base["PO_ID"].duplicated().mean() * 100) if total_rows > 0 else 0.0
    )
    rows_with_missing = (
        float(base.isna().any(axis=1).mean() * 100) if total_rows > 0 else 0.0
    )

    q1, q2, q3, q4 = st.columns(4)
    q1.metric("Rows (filtered context)", f"{total_rows:,}")
    q2.metric("Average missing rate", f"{missing_global:.2f}%")
    q3.metric("PO_ID duplicate rate", f"{duplicate_rate:.2f}%")
    q4.metric("Rows with any missing value", f"{rows_with_missing:.2f}%")

    st.markdown("Missing values by column (%)")
    missing_by_col = (base.isna().mean() * 100).round(2)
    missing_by_col = missing_by_col[missing_by_col > 0].sort_values(ascending=False)

    if missing_by_col.empty:
        st.write("No missing values detected.")
    else:
        st.dataframe(missing_by_col.rename("Missing %"), use_container_width=True)

    st.caption(
        "Note: Missing Delivery_Date (and therefore Lead_Time_Days) typically indicates orders not yet delivered. "
        "Lead time KPIs should be interpreted on delivered orders only."
    )


if __name__ == "__main__":
    main()
