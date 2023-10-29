# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class ResCompany(models.Model):

    _inherit = "res.company"

    pricelist_cache_by_date = fields.Boolean()

    # @api.depends("pricelist_cache_by_date")
    # def _onchange_pricelist_cache_by_date(self):
    # self.env["product.pricelist.cache"].cron_reset_pricelist_cache()
