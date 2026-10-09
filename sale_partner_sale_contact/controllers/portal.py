# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo.fields import Domain

from odoo.addons.sale.controllers import portal


class CustomerPortal(portal.CustomerPortal):
    def _prepare_quotations_domain(self, partner):
        """Also list the quotations on which the user is the sale contact."""
        return Domain.OR(
            [
                super()._prepare_quotations_domain(partner),
                [
                    ("sale_contact_partner_id", "=", partner.id),
                    ("state", "=", "sent"),
                ],
            ]
        )

    def _prepare_orders_domain(self, partner):
        """Also list the orders on which the user is the sale contact."""
        return Domain.OR(
            [
                super()._prepare_orders_domain(partner),
                [
                    ("sale_contact_partner_id", "=", partner.id),
                    ("state", "=", "sale"),
                ],
            ]
        )
