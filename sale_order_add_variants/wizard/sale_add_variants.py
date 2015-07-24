# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Hugo Santos
#    Copyright 2015 FactorLibre
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
##############################################################################
import openerp.addons.decimal_precision as dp
from openerp import api, models, fields, _


class SaleAddVariants(models.TransientModel):
    _name = 'sale.add.variants'

    product_tmpl_id = fields.Many2one('product.template', string="Template",
                                      required=True)
    variant_line_ids = fields.One2many('sale.add.variants.line', 'wizard_id',
                                       string="Variant Lines")

    @api.multi
    def clear_previous_selections(self):
        self.mapped('variant_line_ids').unlink()

    @api.onchange('product_tmpl_id')
    def _onchange_product_tmpl_id(self):
        if self.product_tmpl_id:
            variant_lines = []
            for variant in self.product_tmpl_id.product_variant_ids:
                variant_lines.append([0, 0, {
                    'product_id': variant.id,
                    'product_uom_qty': 0,
                    'product_uom': variant.uom_id.id
                }])
            self.variant_line_ids = variant_lines

    @api.multi
    def add_to_order(self):
        context = self.env.context
        sale_order = self.env['sale.order'].browse(context.get('active_id'))
        for line in self.variant_line_ids:
            if not line.product_uom_qty:
                continue
            line_values = {
                'product_id': line.product_id.id,
                'product_uom_qty': line.product_uom_qty,
                'product_uom': line.product_uom.id,
                'order_id': sale_order.id
            }
            sale_order.order_line.create(line_values)

    @api.multi
    def add_to_order_continue(self):
        self.add_to_order()
        self.clear_previous_selections()
        return self.open_new_window()

    @api.multi
    def open_new_window(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'sale.add.variants',
            'name': _('Add Variants'),
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'nodestroy': True,
            'context': self.env.context
        }


class SaleAddVariantsLine(models.TransientModel):
    _name = 'sale.add.variants.line'

    wizard_id = fields.Many2one('sale.add.variants')
    product_id = fields.Many2one('product.product', string="Variant",
                                 required=True, readonly=True)
    product_uom_qty = fields.Float(
        string="Quantity", digits_compute=dp.get_precision('Product UoS'))
    product_uom = fields.Many2one('product.uom', string='Unit of Measure ',
                                  required=True)
