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


class BomOption(models.Model):
    _name = "mrp.bom.line.option"

    @api.model
    def _get_type(self):
        selection = (
            ('select', 'selection'),
            ('multiselect', 'multi-selection'),
            ('required', 'Required'),
        )
        return selection

    name = fields.Char()
    sequence = fields.Integer()
    type = fields.Selection('_get_type')


class BomLine(models.Model):
    _inherit = "mrp.bom.line"

    option_id = fields.Many2one('mrp.bom.line.option', 'Option')


class Bom(models.Model):
    _inherit = "mrp.bom"

    @api.model
    def _skip_bom_line(self, line, product):
        res = super(Bom, self)._skip_bom_line(line, product)
        prod_id = self.env.context['production_id']
        prod = self.env['mrp.production'].browse(prod_id)
        bom_lines = [option.bom_line_id
                     for option in prod.lot_id.optionnal_bom_line_ids]
        if not line.option_id\
                or line.option_id.type == 'required'\
                or line in bom_lines:
            return res
        else:
            return True

    @api.model
    def _prepare_conssumed_line(self, bom_line, quantity, product_uos_qty):
        vals = super(Bom, self)._prepare_conssumed_line(bom_line, quantity, product_uos_qty)
        prod = self.env['mrp.production'].browse(self.env.context['production_id'])
        for option in prod.lot_id.optionnal_bom_line_ids:
            if option.bom_line_id == bom_line:
                vals['product_qty'] = vals['product_qty'] * option.qty
        return vals

class StockProductionLot(models.Model):
    _inherit = 'stock.production.lot'

    optionnal_bom_line_ids = fields.Many2many('sale.order.line.option',
                                              'option_lot_rel',
                                              'lot_id',
                                              'option_id',
                                              'Optionnal bom lines')
