# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import math


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    payment_signal = fields.Monetary(string='Signal Quotation', store=True)

    rest_pay = fields.Monetary(string='Rest to pay',
                               store=True,
                               compute='_compute_rest_pay',
                               compute_sudo=False)

    @api.onchange('amount_total')
    def _pay_signal(self):
        """Method to calculate payment_signal and rest_pay
        if you change amount_total"""
        for order in self:
            percent = self.env.user.company_id.default_signal
            payment_signal = math.ceil(order.amount_total * percent / 100)
            rest_pay = order.amount_total - payment_signal
            order.update({'payment_signal': payment_signal,
                          'rest_pay': rest_pay,
                          })

    @api.depends('payment_signal')
    def _compute_rest_pay(self):
        """Method to calculate rest_pay if we change payment_signal,
        and verify that we do not make mistakes"""
        for order in self:
            if not 0 <= order.payment_signal <= order.amount_total:
                raise ValidationError(_("Error! The payment signal can not be"
                                        " less than 0 nor more than total."))
            rest_pay = order.amount_total - order.payment_signal
            order.update({'rest_pay': rest_pay, })

    @api.multi
    def button_dummy(self):
        """We expanded the buttton_dummy method"""
        res = super(SaleOrder, self).button_dummy()
        for order in self:
            percent = self.env.user.company_id.default_signal
            payment_signal = math.ceil(order.amount_total * percent / 100)
            rest_pay = order.amount_total - payment_signal
            order.update({'payment_signal': payment_signal,
                          'rest_pay': rest_pay, })
        return res

    @api.constrains('payment_signal')
    def _check_payment_signal(self):
        """Checking the values"""
        if not 0 <= self.payment_signal <= self.amount_total:
            raise ValidationError(_("Error! The payment signal can not be"
                                    " less than 0 nor more than total."))
