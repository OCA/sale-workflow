# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from openerp import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    state = fields.Selection(
        selection_add=[('to_approve', 'To Approve')]
    )

    @api.multi
    def is_amount_to_approve(self):
        currency = self.env.user.company_id.currency_id
        limit_amount = self.company_id.so_double_validation_amount
        limit_amount = currency.compute(limit_amount, self.currency_id)
        return self.amount_total >= limit_amount

    @api.multi
    def is_to_approve(self):
        return (self.company_id.so_double_validation == 'two_step' and
                self.is_amount_to_approve() and
                not self.user_has_groups('base.group_sale_manager'))

    @api.multi
    def action_confirm(self):
        to_approve = self.env['sale.order']
        to_confirm = self.env['sale.order']
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
