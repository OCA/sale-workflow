# Copyright 2019 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class ProductCategory(models.Model):
    _name = "product.category"
    _inherit = ["product.category", "product.min.multiple.mixin"]

    def _get_sale_min_multiple_qty(self):
        res = super()._get_sale_min_multiple_qty()
        force_sale_min_qty = False
        if self.manual_force_sale_min_qty == 'force':
            force_sale_min_qty = True
        if self.manual_force_sale_min_qty == 'not_force':
            force_sale_min_qty = False
        if not self.manual_force_sale_min_qty:
            force_sale_min_qty = self.parent_id.force_sale_min_qty
        res.update(
            {
                "sale_min_qty": self.manual_sale_min_qty or self.parent_id.sale_min_qty,
                "force_sale_min_qty": force_sale_min_qty,
                "sale_multiple_qty": self.manual_sale_multiple_qty
                or self.parent_id.sale_multiple_qty,
            }
        )
        return res

    @api.depends(
        "parent_id.force_sale_min_qty",
        "parent_id.sale_min_qty",
        "parent_id.sale_multiple_qty",
    )
    def _compute_sale_min_multiple_qty(self):
        for rec in self:
            rec.update(rec._get_sale_min_multiple_qty())
