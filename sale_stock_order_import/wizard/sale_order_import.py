# -*- coding: utf-8 -*-
# © 2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, api


class SaleOrderImport(models.TransientModel):
    _inherit = 'sale.order.import'

    @api.model
    def _prepare_order(self, parsed_order, price_source):
        so_vals = super(SaleOrderImport, self)._prepare_order(
            parsed_order, price_source)
        incoterm = self.env['business.document.import']._match_incoterm(
            parsed_order.get('incoterm'), parsed_order['chatter_msg'])
        if incoterm:
            so_vals['incoterm'] = incoterm.id
        return so_vals

    @api.model
    def _prepare_update_order_vals(self, parsed_order, order, partner):
        so_vals = super(SaleOrderImport, self)._prepare_update_order_vals(
            parsed_order, order, partner)
        incoterm = self.env['business.document.import']._match_incoterm(
            parsed_order.get('incoterm'), parsed_order['chatter_msg'])
        if incoterm:
            so_vals['incoterm'] = incoterm.id
        return so_vals
