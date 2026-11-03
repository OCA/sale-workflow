# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def action_confirm(self):
        """Apply the contact-to-company switch on website orders.

        Website orders are created in code with ``partner_id`` set to the
        portal user's partner (the contact person), so the auto-switch
        onchange of ``sale.contact.mixin`` never runs for them.  The switch
        cannot be applied while the order is still a cart either, because
        ``website_sale`` resets ``partner_id`` back to the logged-in user's
        partner on every request while the order is draft (see
        ``Website._get_and_cache_current_cart``) and looks up abandoned carts
        by that same partner.  Confirmation is therefore the first stable
        point to promote the commercial partner.

        The switch is applied after ``super()`` so that:

        * the order confirmation email is sent to the person who actually
          placed the order, not to the company;
        * documents created on confirmation (e.g. delivery orders) are
          generated with the addresses chosen at checkout;
        * the pricelist is not recomputed (``_compute_pricelist_id`` skips
          non-draft orders).
        """
        res = super().action_confirm()
        self.filtered("website_id")._sale_contact_apply_website_switch()
        return res

    def _sale_contact_apply_website_switch(self):
        """Promote ``partner_id`` to the commercial partner and store the
        contact person in ``sale_contact_partner_id``."""
        for order in self:
            contact = order.partner_id
            commercial = contact.commercial_partner_id
            if not commercial or contact == commercial:
                continue
            order.write(
                {
                    "partner_id": commercial.id,
                    "sale_contact_partner_id": (
                        order.sale_contact_partner_id.id or contact.id
                    ),
                    # Pin the values chosen at checkout: writing partner_id
                    # would otherwise trigger their recomputation from the
                    # new partner.
                    "partner_invoice_id": order.partner_invoice_id.id,
                    "partner_shipping_id": order.partner_shipping_id.id,
                    "fiscal_position_id": order.fiscal_position_id.id,
                    "payment_term_id": order.payment_term_id.id,
                }
            )
