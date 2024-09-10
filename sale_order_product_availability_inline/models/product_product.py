# Copyright 2020 Tecnativa - Ernesto Tejeda
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class ProductProduct(models.Model):
    _inherit = "product.product"

    def _compute_display_name(self):
        res = super()._compute_display_name()
        if self.env.context.get("so_product_stock_inline"):
            self = self.with_context(warehouse=self.env.context.get("warehouse"))
            availability = {r.id: [r.free_qty, r.uom_id.display_name] for r in self}
            precision = self.env["decimal.precision"].precision_get(
                "Product Unit of Measure"
            )
            for record in self:
                name = "{} ({:.{}f} {})".format(
                    record.display_name,
                    availability[record.id][0],
                    precision,
                    availability[record.id][1],
                )
                record.display_name = name
        return res
