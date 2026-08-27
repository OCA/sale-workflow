# © 2019 Akretion
# Copyright 2025 Raumschmiede GmbH
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import fields, models


class SaleOrderLine(models.Model):
    _inherit = ["sale.order.line", "base.exception"]
    _name = "sale.order.line"

    ignore_exception = fields.Boolean(related="order_id.ignore_exception")

    def _get_main_records(self):
        return self.mapped("order_id")
