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
        print "_skip bom line"
        import ipdb; ipdb.set_trace()
        res = super(Bom, self)._skip_bom_line(line, product)
        prod_id = self.env.context['production_id']
        prod = self.env['mrp.production'].browse(prod_id)
        if line in line.lot_id.optionnal_bom_line_ids:
            res = True
        else:
            res = False
        return res
