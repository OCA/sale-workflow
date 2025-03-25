# Copyright 2025 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    is_dropship_address = fields.Boolean(string="Dropship Address")

    def _get_complete_name(self):
        res = super()._get_complete_name()
        if not self.is_dropship_address or not self.name or not self.type == "delivery":
            return res
        return self.name.strip()
