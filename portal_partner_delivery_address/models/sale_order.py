# Copyright 2026 Tohid Pathan (Allied Vision Technologies Pvt. Ltd.)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models
from odoo.exceptions import AccessError, UserError


class SaleOrder(models.Model):
    """Extend sale.order with portal shipping address update logic."""

    _inherit = "sale.order"

    def action_update_portal_shipping_address(self, shipping_partner_id):
        """Update the shipping address of a draft/sent sale order.

        Security contract:
        - Order must be in draft or sent state.
        - shipping_partner_id must share the same commercial_partner_id as the
          order's partner_id.  Any mismatch raises ``AccessError`` so the caller
          (controller) can surface a 403 to the browser.

        Ownership verification is done before any ``sudo()`` escalation, per
        OCA security guidelines.

        :param res.partner shipping_partner_id: The new shipping partner.
        :raises UserError: When the order state does not allow address changes.
        :raises AccessError: When the address does not belong to the same
                             commercial partner.
        """
        self.ensure_one()
        if self.state not in ("draft", "sent"):
            raise UserError(
                self.env._(
                    "The shipping address can only be changed on quotations "
                    "(draft or sent orders)."
                )
            )
        # Hard ownership check – must precede any sudo() call.
        if (
            shipping_partner_id.commercial_partner_id
            != self.partner_id.commercial_partner_id
        ):
            raise AccessError(
                self.env._(
                    "The selected shipping address does not belong to the customer."
                )
            )
        # Explicit ownership verified above; sudo() needed to write on the
        # order when called from a portal context (limited record rules).
        self.sudo().write({"partner_shipping_id": shipping_partner_id.id})
