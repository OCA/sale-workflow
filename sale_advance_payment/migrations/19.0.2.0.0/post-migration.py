# Copyright 2026 Studio73
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api
from odoo.api import SUPERUSER_ID
from odoo.tools import split_every


def migrate(cr, version):
    if not version:
        return

    env = api.Environment(
        cr, SUPERUSER_ID, {"active_test": False, "tracking_disable": True}
    )
    orders_model = env["sale.order"]
    residual_field = orders_model._fields["amount_residual"]

    # Find orders whose invoice payment allocation may change. The old 19.0
    # compute also counted drafts and subtracted the unsigned residual from
    # the signed credit note total, so include those balances as well.
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
             WHERE move.state IN ('draft', 'posted')
               AND move.move_type IN ('out_invoice', 'out_refund')
               AND (
                   move.amount_total_in_currency_signed <> move.amount_residual
                   OR (move.state = 'posted'
                       AND move.amount_total <> move.amount_residual)
               )
               AND line.display_type IN (
                   'product', 'line_section', 'line_subsection', 'line_note'
               )
             GROUP BY move.id, line.id
        ),
        affected_moves AS (
            SELECT linked.move_id
              FROM linked_lines AS linked
              JOIN account_move AS move ON move.id = linked.move_id
             GROUP BY linked.move_id, move.state, move.move_type,
                      move.amount_total, move.amount_residual
            HAVING move.state = 'draft'
                OR (move.move_type = 'out_refund' AND move.amount_residual <> 0)
                OR MIN(linked.first_order_id) <> MAX(linked.last_order_id)
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
