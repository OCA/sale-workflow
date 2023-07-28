def pre_init_hook(cr):
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

    cr.execute(
        """
update sale_order_line as sol set qty_procured = r.qty_procured,
qty_to_procure = sol.product_uom_qty - r.qty_procured
from (select sol.id, sum(
    case
        when (
        sl.usage = 'customer'
        and sm.origin_returned_move_id is null
        or (
        sm.origin_returned_move_id is not null and sm.to_refund
        )) then
            ROUND(
                ((sm.product_uom_qty / sm_product_uom.factor) * sol_product_uom.factor),
                SCALE(sol_product_uom.rounding)
                )
        when (
        sl.usage != 'customer'
        and sm.to_refund
        ) then
        ROUND(
                ((sm.product_uom_qty / sm_product_uom.factor) * sol_product_uom.factor),
                SCALE(sol_product_uom.rounding)
                ) * -1
        else 0
    end)
 AS qty_procured
from
sale_order_line as sol
inner join (
    select sol.id, sm.id as move_id, sm.location_id, sm.location_dest_id
    from sale_order_line as sol
    left join stock_move as sm on (
        sm.state != 'cancel'
        and sm.scrapped = false
        and sol.product_id = sm.product_id
        and sm.sale_line_id = sol.id
        )
) as q on q.id = sol.id
left join stock_move as sm on sm.id = q.move_id
left join product_product as pp on pp.id = sol.product_id
left join product_template as pt on pt.id = pp.product_tmpl_id
left join stock_location as sl on sl.id = q.location_dest_id
LEFT JOIN uom_uom sm_product_uom ON sm.product_uom = sm_product_uom.id
LEFT JOIN uom_uom sol_product_uom ON sol.product_uom = sol_product_uom.id
group by sol.id, sm.product_uom, sol.product_uom
) as r
where r.id = sol.id
    """
    )
