# -*- coding: utf-8 -*-
# © 2016 Dreambits Technologies (http://www.dreambits.in)
# @author Karan Shah <admin@dreambits.in>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api
import logging

_logger = logging.getLogger(__name__)

class CustomProductProduct(models.Model):
    _inherit = "product.template"

    @api.model
    @api.multi
    def get_whitelist_status(self):
        for product in self:
            control_product = product.env['ir.config_parameter'].get_param('procurement_product')
            return_value = False
            if control_product!=0:
                return_value = True
            product.x_show_whitelist = return_value

    x_whitelist_blacklist = fields.Boolean("Blacklist")
    x_show_whitelist = fields.Boolean(compute=get_whitelist_status,store=False)
