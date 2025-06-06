# Copyright 2017 ACSONE SA/NV (<http://acsone.eu>)
# Copyright 2025 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
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

    def _force_lines_to_invoice_policy_order(self):
        # When a SO is fully paid by a payment transaction and the automatic
        # invoicing is enabled, the lines are forced to policy on order.
        # Reflect this on the SO policy.
        self.invoice_policy = "order"
        return super()._force_lines_to_invoice_policy_order()
