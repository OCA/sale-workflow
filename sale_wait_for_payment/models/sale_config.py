# -*- coding: utf-8 -*-
# © 2016 Dreambits Technologies (http://www.dreambits.in)
# @author Karan Shah <admin@dreambits.in>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from openerp import api, fields, models

_logger = logging.getLogger(__name__)


class SaleConfigSettings(models.TransientModel):
    _inherit = 'sale.config.settings'

    default_procurement_product = fields.Selection(
        [
            (0, "No stop rules bases on Products"),
            (1, "Stop only for Blacklisted products only"),
        ], "Stop Procurement without payment for Products")

    default_procurement_customer = fields.Selection(
        [
            (0, "No stop rules bases on Customer"),
            (1, "Stop only for Blacklisted Customer only"),
        ], "Stop Procurement without payment for Customer")

    @api.multi
    def set_procurement_settings(self):
        self.ensure_one()
        conf = self.env['ir.config_parameter']
        conf.set_param('procurement_product', self.default_procurement_product)
        conf.set_param('procurement_customer',
                       self.default_procurement_customer)

    @api.model
    def get_default_procurement_product(self, fields):
        conf = self.env['ir.config_parameter']
        return {'default_procurement_product':
                conf.get_param('procurement_product'),
                'default_procurement_customer':
                conf.get_param('procurement_customer')}
