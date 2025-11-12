SELECT p.category,
       ROUND(SUM(i.on_hand * p.unit_cost), 2) AS inventory_value
FROM inventory i
JOIN parts p ON p.part_id = i.part_id
JOIN locations l ON l.location_id = i.location_id
WHERE l.code = 'MAIN'
GROUP BY p.category
ORDER BY inventory_value DESC;
