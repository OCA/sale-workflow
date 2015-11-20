# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
# Author: Guewen Baconnier, Leonardo Pistone
# Copyright 2014-2015 Camptocamp SA

from openerp import models, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.onchange('section_id')
    def section_id_set_section_id_default(self):
        self.payment_term = self.section_id.payment_term_id
        self.fiscal_position = self.section_id.fiscal_position_id
        self.pricelist_id = self.section_id.pricelist_id
        self.warehouse_id = self.section_id.warehouse_id
        self.project_id = self.section_id.account_analytic_id

    @api.onchange('user_id')
    def user_id_change_section_id(self):
        self.section_id = self.user_id.default_section_id

    @api.model
    def _prepare_invoice(self, order, lines):
        invoice_data = super(SaleOrder, self)._prepare_invoice(order, lines)

        if order.section_id:
            invoice_data['journal_id'] = order.section_id.journal_id.id
        return invoice_data
