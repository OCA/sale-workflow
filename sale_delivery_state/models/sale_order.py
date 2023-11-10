# Copyright 2018 Akretion (http://www.akretion.com).
# @author Pierrick BRUN <pierrick.brun@akretion.com>
# Copyright 2018 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.tools import float_compare, float_is_zero


class SaleOrder(models.Model):
    _inherit = "sale.order"

    delivery_status = fields.Selection(
        [
            ("pending", "Not Delivered"),
            ("partial", "Partially Delivered"),
            ("full", "Fully Delivered"),
        ],
        # Compute method have a different name then the field because
        # the method _compute_delivery_status already exist in odoo sale_stock
        compute="_compute_oca_delivery_status",
        store=True,
    )

    force_delivery_state = fields.Boolean(
        help=(
            "Allow to enforce done state of delivery, for instance if some"
            " quantities were cancelled"
        ),
    )

    def _all_qty_delivered(self):
        """
        Returns True if all line have qty_delivered >= to ordered quantities

        If `delivery` module is installed, ignores the lines with delivery costs

        :returns: boolean
        """
        self.ensure_one()
        # Skip delivery costs lines
        sale_lines = self.order_line.filtered(lambda rec: not rec._is_delivery())
        precision = self.env["decimal.precision"].precision_get(
            "Product Unit of Measure"
        )
        return all(
            float_compare(
                line.qty_delivered, line.product_uom_qty, precision_digits=precision
            )
            >= 0
            for line in sale_lines
        )

    def _partially_delivered(self):
        """
        Returns True if at least one line is delivered

        :returns: boolean
        """
        self.ensure_one()
        # Skip delivery costs lines
        sale_lines = self.order_line.filtered(lambda rec: not rec._is_delivery())
        precision = self.env["decimal.precision"].precision_get(
            "Product Unit of Measure"
        )
        return any(
            not float_is_zero(line.qty_delivered, precision_digits=precision)
            for line in sale_lines
        )

    @api.depends("order_line.qty_delivered", "state", "force_delivery_state")
    def _compute_oca_delivery_status(self):
        for order in self:
            if order.state in ("draft", "cancel"):
                order.delivery_status = None
            elif order.force_delivery_state or order._all_qty_delivered():
                order.delivery_status = "full"
            elif order._partially_delivered():
                order.delivery_status = "partial"
            else:
                order.delivery_status = "pending"

    def action_force_delivery_state(self):
        self.write({"force_delivery_state": True})

    def action_unforce_delivery_state(self):
        self.write({"force_delivery_state": False})
