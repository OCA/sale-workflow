# Copyright 2017 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    def _default_default_invoice_policy(self):
        return self.env["ir.default"].get("product.template", "invoice_policy")

    default_invoice_policy = fields.Selection(
        [("order", "Ordered quantities"), ("delivery", "Delivered quantities")],
        string="Default Invoicing Policy",
        help="Ordered Quantity: Invoice based on the quantity the customer "
        "ordered.\n"
        "Delivered Quantity: Invoiced based on the quantity the vendor "
        "delivered (time or deliveries).",
        default=lambda x: x._default_default_invoice_policy(),
    )
