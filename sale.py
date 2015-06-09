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


class SaleOrderLineOption(models.Model):
    _name = 'sale.order.line.option'

    sale_line_id = fields.Many2one('sale.order.line')
    product_id = fields.Many2one('product.product', 'Option')
    uom_qty = fields.Integer(default=1)
    price_unit = fields.Float()
    note = fields.Text()

    @api.onchange('product_id')
    def _onchange_product(self):
        if self.product_id:
            pricelist = self.env['product.pricelist'].browse(self.env.context['pricelist_id'])
            price = pricelist.price_get(
                self.product_id.id,
                self.uom_qty or 1.0,
                self.sale_line_id.order_id.partner_id.id,
            )[pricelist.id]
            self.price_unit = price


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    base_price_unit = fields.Float()
    option_ids = fields.One2many('sale.order.line.option', 'sale_line_id',
                                 'Options')


    def product_id_change(self, cr, uid, ids, pricelist, product, qty=0,
                          uom=False, qty_uos=0, uos=False, name='',
                          partner_id=False, lang=False, update_tax=True,
                          date_order=False, packaging=False,
                          fiscal_position=False, flag=False, context=None):
        res = super(SaleOrderLine, self).product_id_change(cr, uid, ids,
                                                           pricelist,
                                                           product, qty, uom,
                                                           qty_uos, uos, name,
                                                           partner_id, lang,
                                                           update_tax,
                                                           date_order,
                                                           packaging,
                                                           fiscal_position,
                                                           flag, context
                                                           )
        if pricelist and product:
            price = self.pool.get('product.pricelist').price_get(cr, uid, [pricelist],
                    product, qty or 1.0, partner_id, {
                        'uom': uom or res['value'].get('product_uom'),
                        'date': date_order,
                        })[pricelist]
            res['value']['base_price_unit'] = price
        return res

    @api.onchange('option_ids')
    def _onchange_option(self):
        option_price = 0
        for option in self.option_ids:
            option_price += option.price_unit * option.uom_qty
        self.price_unit = option_price + self.base_price_unit
