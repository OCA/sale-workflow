def pre_init_hook(env):
    cr = env.cr

    cr.execute(
        """
        ALTER TABLE sale_order_line ADD COLUMN IF NOT EXISTS qty_procured numeric;
        COMMENT ON COLUMN sale_order_line.qty_procured IS 'Quantity Procured';
        """
    )
    cr.execute(
        """
        ALTER TABLE sale_order_line ADD COLUMN IF NOT EXISTS qty_to_procure numeric;
        COMMENT ON COLUMN sale_order_line.qty_to_procure IS 'Quantity to Procure"';
        """
    )

    # Backfill qty_procured / qty_to_procure by replicating
    # _get_qty_procurement in SQL (faster than the Python ).

    # qty_procured = how much of the SO line actually reached the customer
    # - Add outgoing moves toward customers
    # - Substract to_refund returns
    # - Ignore the rest: cancelled, scrapped, non-refund returns
    cr.execute("""\
UPDATE sale_order_line AS sol
SET
    qty_procured = r.qty_procured,
    qty_to_procure = sol.product_uom_qty - r.qty_procured
FROM (
    SELECT
        sol.id,
        SUM(
            CASE
                WHEN (
                    (
                        sl.usage = 'customer'
                        AND sm.origin_returned_move_id IS NULL
                    )
                    OR
                    (
                        sm.origin_returned_move_id IS NOT NULL
                        AND sm.to_refund
                    )
                ) THEN
                    ROUND(
                        ((sm.product_uom_qty / sm_product_uom.factor) * sol_product_uom.factor),
                        SCALE(sol_product_uom.rounding)
                        )
                WHEN (
                    sl.usage != 'customer'
                    AND sm.to_refund
                ) THEN
                ROUND(
                        ((sm.product_uom_qty / sm_product_uom.factor) * sol_product_uom.factor),
                        SCALE(sol_product_uom.rounding)
                        ) * -1
                ELSE 0
            END
        ) AS qty_procured
    FROM
    sale_order_line AS sol
    INNER JOIN (
        SELECT
            sol.id,
            sm.id AS move_id,
            sm.location_id,
            sm.location_dest_id
        FROM sale_order_line AS sol
        LEFT JOIN stock_move AS sm ON (
            sm.state != 'cancel'
            AND sm.scrapped = false
            AND sol.product_id = sm.product_id
            AND sm.sale_line_id = sol.id
            )
    ) AS q ON q.id = sol.id
    LEFT JOIN stock_move AS sm ON sm.id = q.move_id
    LEFT JOIN product_product AS pp ON pp.id = sol.product_id
    LEFT JOIN product_template AS pt ON pt.id = pp.product_tmpl_id
    LEFT JOIN stock_location AS sl ON sl.id = q.location_dest_id
    LEFT JOIN uom_uom sm_product_uom ON sm.product_uom = sm_product_uom.id
    LEFT JOIN uom_uom sol_product_uom ON sol.product_uom = sol_product_uom.id
    GROUP BY
        sol.id,
        sm.product_uom,
        sol.product_uom
) AS r
WHERE r.id = sol.id
    """
    )
    raise 
