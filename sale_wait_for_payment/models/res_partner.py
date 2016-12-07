# -*- coding: utf-8 -*-
# © 2016 Dreambits Technologies (http://www.dreambits.in)
# @author Karan Shah <admin@dreambits.in>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
from openerp import models, fields, api

_logger = logging.getLogger(__name__)


class CustomResPartner(models.Model):
    _inherit = "res.partner"

    @api.model
    @api.multi
    def get_whitelist_status(self):
        for partner in self:
            control_product = partner.env['ir.config_parameter'].\
                get_param('procurement_customer')
            return_value = False
            if control_product != 0:
                return_value = True
            partner.x_show_whitelist = return_value

    x_whitelist_blacklist = fields.Boolean("Blacklist")
    x_show_whitelist = fields.Boolean(compute=get_whitelist_status,
                                      store=False)
