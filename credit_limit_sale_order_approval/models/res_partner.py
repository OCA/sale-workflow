# -*- coding: utf-8 -*-
################################################################
#    License, author and contributors information in:          #
#    __openerp__.py file at the root folder of this module.    #
################################################################

from openerp import models, fields, api
import logging
_logger = logging.getLogger(__name__)


# RES.PARTNER
class res_partner(models.Model):
    _inherit = 'res.partner'

    @api.multi
    @api.depends('credit', 'credit_limit')
    def _get_available_credit(self):
        for partner in self:
            available_credit = partner.credit_limit - partner.credit
            if partner.set_credit_limit and available_credit > 0:
                partner.available_credit = available_credit
            else:
                partner.available_credit = 0

    set_credit_limit = fields.Boolean(string='Set credit limit')

    available_credit = fields.Float(string='Available credit',
                                    compute=_get_available_credit)

    @api.onchange('set_credit_limit')
    def onchange_set_credit_limit(self):
        if not self.set_credit_limit:
            self.credit_limit = 0
