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
    optionnal_bom_line_ids = fields.Many2many('mrp.bom.line',
                                       'sale_line_bom_line',
                                       'sale_line_id',
                                       'bom_line_id',
                                       'Optionnal BoM Line'
                                       )

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
        if product:
            res['value']['base_price_unit'] = res['value']['price_unit']
        return res

    @api.onchange('optionnal_bom_line_ids', 'base_price_unit')
    def _onchange_option(self):
        option_price = 0
        final_options_price = 0
        for option in self.optionnal_bom_line_ids:
            option_price = self.pool.get('product.pricelist').price_get(
                    self.env.cr,
                    self.env.uid,
                    [self.order_id.pricelist_id.id],
                    option.product_id.id,
                    option.product_qty or 1.0,
                    self.order_id.partner_id.id,
                    {
                        'uom': option.product_uom.id ,
                        'date': self.order_id.date_order,
                    })[self.order_id.pricelist_id.id]
            option_price = option_price * option.product_qty
            final_options_price += option_price
        self.price_unit = final_options_price + self.base_price_unit


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.model
    def _prepare_vals_lot_number(self, order_line_id, index_lot):
        res = super(SaleOrder, self)._prepare_vals_lot_number(order_line_id,
                                                              index_lot
                                                              )
        order_line = self.env['sale.order.line'].browse(order_line_id)
        res['optionnal_bom_line_ids'] = [line.id for line in order_line.optionnal_bom_line_ids]
        return res
