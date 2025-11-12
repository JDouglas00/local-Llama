-- :parent_sku and :qty are parameters you bind in Python
WITH parent AS (
  SELECT part_id FROM parts WHERE sku = :parent_sku
),
components AS (
  SELECT b.component_part_id, b.qty_per, b.scrap_pct
  FROM bom b JOIN parent p ON b.parent_part_id = p.part_id
)
SELECT p.sku AS component_sku, p.description,
       ROUND(:qty * c.qty_per * (1 + c.scrap_pct), 3) AS qty_needed,
       p.uom
FROM components c
JOIN parts p ON p.part_id = c.component_part_id
ORDER BY component_sku;
