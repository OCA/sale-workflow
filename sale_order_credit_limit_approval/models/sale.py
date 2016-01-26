# -*- coding: utf-8 -*-
################################################################
#    License, author and contributors information in:          #
#    __openerp__.py file at the root folder of this module.    #
################################################################

from openerp import models, fields, api, _
import logging
_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _confirmation_is_allowed(self):
        self.ensure_one()
        if self.partner_id and self.partner_id.set_credit_limit and (
           (self.amount_total + self.partner_id.credit) >
           self.partner_id.credit_limit):
            return False
        else:
            return True

    @api.multi
    @api.depends('amount_total', 'partner_id.credit',
                 'partner_id.credit_limit')
    def _compute_confirmation_allowed(self):
        for sale_order in self:
            sale_order.confirmation_allowed = \
                sale_order._confirmation_is_allowed()

    @api.multi
    @api.depends('amount_total', 'partner_id.credit',
                 'partner_id.credit_limit')
    def _compute_warning(self):
        for sale_order in self:
            if sale_order._confirmation_is_allowed():
                sale_order.credit_limit_warning = ''
            else:
                sale_order.credit_limit_warning = _(
                    'Contact credit limit exceeded.')

    confirmation_allowed = fields.Boolean(
        string='Confirmation allowed', compute=_compute_confirmation_allowed)
    credit_limit_warning = fields.Char(string='Warning',
                                       compute=_compute_warning)
    state = fields.Selection(
        selection_add=[('waiting_for_approval', 'Waiting for approval')])
