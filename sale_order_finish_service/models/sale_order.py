# Copyright 2026 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    finished_sale_order = fields.Boolean(copy=False)

    def action_finish_sale_order(self):
        for order in self.filtered(
            lambda o: o.state == "sale" and not o.finished_sale_order
        ):
            order.finished_sale_order = True

    def action_unfinish_sale_order(self):
        for order in self.filtered(
            lambda o: o.state == "sale" and o.finished_sale_order
        ):
            order.finished_sale_order = False
