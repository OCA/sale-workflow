# Copyright 2017 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    invoice_policy = fields.Selection(
        [
            ("product", "Products Invoice Policy"),
            ("order", "Ordered quantities"),
            ("delivery", "Delivered quantities"),
        ],
        compute="_compute_invoice_policy",
        store=True,
        readonly=False,
        required=True,
        precompute=True,
        help="Ordered Quantity: Invoice based on the quantity the customer "
        "ordered.\n"
        "Delivered Quantity: Invoiced based on the quantity the vendor "
        "delivered (time or deliveries).",
    )

    @api.depends("company_id")
    def _compute_invoice_policy(self) -> None:
        """
        Get default sale order invoice policy
        """
        for company, sale_orders in self.partition("company_id").items():
            sale_orders.invoice_policy = company.sale_default_invoice_policy
