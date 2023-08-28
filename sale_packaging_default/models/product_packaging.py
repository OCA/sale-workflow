# Copyright 2023 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)
from odoo import api, fields, models


class ProductPackaging(models.Model):
    _inherit = "product.packaging"

    sales_default = fields.Boolean(
        "Default for sales",
        compute="_compute_sales_default",
        readonly=False,
        store=True,
        help=(
            "The first packaging with this option checked will be used by "
            "default in sales orders."
        ),
    )

    @api.depends("sales")
    def _compute_sales_default(self):
        """Remove from default if packaging is not available for sales."""
        for packaging in self:
            if not packaging.sales:
                packaging.sales_default = False

    def _find_suitable_product_packaging(self, product_qty, uom_id):
        """Find nothing if you want to keep what was there."""
        if self.env.context.get("keep_product_packaging"):
            return self.browse()
        return super()._find_suitable_product_packaging(product_qty, uom_id)
