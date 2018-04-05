# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    @api.model
    def _get_advance_payment_method(self):
        """We modified the method to add the 'fixed' option
        in case of being in 'draft' or 'sent'."""
        res = super(SaleAdvancePaymentInv, self)\
            ._get_advance_payment_method()
        state_obj = self.env['sale.order'].browse(
            self._context.get('active_ids')).state
        if state_obj in ('draft', 'sent'):
            return 'fixed'
        return res

    advance_payment_method = fields.Selection([
        ('fixed', 'Down payment (fixed amount)'),
        ('percentage', 'Down payment (percentage)'),
        ('all', 'Invoiceable lines (deduct down payments)'),
        ('delivered', 'Invoiceable lines')],
        string='What do you want to invoice?',
        default=_get_advance_payment_method,
        required=True)

    @api.multi
    @api.onchange('advance_payment_method')
    def onchange_advance_payment_method(self):
        """We extend the functionality of onchange_advance_payment_method"""
        super(SaleAdvancePaymentInv, self)\
            .onchange_advance_payment_method()
        sale_obj = self.env['sale.order'].browse(
            self._context.get('active_ids'))
        if self.advance_payment_method == 'percentage':
            self.amount = sale_obj.user_id.company_id.default_signal
            return {}
        if self.advance_payment_method == 'fixed':
            self.amount = sale_obj.payment_signal
            return {}
