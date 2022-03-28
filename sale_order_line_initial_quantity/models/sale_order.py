# Copyright 2021 Akretion France (http://www.akretion.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    initial_qty_changed = fields.Boolean(
        string="Initial Quantity Changed",
        compute="_compute_initial_qty_changed",
        store=True,
    )

    @api.depends("order_line", "order_line.product_uom_qty")
    def _compute_initial_qty_changed(self):
        for order in self:
            order.initial_qty_changed = order.state in ["sale", "done"] and bool(
                order.order_line.filtered(
                    lambda l: l.product_uom_qty != l.product_uom_initial_qty
                )
            )

    def action_confirm(self):
        res = super().action_confirm()
        for order in self:
            for line in order.order_line:
                line.product_uom_initial_qty = line.product_uom_qty
        return res
