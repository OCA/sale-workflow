# Copyright 2018 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    sale_discount = fields.Float(
        string="Discount",
        digits="Discount",
        company_dependent=True,
    )

    @api.model
    def _commercial_fields(self):
        return super()._commercial_fields() + ["sale_discount"]
