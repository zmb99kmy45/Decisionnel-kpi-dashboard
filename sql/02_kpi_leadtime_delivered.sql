WITH delivered AS (
  SELECT
    Supplier,
    CAST(Order_Date AS DATE) AS order_date,
    CAST(Delivery_Date AS DATE) AS delivery_date
  FROM procurement
  WHERE LOWER(Order_Status) = 'delivered'
    AND Delivery_Date IS NOT NULL
    AND Order_Date IS NOT NULL
)
SELECT
  Supplier,
  AVG(DATE_DIFF('day', order_date, delivery_date)) AS avg_lead_time_days,
  PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY DATE_DIFF('day', order_date, delivery_date)) AS median_lead_time_days
FROM delivered
GROUP BY Supplier
ORDER BY avg_lead_time_days DESC;