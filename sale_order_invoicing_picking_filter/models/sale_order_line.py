# Copyright 2023 Manuel Regidor <manuel.regidor@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models
from odoo.fields import Command


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _prepare_stock_move_invoice_line(self, move, **optional_values):
        self.ensure_one()
        qty = move.product_uom._compute_quantity(move.quantity_done, self.product_uom)
        res = {
            "display_type": "product",
            "sequence": self.sequence,
            "name": self.name,
            "product_id": self.product_id.id,
            "product_uom_id": self.product_uom.id,
            "quantity": qty,
            "discount": self.discount,
            "price_unit": self.price_unit,
            "tax_ids": [Command.set(self.tax_id.ids)],
            "sale_line_ids": [Command.link(self.id)],
            "move_line_ids": [Command.link(move.id)],
        }
        analytic_account_id = self.order_id.analytic_account_id.id
        if self.analytic_distribution and not self.display_type:
            res["analytic_distribution"] = self.analytic_distribution
        if analytic_account_id and not self.display_type:
            analytic_account_id = str(analytic_account_id)
            if "analytic_distribution" in res:
                res["analytic_distribution"][analytic_account_id] = (
                    res["analytic_distribution"].get(analytic_account_id, 0) + 100
                )
            else:
                res["analytic_distribution"] = {analytic_account_id: 100}
        if optional_values:
            res.update(optional_values)
        return res
