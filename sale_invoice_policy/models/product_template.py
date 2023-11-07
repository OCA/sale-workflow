# Copyright 2017 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    def _default_invoice_policy(self):
        return (
            self.env["res.config.settings"]
            .sudo()
            .default_get(["default_invoice_policy"])
            .get("default_invoice_policy", False)
        )

    invoice_policy = fields.Selection(default=_default_invoice_policy)
