# -*- coding: utf-8 -*-
# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.tools import safe_eval


class SaleConfigSettings(models.TransientModel):

    _inherit = 'sale.config.settings'

    product_blacklist_global_mandatory = fields.Boolean(
        string="Products must have global settings defined",
        help="If checked, products must have either globally available "
             "option enabled, either at least one blacklisted country."
    )

    @api.multi
    def set_product_blacklist_global_mandatory(self):
        self.ensure_one()

        icp = self.env['ir.config_parameter']
        icp.set_param(
            'sale_product_country_filter.blacklist_global_mandatory',
            repr(self.product_blacklist_global_mandatory))

    @api.multi
    def get_product_blacklist_global_mandatory(self):
        self.ensure_one()

        icp = self.env['ir.config_parameter']
        icp.get_param(
            safe_eval(
                icp.get_param(
                    'sale_product_country_filter.blacklist_global_mandatory',
                    'False')))
