import os
import sys

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

# Import pipeline
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))
from pipeline import load_and_prepare


def main():
    st.set_page_config(page_title="Procurement KPI Dashboard", layout="wide")
    st.title("Procurement KPI Dashboard")

    # ==============================
    # LOAD DATA
    # ==============================

    CSV_PATH = "data/raw/procurement_kpi.csv"
    df = load_and_prepare(CSV_PATH)

    # ==============================
    # SIDEBAR FILTERS
    # ==============================

    st.sidebar.header("Filtres")

    suppliers = st.sidebar.multiselect(
        "Supplier",
        sorted(df["Supplier"].unique()),
        default=sorted(df["Supplier"].unique()),
    )

    categories = st.sidebar.multiselect(
        "Item Category",
        sorted(df["Item_Category"].unique()),
        default=sorted(df["Item_Category"].unique()),
    )

    delivered_only = st.sidebar.checkbox(
        "Delivered only (avec Delivery_Date)", value=True
    )

    # Base filter
    base = df[
        (df["Supplier"].isin(suppliers)) & (df["Item_Category"].isin(categories))
    ].copy()

    # Delivered filter
    if delivered_only:
        f = base[base["Is_Delivered"] & base["Delivery_Date"].notna()].copy()
    else:
        f = base.copy()

    # ==============================
    # KPIs
    # ==============================

    total_spend = f["Total_Spend"].sum()
    total_savings = f["Savings"].sum()
    avg_lead = f["Lead_Time_Days"].mean()
    compliance_rate = f["Is_Compliant"].mean() * 100
    delivered_rate = base["Is_Delivered"].mean() * 100

    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric("Spend total (€)", f"{total_spend:,.0f}")
    col2.metric("Savings total (€)", f"{total_savings:,.0f}")
    col3.metric("Lead Time moyen (Delivered)", f"{avg_lead:.1f}")
    col4.metric("Compliance (%)", f"{compliance_rate:.1f}")
    col5.metric("Delivered rate (%)", f"{delivered_rate:.1f}")

    st.divider()

    # ==============================
    # CHART 1 - Spend par fournisseur
    # ==============================

    st.subheader("Spend per supplier")

    spend_supplier = (
        f.groupby("Supplier")["Total_Spend"].sum().sort_values(ascending=False).head(10)
    )

    fig1, ax1 = plt.subplots()
    ax1.bar(spend_supplier.index, spend_supplier.values)
    ax1.set_ylabel("Spend (€)")
    ax1.tick_params(axis="x", rotation=45)
    st.pyplot(fig1)

    # ==============================
    # CHART 2 - Lead time par fournisseur
    # ==============================

    st.subheader("Average lead time per supplier")

    lead_supplier = (
        f.groupby("Supplier")["Lead_Time_Days"]
        .mean()
        .sort_values(ascending=False)
        .head(10)
    )

    fig2, ax2 = plt.subplots()
    ax2.bar(lead_supplier.index, lead_supplier.values)
    ax2.set_ylabel("Lead Time (jours)")
    ax2.tick_params(axis="x", rotation=45)
    st.pyplot(fig2)

    # ==============================
    # TABLE - Fournisseurs à investiguer
    # ==============================

    st.subheader("Top suppliers to investigate")

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
    table["compliance_rate"] = (table["compliance_rate"] * 100).round(1)
    table["defect_rate"] = (table["defect_rate"] * 100).round(2)
    table["spend"] = table["spend"].round(0)

    table = table.sort_values("avg_lead_time", ascending=False).head(10)

    st.dataframe(table, use_container_width=True)

    if not table.empty:
        worst = table.iloc[0]
        st.info(
            f"Insight : {worst['Supplier']} présente le lead time moyen le plus élevé "
            f"({worst['avg_lead_time']} jours) sur {int(worst['orders'])} commandes."
        )

    st.divider()

    # ==============================
    # DATA QUALITY
    # ==============================

    st.subheader("Data quality")

    total_rows = len(base)
    missing_rate = base.isna().mean().mean() * 100
    duplicate_rate = base["PO_ID"].duplicated().mean() * 100

    q1, q2, q3 = st.columns(3)

    q1.metric("Number of rows", f"{total_rows:,}")
    q2.metric("Average missing value rate", f"{missing_rate:.2f}%")
    q3.metric("Duplicate PO_ID rate", f"{duplicate_rate:.2f}%")

    st.markdown("### Missing values by column (%)")

    missing_by_col = (base.isna().mean() * 100).round(2)
    missing_by_col = missing_by_col[missing_by_col > 0]

    if not missing_by_col.empty:
        st.dataframe(missing_by_col.sort_values(ascending=False))
    else:
        st.success("Aucune valeur manquante détectée.")


if __name__ == "__main__":
    main()
