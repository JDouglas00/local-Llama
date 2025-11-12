SELECT p.sku, p.description, l.code AS location,
       i.on_hand, i.reorder_point, i.safety_stock,
       (i.reorder_point + i.safety_stock) AS min_needed,
       (i.reorder_point + i.safety_stock) - i.on_hand AS shortage
FROM inventory i
JOIN parts p ON p.part_id = i.part_id
JOIN locations l ON l.location_id = i.location_id
WHERE i.on_hand < (i.reorder_point + i.safety_stock)
ORDER BY shortage DESC
LIMIT 50;
