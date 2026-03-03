WITH supplier_month AS (
  SELECT
    DATE_TRUNC('month', CAST(Order_Date AS DATE)) AS month,
    Supplier,
    SUM(Quantity * Negotiated_Price) AS spend,
    SUM((Unit_Price - Negotiated_Price) * Quantity) AS savings
  FROM procurement
  GROUP BY 1, 2
),
ranked AS (
  SELECT
    month,
    Supplier,
    spend,
    savings,
    RANK() OVER (PARTITION BY month ORDER BY spend DESC) AS spend_rank,
    RANK() OVER (PARTITION BY month ORDER BY savings DESC) AS savings_rank
  FROM supplier_month
)
SELECT *
FROM ranked
WHERE spend_rank <= 10 OR savings_rank <= 10
ORDER BY month DESC, spend_rank ASC, savings_rank ASC;