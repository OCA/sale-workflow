# Copyright 2020 Tecnativa - Ernesto Tejeda
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class ProductProduct(models.Model):
    _inherit = "product.product"

    def name_get(self):
        if self.env.context.get("so_product_stock_inline"):
            res = super().name_get()
            self = self.with_context(warehouse=self.env.context.get("warehouse"))
            availability = {r.id: [r.free_qty, r.uom_id.name] for r in self}
            precision = self.env["decimal.precision"].precision_get(
                "Product Unit of Measure"
            )
            new_res = []
            for _i in res:
                name = "{} ({:.{}f} {})".format(
                    _i[1], availability[_i[0]][0], precision, availability[_i[0]][1]
                )
                new_res.append((_i[0], name))
            return new_res
        else:
            return super().name_get()
