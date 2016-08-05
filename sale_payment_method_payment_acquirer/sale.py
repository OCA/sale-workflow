# -*- coding: utf-8 -*-
# © initOS GmbH 2016
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.onchange('payment_acquirer_id')
    def onchange_payment_acquirer_id(self):
        #change payment method according to payment_acquirer_id
        if not self.payment_acquirer_id:
            return
        method = self.payment_acquirer_id.payment_method_id
        if method:
            self.payment_method_id = method
