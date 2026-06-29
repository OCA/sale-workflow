# Copyright 2025 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import models
from odoo.tools import float_round


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _prepare_procurement_values(self, group_id=False):
        values = super()._prepare_procurement_values(group_id)
        values["secondary_uom_id"] = self.secondary_uom_id.id
        values["secondary_uom_qty"] = self.env.context.get(
            "procure_secondary_uom_qty", {}
        ).get(self.id, self.secondary_uom_qty)
        return values

    def write(self, vals):
        if "secondary_uom_qty" in vals:
            lines = self.filtered(lambda r: r.state == "sale" and not r.is_expense)
            procure_secondary_uom_qty = {
                line.id: float_round(
                    vals["secondary_uom_qty"] - line.secondary_uom_qty,
                    precision_rounding=self.secondary_uom_id.uom_id.rounding or 0.01,
                )
                for line in lines
            }
            self = self.with_context(
                procure_secondary_uom_qty=procure_secondary_uom_qty
            )
        return super().write(vals)
