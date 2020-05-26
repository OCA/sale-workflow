# Copyright 2019 Akretion
#  @author Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.addons import decimal_precision as dp


class ProductProduct(models.Model):
    _name = "product.product"
    _inherit = ["product.product", "product.min.multiple.mixin"]

    def _get_sale_min_multiple_qty(self):
        res = super(ProductProduct, self)._get_sale_min_multiple_qty()
        res.update(
            {
                "sale_min_qty": self.manual_sale_min_qty
                or self.product_tmpl_id.sale_min_qty,
                "force_sale_min_qty": self.manual_force_sale_min_qty
                or self.product_tmpl_id.force_sale_min_qty,
                "sale_multiple_qty": self.manual_sale_multiple_qty
                or self.product_tmpl_id.sale_multiple_qty,
            }
        )
        return res

    @api.depends(
        "product_tmpl_id.force_sale_min_qty",
        "product_tmpl_id.sale_min_qty",
        "product_tmpl_id.sale_multiple_qty",
    )
    def _compute_sale_min_multiple_qty(self):
        for rec in self:
            rec.update(rec._get_sale_min_multiple_qty())

