from odoo import models


class ProductProduct(models.Model):
    _inherit = "product.product"

    def _default_quick_uom_id(self):
        if self.env.context.get("parent_model", False) == "sale.blanket.order":
            return self.uom_id
        return super()._default_quick_uom_id()
