# -*- coding: utf-8 -*-
#
#    Author: Alexandre Fayolle
#    Copyright 2014 Camptocamp SA
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#
from openerp import models, fields, api


class QuotationSourcingWizard(models.TransientModel):
    _name = 'sale.order.sourcing'
    sale_id = fields.Many2one('sale.order', string='Sale Order')
    line_ids = fields.One2many('sale.order.line.sourcing', 'wizard_id',
                               string='Lines')
    _rec_name = 'sale_id'

    @api.multi
    def action_done(self):
        self.ensure_one()
        for line in self.line_ids:
            line.so_line_id.sourced_by = line.po_line_id
        return self[0].sale_id.action_button_confirm()


class QuotationLineSource(models.TransientModel):
    _name = 'sale.order.line.sourcing'
    wizard_id = fields.Many2one('sale.order.sourcing', string='Wizard')
    so_line_id = fields.Many2one('sale.order.line', string='Sale Order Line')
    product_id = fields.Many2one('product.product',
                                 string='Product',
                                 related=('so_line_id', 'product_id'))
    po_line_id = fields.Many2one('purchase.order.line', string='Sourced By')
