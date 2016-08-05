# -*- coding: utf-8 -*-
# © initOS GmbH 2016
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, api, fields, _


class PaymentMethod(models.Model):
    _inherit = 'payment.method'

    @api.model
    def _get_allow_automatic_payment_selection(self):
        return [('never', _('never')),
                ('none', _('no limitation')),
                ]

    allow_automatic_payment = fields.Selection(
        '_get_allow_automatic_payment_selection',
        string='Allow Automatic Payment',
        default='none',
        required=True,
    )
