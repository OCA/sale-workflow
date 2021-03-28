# Copyright 2017 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    default_invoice_policy = fields.Selection(
        [("order", "Ordered quantities"), ("delivery", "Delivered quantities")],
        string="Default Invoicing Policy",
        help="Ordered Quantity: Invoice based on the quantity the customer "
        "ordered.\n"
        "Delivered Quantity: Invoiced based on the quantity the vendor "
        "delivered (time or deliveries).",
        default="order",
    )

    invoice_policy = fields.Selection(
        compute="_compute_invoice_policy",
        store=False,
        readonly=True,
        search="_search_invoice_policy",
        inverse="_inverse_invoice_policy",
    )

    @api.multi
    def _inverse_invoice_policy(self):
        for template in self.filtered("invoice_policy"):
            template.default_invoice_policy = template.invoice_policy

    @api.multi
    @api.depends("type", "default_invoice_policy")
    def _compute_invoice_policy(self):
        """
        Apply the invoice_policy given by context (if exist) otherwise use the
        default invoice policy given by the field with this same name.
        If the product is type = 'service', we don't have to apply the invoice
        policy given by the context.
        :return:
        """
        invoice_policy = self.env.context.get("invoice_policy")
        for tmpl in self:
            if tmpl.type != "service" and invoice_policy:
                tmpl.invoice_policy = invoice_policy
            else:
                tmpl.invoice_policy = tmpl.default_invoice_policy

    @api.model
    def _search_invoice_policy(self, operator, value):
        return [("default_invoice_policy", operator, value)]
