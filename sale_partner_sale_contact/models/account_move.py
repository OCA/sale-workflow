# Copyright 2026 OpenStudio SAS
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class AccountMove(models.Model):
    _inherit = ["account.move", "sale.contact.mixin"]
    _name = "account.move"

    sale_contact_partner_id = fields.Many2one(
        # Not copied on duplication: the contact is normally propagated from
        # the sale order via _prepare_invoice().  Carrying it over on a manual
        # duplicate risks stale data (person has left, role changed, etc.).
        copy=False,
        help="Contact person for this invoice. "
        "Only child contacts of the partner can be selected.",
    )

    def _sale_contact_should_auto_switch(self):
        # On an invoice it is legitimate to bill a dedicated invoice address
        # (address type 'invoice') as partner_id rather than the root company,
        # so the contact-to-company auto-switch must not kick in for those.
        if self.partner_id.type == "invoice":
            return False
        return super()._sale_contact_should_auto_switch()
