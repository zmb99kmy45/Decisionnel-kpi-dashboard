WITH base AS (
  SELECT
    PO_ID,
    Supplier,
    Item_Category,
    CAST(Order_Date AS DATE) AS order_date,
    Quantity,
    Unit_Price,
    Negotiated_Price
  FROM procurement
)
SELECT
  DATE_TRUNC('month', order_date) AS month,
  Supplier,
  Item_Category,
  SUM(Quantity * Negotiated_Price) AS total_spend,
  SUM((Unit_Price - Negotiated_Price) * Quantity) AS total_savings,
  SUM((Unit_Price - Negotiated_Price) * Quantity) / NULLIF(SUM(Quantity * Unit_Price), 0) AS savings_rate
FROM base
GROUP BY 1, 2, 3
ORDER BY 1, 2, 3;