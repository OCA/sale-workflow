# Copyright 2017 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    @api.depends("detailed_type")
    def _compute_invoice_policy(self):
        """
        Apply the invoice_policy given by context (if exist) otherwise use the
        default invoice policy given by variable with this same name.
        If the product is type = 'service', we don't have to apply the invoice
        policy given by the context.
        """
        invoice_policy = self.env.context.get("invoice_policy")
        if invoice_policy:
            non_service_products = self.filtered(lambda p: p.type != "service")
            non_service_products.invoice_policy = invoice_policy
        else:
            default_invoice_policy = (
                self.env["res.config.settings"]
                .sudo()
                .default_get(["default_invoice_policy"])
                .get("default_invoice_policy", False)
            )
            self.invoice_policy = default_invoice_policy
