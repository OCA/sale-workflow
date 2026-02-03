# Copyright 2026 Tecnativa - Pilar Vargas
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import models


class ResPartner(models.Model):
    _inherit = "res.partner"

    def can_edit_vat(self):
        # If VAT is not available, allow it to be completed.
        if not self.vat:
            return True
        return super().can_edit_vat()

    def can_edit_country(self):
        # Allow completing country only if it is missing.
        # Do not use can_edit_vat(), because that would also unlock VAT in portal.
        self.ensure_one()
        return not self.country_id or self.can_edit_vat()
