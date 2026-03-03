SELECT
  COUNT(*) AS total_rows,
  (COUNT(*) - COUNT(DISTINCT PO_ID)) * 1.0 / COUNT(*) AS duplicate_po_id_rate,
  SUM(CASE WHEN Supplier IS NULL THEN 1 ELSE 0 END) * 1.0 / COUNT(*) AS missing_supplier_rate,
  SUM(CASE WHEN Order_Date IS NULL THEN 1 ELSE 0 END) * 1.0 / COUNT(*) AS missing_order_date_rate,
  SUM(CASE WHEN Delivery_Date IS NULL THEN 1 ELSE 0 END) * 1.0 / COUNT(*) AS missing_delivery_date_rate,
  SUM(CASE WHEN Defective_Units IS NULL THEN 1 ELSE 0 END) * 1.0 / COUNT(*) AS missing_defective_units_rate
FROM procurement;