# -*- coding: utf-8 -*-
# Copyright 2017-2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, models, _
from odoo.tools import float_compare


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def _setup_fields(self, partial):
        super(SaleOrder, self)._setup_fields(partial)
        selection = self._fields['state'].selection
        position = 0
        exists = False
        for idx, (state, __) in enumerate(selection):
            if state == 'draft':
                position = idx
            elif state == 'to_approve':
                exists = True
        if not exists:
            selection.insert(position + 1, ('to_approve', _('To Approve')))

    @api.multi
    def is_amount_to_approve(self):
        currency = self.company_id.currency_id
        limit_amount = self.company_id.so_double_validation_amount
        limit_amount = currency.compute(limit_amount, self.currency_id)
        rounding = self.currency_id.rounding
        return float_compare(
            limit_amount, self.amount_total, precision_rounding=rounding) <= 0

    @api.multi
    def is_to_approve(self):
        return (self.company_id.so_double_validation == 'two_step' and
                self.is_amount_to_approve() and
                not self.user_has_groups('sales_team.group_sale_manager'))

    @api.multi
    def action_confirm(self):
        to_approve = self.env['sale.order'].browse()
        to_confirm = self.env['sale.order'].browse()
        for order in self:
            if order.is_to_approve():
                to_approve |= order
            else:
                to_confirm |= order
        to_approve.write({'state': 'to_approve'})

        if to_confirm:
            return super(SaleOrder, to_confirm).action_confirm()
        return True

    @api.multi
    def action_approve(self):
        return super(SaleOrder, self).action_confirm()
