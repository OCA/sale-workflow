# -*- coding: utf-8 -*-
# © 2016 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import api, fields, models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    cancelled_by_refund = fields.Boolean('Cancelled by refund',
                                         compute='_is_cancelled_by_refund')

    @api.one
    @api.depends('payment_ids')
    def _is_cancelled_by_refund(self):
        cancelled = False
        for move in self.payment_ids:
            if move.invoice and move.invoice.type == 'out_refund':
                cancelled = True
                break
        self.cancelled_by_refund = cancelled
