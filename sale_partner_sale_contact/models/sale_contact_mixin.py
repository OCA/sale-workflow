# Copyright 2026 OpenStudio SAS
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class SaleContactMixin(models.AbstractModel):
    """Mixin that adds a Sale Contact field and the related onchange logic.

    Inherit from this mixin on any model that has a ``partner_id`` field and
    needs to track a named commercial contact person (e.g. procurement manager,
    project lead) distinct from the billing/shipping addresses.
    """

    _name = "sale.contact.mixin"
    _description = "Sale Contact Mixin"

    sale_contact_partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Sale Contact",
        domain=(
            "[('id', 'child_of', partner_id), "
            "('is_company', '=', False), ('id', '!=', partner_id)]"
        ),
        # Copied by default: when duplicating a sale order or a project the
        # commercial context (same contact person) should carry over.
        # account.move overrides this to copy=False because the contact is
        # normally propagated from the originating sale order via
        # _prepare_invoice(); carrying it over on a manual duplicate risks
        # stale data (person has left, role changed, etc.).
        copy=True,
        help="Contact person for this record. "
        "Only child contacts of the partner can be selected.",
    )

    @api.onchange("partner_id")
    def _onchange_partner_id_sale_contact_auto_switch(self):
        """Auto-switch from contact person to root company.

        When the user selects a contact person instead of a company, this
        handler corrects the selection by setting ``partner_id`` to the root
        company and storing the chosen contact in ``sale_contact_partner_id``.

        Defined on the mixin so all inheriting models get it automatically.
        Odoo calls every ``@api.onchange("partner_id")`` handler registered on
        the model, so this runs alongside the model's own standard partner
        onchange (fiscal position, pricelist, payment terms, …).
        """
        self._sale_contact_apply_auto_switch()

    def _sale_contact_apply_auto_switch(self):
        """Apply the contact-to-company auto-switch.

        If the user selects a contact person instead of a company, corrects
        the selection by setting ``partner_id`` to the root company and storing
        the chosen contact in ``sale_contact_partner_id``.

        Returns:
            bool: True if a switch was performed, False otherwise.
        """
        if (
            self.partner_id
            and self.partner_id.commercial_partner_id
            and self.partner_id.commercial_partner_id != self.partner_id
            and self._sale_contact_should_auto_switch()
        ):
            contact = self.partner_id
            self.partner_id = contact.commercial_partner_id
            self.sale_contact_partner_id = contact
            return True
        return False

    def _sale_contact_should_auto_switch(self):
        """Hook to let inheriting models opt out of the auto-switch.

        Returns True by default. Models can override this to skip the
        contact-to-company promotion in situations where selecting a
        non-company contact as ``partner_id`` is legitimate.
        """
        return True

    @api.onchange("partner_id")
    def _onchange_partner_id_clear_sale_contact(self):
        """Clear sale contact when the partner changes
        and the contact is no longer valid."""
        # Clear sale contact if it no longer belongs to the new partner's hierarchy.
        # We compare commercial_partner_id (the root company) rather than parent_id
        # (direct parent only), to match the domain's use of child_of which includes
        # the full descendant tree (children, grandchildren, etc.).
        # In B2C (individual without a company), commercial_partner_id == the partner
        # itself, so that case is also handled correctly.
        if self.sale_contact_partner_id:
            if (
                self.sale_contact_partner_id.commercial_partner_id != self.partner_id
                and self.sale_contact_partner_id != self.partner_id
            ):
                self.sale_contact_partner_id = False
