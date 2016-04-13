# -*- coding: utf-8 -*-
# © initOS GmbH 2016
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields


class PaymentAcquirer(models.Model):
    _inherit = 'payment.acquirer'

    payment_method_id = fields.Many2one('payment.method',
                                        'Payment Method',
                                        )
