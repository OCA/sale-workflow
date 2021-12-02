# Copyright 2021 Akretion France (http://www.akretion.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, models
from odoo.tools import float_compare


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _log_decrease_ordered_quantity(self, documents, cancel=False):
        # no log message as we support the feature
        pass


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def write(self, values):
        lines = self.env["sale.order.line"]
        if "product_uom_qty" in values:
            precision = self.env["decimal.precision"].precision_get(
                "Product Unit of Measure"
            )
            lines = self.filtered(
                lambda r: r.state == "sale"
                and not r.is_expense
                and float_compare(
                    r.product_uom_qty,
                    values["product_uom_qty"],
                    precision_digits=precision,
                )
                == 1
            )
        res = super().write(values)
        if lines:
            lines.mapped("move_ids")._update_qty_recursively(values["product_uom_qty"])
        return res

    @api.onchange("product_uom_qty")
    def _onchange_product_uom_qty(self):
        res = super()._onchange_product_uom_qty()
        if "warning" in res and res["warning"]["title"] == _(
            "Ordered quantity decreased!"
        ):
            return {}
        return res
