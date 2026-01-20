# Copyright 2026 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from odoo import models


class ProductTemplate(models.Model):
    _name = "product.template"
    _inherit = ["product.template", "product.price.compliance.threshold.config.mixin"]

    def _get_price_compliance_thresholds(self):
        return (
            super()._get_price_compliance_thresholds()
            or self.categ_id._get_price_compliance_thresholds()
        )
