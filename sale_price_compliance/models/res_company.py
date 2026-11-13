# Copyright 2026 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)
#
from odoo import models


class ResCompany(models.Model):
    _name = "res.company"
    _inherit = ["res.company", "product.price.compliance.threshold.config.mixin"]
