# Copyright 2015 Opener B.V. (<https://opener.am>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    incoterm_address_id = fields.Many2one(
        comodel_name="res.partner",
        string="Incoterm Address",
    )

    @api.onchange("partner_id")
    def onchange_partner_id(self):
        res = super().onchange_partner_id()
        self.update(
            {
                "incoterm": self.partner_id.sale_incoterm_id.id,
                "incoterm_address_id": self.partner_id.sale_incoterm_address_id.id,
            }
        )
        return res
