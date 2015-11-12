# -*- coding: utf-8 -*-
###############################################################################
#
#   Module for Odoo
#   Copyright (C) 2015 Akretion (http://www.akretion.com).
#   @author Valentin CHEMIERE <valentin.chemiere@akretion.com>
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as
#   published by the Free Software Foundation, either version 3 of the
#   License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

from openerp import fields, api, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    base_price_unit = fields.Float()
    pricelist_id = fields.Many2one(related="order_id.pricelist_id")
    optional_bom_line_ids = fields.One2many(
        'sale.order.line.option',
        'sale_line_id',
        string='optional BoM Line',
        copy=True)

    def product_id_change(self, cr, uid, ids, pricelist, product,
                          qty=0,
                          uom=False,
                          qty_uos=0,
                          uos=False,
                          name='',
                          partner_id=False,
                          lang=False,
                          update_tax=True,
                          date_order=False,
                          packaging=False,
                          fiscal_position=False,
                          flag=False,
                          context=None):
        res = super(SaleOrderLine, self).product_id_change(
            cr, uid, ids, pricelist, product, qty, uom, qty_uos, uos, name,
            partner_id, lang, update_tax, date_order, packaging,
            fiscal_position, flag, context)
        if product:
            res['value']['base_price_unit'] = res['value']['price_unit']
            return res

    @api.onchange('optional_bom_line_ids', 'base_price_unit')
    def _onchange_option(self):
        final_options_price = 0
        for option in self.optional_bom_line_ids:
            final_options_price += option.line_price
            self.price_unit = final_options_price + self.base_price_unit


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.model
    def _prepare_vals_lot_number(self, order_line, index_lot):
        res = super(SaleOrder, self)._prepare_vals_lot_number(order_line,
                                                              index_lot)
        res['optional_bom_line_ids'] = [
            (6, 0, [line.id for line in order_line.optional_bom_line_ids])
        ]
        return res


class SaleOrderLineOption(models.Model):
    _name = 'sale.order.line.option'

    sale_line_id = fields.Many2one(
        'sale.order.line',
        required=True,
        ondelete='cascade',)
    bom_line_id = fields.Many2one('mrp.bom.line', 'Bom line', required=True)
    qty = fields.Integer(default=1)
    line_price = fields.Float(compute='_compute_price', store=True)

    @api.one
    @api.onchange('bom_line_id', 'qty')
    @api.depends('bom_line_id', 'qty')
    def _compute_price(self):
        option_price = 0
        if self.bom_line_id and self.sale_line_id.pricelist_id:
            option_price = self.sale_line_id.pricelist_id.with_context(
                {
                    'uom': self.bom_line_id.product_uom.id,
                    'date': self.sale_line_id.order_id.date_order,
                    'with_rm': self.sale_line_id.price_with_material,
                    'urgent': self.sale_line_id.order_id.urgent
                }).price_get(
                self.bom_line_id.product_id.id,
                self.bom_line_id.product_qty or 1.0,
                self.sale_line_id.order_id.partner_id.id
            )[self.sale_line_id.pricelist_id.id]
            option_price *= self.bom_line_id.product_qty * self.qty
        self.line_price = option_price
