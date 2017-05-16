# -*- coding: utf-8 -*-
# © initOS GmbH 2016
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields


class PaymentMethod(models.Model):
    _inherit = 'payment.method'

    acquirer_id = fields.One2many('payment.acquirer',
                                  'payment_method_id',
                                  'Acquirer',
                                  required=False,)
