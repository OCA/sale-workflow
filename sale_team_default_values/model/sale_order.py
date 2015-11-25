# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
# Author: Guewen Baconnier, Leonardo Pistone
# Copyright 2014-2015 Camptocamp SA

from openerp import models, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.onchange('section_id')
    def onchange_section_id(self):
        for field in self._propagate_fields():
            if self.section_id[field]:
                setattr(self, field, self.section_id[field])

    @api.onchange('user_id')
    def user_id_change_section_id(self):
        self.section_id = self.user_id.default_section_id

    @api.model
    def _prepare_invoice(self, order, lines):
        invoice_data = super(SaleOrder, self)._prepare_invoice(order, lines)

        if order.section_id and order.section_id.journal_id:
            invoice_data['journal_id'] = order.section_id.journal_id.id
        return invoice_data

    @api.model
    def _propagate_fields(self):
        return [
            'payment_term',
            'fiscal_position',
            'pricelist_id',
            'warehouse_id',
            'project_id',
        ]
