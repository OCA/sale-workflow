# Copyright 2021 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.tools import float_compare, float_is_zero


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    delivery_state = fields.Selection(
        [
            ("no", "No delivery"),
            ("unprocessed", "Unprocessed"),
            ("partially", "Partially processed"),
            ("done", "Done"),
        ],
        # Compute method have a different name then the field because
        # the method _compute_delivery_state already exist to compute
        # the field delivery_set in odoo delivery module
        compute="_compute_sale_line_delivery_state",
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
        Returns True if line has qty_delivered >= to ordered quantities

        :returns: boolean
        """
        self.ensure_one()
        precision = self.env["decimal.precision"].precision_get(
            "Product Unit of Measure"
        )
        return (
            float_compare(
                self.qty_delivered, self.product_uom_qty, precision_digits=precision
            )
            >= 0
        )

    def _partially_delivered(self):
        """
        Returns True if line has qty_delivered != to 0 and < ordered
        quantities.

        :returns: boolean
        """
        self.ensure_one()
        precision = self.env["decimal.precision"].precision_get(
            "Product Unit of Measure"
        )
        return not float_is_zero(self.qty_delivered, precision_digits=precision)

    @api.depends("qty_delivered", "state", "force_delivery_state")
    def _compute_sale_line_delivery_state(self):
        """
        If `delivery` module is installed, lines with delivery costs are marked
        as 'No delivery'.
        """
        for line in self:
            if line.state in ("draft", "cancel") or line._is_delivery():
                line.delivery_state = "no"
            elif line.force_delivery_state or line._all_qty_delivered():
                line.delivery_state = "done"
            elif line._partially_delivered():
                line.delivery_state = "partially"
            else:
                line.delivery_state = "unprocessed"

    def action_force_delivery_state(self):
        self.write({"force_delivery_state": True})

    def action_unforce_delivery_state(self):
        self.write({"force_delivery_state": False})
