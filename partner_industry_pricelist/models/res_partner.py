# Copyright 2021 KMEE
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class ResPartner(models.Model):

    _inherit = 'res.partner'

    @api.onchange('industry_id')
    def _onchange_industry_id(self):
        if self.industry_id and self.industry_id.pricelist_id:
            # property_product_pricelist is a fake property on v12.
            self.property_product_pricelist = self.industry_id.pricelist_id
