#
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2013 Agile Business Group sagl (<http://www.agilebg.com>)
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

from openerp import models, api


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.one
    def copy(self, default=None):
        if default is None:
            default = {}
        default['name'] = '/'
        return super(SaleOrder, self).copy(default=default)

    @api.model
    def create(self, vals):
        if vals.get('name', '/') == '/':
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'sale.quotation') or '/'
        return super(SaleOrder, self).create(vals)

    @api.multi
    def action_wait(self):
        if super(SaleOrder, self).action_wait():
            for sale in self:
                quo = sale.name
                sale.write({
                    'origin': quo,
                    'name': self.env['ir.sequence'].next_by_code(
                        'sale.order')
                })
        return True
