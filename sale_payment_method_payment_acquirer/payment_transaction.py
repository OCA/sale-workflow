# -*- coding: utf-8 -*-
# © initOS GmbH 2016
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models
from openerp import SUPERUSER_ID


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    def form_feedback(self, cr, uid, data, acquirer_name, context=None):
        """ Override to create automatic payments for order,
         if transaction is done. """

        res = super(PaymentTransaction, self).\
            form_feedback(cr, uid, data, acquirer_name, context=context)
        # Order already confirmed. (cmp. module website_sale)

        tx = None
        # fetch the tx, check its state, confirm the potential SO
        tx_find_method_name = '_%s_form_get_tx_from_data' % acquirer_name
        if hasattr(self, tx_find_method_name):
            tx = getattr(self, tx_find_method_name)(cr,
                                                    uid,
                                                    data,
                                                    context=context)
        if tx and tx.state == 'done' and tx.sale_order_id:
            self.pool['sale.order'].automatic_payment(cr,
                                                      SUPERUSER_ID,
                                                      [tx.sale_order_id.id],
                                                      context=context,
                                                      amount=tx.amount)

        return res
