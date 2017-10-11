# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def _get_draft_invoices(self, invoices, references):
        if self.env.context.get('merge_draft_invoice', False):
            invoices, references = super(SaleOrder, self)._get_draft_invoices(
                invoices, references)
            draft_inv = self.env['account.invoice'].search([('state', '=',
                                                             'draft')])
            for inv in draft_inv:
                lines = inv.invoice_line_ids.filtered(
                    lambda l: l.sale_line_ids)
                if lines:
                    ref_order = lines[0].sale_line_ids[0].order_id
                    group_inv_key = self._get_invoice_group_key(ref_order)
                    references[inv] = ref_order
                    invoices[group_inv_key] = inv
            return invoices, references
        else:
            return super(SaleOrder, self)._get_draft_invoices(
                invoices, references)
