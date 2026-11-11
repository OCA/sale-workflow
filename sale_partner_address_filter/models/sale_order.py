# Copyright 2025 Open Source Integrators
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    only_customer_addresses = fields.Boolean(
        string="Select Only Customer Contacts",
        default=True,
        help="When checked, delivery and invoice addresses are filtered "
        "to only show addresses belonging to the customer's commercial company.",
    )

    @api.depends("only_customer_addresses", "partner_id.commercial_partner_id")
    def _compute_address_domain(self):
        """Compute domain for address fields"""
        for order in self:
            comm_partner = order.partner_id.commercial_partner_id
            address_domain = (
                [("commercial_partner_id", "=", comm_partner.id)]
                if order.only_customer_addresses
                else []
            )
            # Return domain as string for XML compatibility
            order.address_domain = str(address_domain)

    address_domain = fields.Text(compute="_compute_address_domain")
