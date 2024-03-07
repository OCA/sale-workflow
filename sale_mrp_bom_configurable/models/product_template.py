from odoo import models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    def _find_price_config(self):
        return self.env["sale.price.config"].search([("product_id", "=", self.id)])
