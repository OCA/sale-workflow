# Copyright 2026 Tecnativa - Pilar Vargas
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _get_mandatory_partner_fields(self, country_id=False):
        required = ["phone", "vat", "street", "city", "country_id"]
        if country_id:
            country = self.env["res.country"].browse(country_id)
            if country.state_required:
                required += ["state_id"]
        return required

    def _check_partner_mandatory_fields(self, partner):
        self.ensure_one()
        fields_required = self._get_mandatory_partner_fields(partner.country_id.id)
        return all(partner.read(fields_required)[0].values())
