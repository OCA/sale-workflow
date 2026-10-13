from odoo import SUPERUSER_ID, api
from odoo.osv import expression


def post_init_hook(cr, registry):
    """
    Recompute untaxed amount to invoice for sale order lines with discounts
    different than 0.
    """
    env = api.Environment(cr, SUPERUSER_ID, {})
    sol = env["sale.order.line"]
    domain = expression.OR([[(field, "!=", 0)] for field in sol._discount_fields()])
    sale_lines = sol.search(domain)
    sale_lines._compute_untaxed_amount_to_invoice()
