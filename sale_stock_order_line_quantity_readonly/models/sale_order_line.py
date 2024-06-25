# Copyright 2024 Camptocamp
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    quantity_updatable = fields.Boolean(compute="_compute_quantity_updatable")

    @api.depends("state", "qty_delivered_method")
    def _compute_quantity_updatable(self):
        for rec in self:
            rec.quantity_updatable = rec._is_updatable()

    def _is_updatable(self):
        self.ensure_one()
        if self.state not in ["done", "cancel"]:
            return self.state != "sale" or self.qty_delivered_method != "stock_move"
        return False
