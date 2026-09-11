# Copyright 2026 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from odoo import models


class ProductCategory(models.Model):
    _name = "product.category"
    _inherit = ["product.category", "product.price.compliance.threshold.config.mixin"]

    def _get_price_compliance_thresholds(self):
        res = super()._get_price_compliance_thresholds()
        if not res and self.parent_id:
            res = self.parent_id._get_price_compliance_thresholds()
        return res or self.env.company._get_price_compliance_thresholds()
