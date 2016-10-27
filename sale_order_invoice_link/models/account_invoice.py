# -*- coding: utf-8 -*-
# Copyright (C) 2016  KMEE - Hendrix Costa
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import api, fields, models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    sale_ids = fields.Many2many(
        string='Sale Orders2',
        comodel_name='sale.order',
        compute="_compute_sale_ids"
    )

    @api.multi
    def _compute_sale_ids(self):
        for invoice in self:
            invoice.sale_ids = self.env['sale.order']
            for line in invoice.invoice_line_ids:
                invoice.sale_ids |= line.sale_line_ids.mapped('order_id')
