# Copyright 2026 Tohid Pathan (Allied Vision Technologies Pvt. Ltd.)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResPartner(models.Model):
    """Extend res.partner with portal delivery address management."""

    _inherit = "res.partner"

    is_portal_delivery = fields.Boolean(
        string="Portal Delivery Address",
        default=False,
        index=True,
        help=(
            "Indicates this address was created by a portal user specifically "
            "for delivery purposes."
        ),
    )

    def _get_portal_delivery_addresses(self):
        """Return active delivery-type child partners of the commercial partner.

        :return: Recordset of delivery-type child partners.
        :rtype: res.partner
        """
        self.ensure_one()
        return self.env["res.partner"].search(
            [
                ("id", "child_of", self.commercial_partner_id.id),
                ("type", "=", "delivery"),
                ("active", "=", True),
            ],
            order="id asc",
        )

    def _can_be_edited_by_current_customer(self, **kwargs):
        """Override to enforce same-commercial-partner ownership.

        A portal user may only edit addresses whose commercial_partner_id
        matches their own.  The base implementation already covers most cases
        but this override adds an explicit check on the ``is_portal_delivery``
        path, making the rule crystal-clear and auditable.

        :return: Whether the current user may edit this partner record.
        :rtype: bool
        """
        self.ensure_one()
        # Resolve the current partner first: the core implementation
        # dereferences ``current_partner.commercial_partner_id`` and crashes
        # when no partner can be resolved.
        current_partner = self._get_current_partner(**kwargs)
        if not current_partner:
            return False
        if not super()._can_be_edited_by_current_customer(**kwargs):
            return False
        # Additional hard guard: commercial partner must match the current user.
        return self.commercial_partner_id == current_partner.commercial_partner_id
