# Copyright 2025 Akretion (https://www.akretion.com).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def action_open_delivery_wizard(self):
        res = super().action_open_delivery_wizard()
        res["context"]["price_include_taxes"] = self.pricelist_id and self.pricelist_id.price_include_taxes
        return res
    

