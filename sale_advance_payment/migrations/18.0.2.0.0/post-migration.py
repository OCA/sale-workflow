# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import SUPERUSER_ID, api
from odoo.tools import split_every


def migrate(cr, version):
    if not version:
        return

    env = api.Environment(
        cr, SUPERUSER_ID, {"active_test": False, "tracking_disable": True}
    )
    orders_model = env["sale.order"]
    residual_field = orders_model._fields["amount_residual"]
    # Find sale orders through the lines of posted invoices and credit notes
    # that have been partially or fully settled. Recompute the orders when the
    # document covers multiple orders or its sale-linked lines do not add up
    # to the document total. In either case, the full settled amount may differ
    # from the amount attributable to each order.
    cr.execute("""
        WITH linked_lines AS (
            SELECT move.id AS move_id,
                   line.price_total,
                   ARRAY_AGG(DISTINCT sale_line.order_id) AS order_ids,
                   MIN(sale_line.order_id) AS first_order_id,
                   MAX(sale_line.order_id) AS last_order_id
              FROM sale_order_line_invoice_rel AS link
              JOIN sale_order_line AS sale_line ON sale_line.id = link.order_line_id
              JOIN account_move_line AS line ON line.id = link.invoice_line_id
              JOIN account_move AS move ON move.id = line.move_id
             WHERE move.state = 'posted'
               AND move.move_type IN ('out_invoice', 'out_refund')
               AND move.amount_total <> move.amount_residual
               AND line.display_type IN ('product', 'line_section', 'line_note')
             GROUP BY move.id, line.id
        ),
        affected_moves AS (
            SELECT linked.move_id
              FROM linked_lines AS linked
              JOIN account_move AS move ON move.id = linked.move_id
             GROUP BY linked.move_id, move.amount_total
            HAVING MIN(linked.first_order_id) <> MAX(linked.last_order_id)
                OR COALESCE(SUM(linked.price_total), 0) <> move.amount_total
        )
        SELECT DISTINCT UNNEST(linked.order_ids) AS order_id
          FROM linked_lines AS linked
          JOIN affected_moves USING (move_id)
         ORDER BY order_id
    """)
    candidate_ids = [order_id for (order_id,) in cr.fetchall()]
    for order_ids in split_every(1000, candidate_ids):
        orders = orders_model.browse(order_ids)
        env.add_to_compute(residual_field, orders)
        env.flush_all()
        env.invalidate_all(flush=False)
