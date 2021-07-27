# Copyright 2021 Manuel Calero Solís (https://xtendoo.es)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, SUPERUSER_ID


def post_init_hook(cr, registry):
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        sale_order_lines = env['sale.order.line'].search([
            ('unit_weight', '=', False),
            ('product_id.weight', '!=', False),
        ])
        for sale_order_line in sale_order_lines:
            sale_order_line.write({
                'unit_weight': sale_order_line.product_id.weight
            })
