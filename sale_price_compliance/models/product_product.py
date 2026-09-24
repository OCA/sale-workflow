# Copyright 2026 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from odoo import models


class ProductProduct(models.Model):
    _name = "product.product"
    _inherit = ["product.product", "product.price.compliance.threshold.config.mixin"]

    def _get_price_compliance_thresholds(self):
        return (
            super()._get_price_compliance_thresholds()
            or self.product_tmpl_id._get_price_compliance_thresholds()
        )
