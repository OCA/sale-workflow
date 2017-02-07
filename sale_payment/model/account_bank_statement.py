# -*- coding: utf-8 -*-
# Copyright (C) 2016  Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api


class AccountBankStatementLine(models.Model):
    _inherit = 'account.bank.statement.line'

    sale_ids = fields.Many2many(
        comodel_name='sale.order',
        string='Sales Orders')

    def process_reconciliation(self, counterpart_aml_dicts=None,
                               payment_aml_rec=None, new_aml_dicts=None):
        if new_aml_dicts and self.sale_ids:
            for aml_dict in new_aml_dicts:
                aml_dict['sale_ids'] = [(6, 0, self.sale_ids.ids)]
        return super(AccountBankStatementLine, self).process_reconciliation(
            counterpart_aml_dicts=counterpart_aml_dicts,
            payment_aml_rec=payment_aml_rec, new_aml_dicts=new_aml_dicts)

    @api.onchange('sale_ids')
    def onchange_sale_ids(self):
        if self.sale_ids:
            self.partner_id = self.sale_ids[0].partner_id.id
            self.account_id = self.partner_id.\
                property_account_receivable_id.id
