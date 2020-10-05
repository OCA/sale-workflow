# Copyright 2020 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def delivery_recreate(self):
        for order in self:
            order.with_context(
                delivery_create_only=True
            ).order_line._action_launch_stock_rule()
