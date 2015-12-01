# -*- coding: utf-8 -*-
#
#
#    Copyright Camptocamp SA
#    @author: Guewen Baconnier
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#
from openerp import models, fields, api


class SaleExceptionConfirm(models.TransientModel):

    _name = 'sale.exception.confirm'

    sale_id = fields.Many2one('sale.order', 'Sale')
    exception_ids = fields.Many2many('sale.exception',
                                     string='Exceptions to resolve',
                                     readonly=True)
    ignore = fields.Boolean('Ignore Exceptions')

    @api.model
    def default_get(self, field_list):
        res = super(SaleExceptionConfirm, self).default_get(field_list)
        order_obj = self.env['sale.order']
        sale_id = self._context.get('active_ids')
        assert len(sale_id) == 1, "Only 1 ID accepted, got %r" % sale_id
        sale_id = sale_id[0]
        sale = order_obj.browse(sale_id)
        exception_ids = [e.id for e in sale.exception_ids]
        res.update({'exception_ids': [(6, 0, exception_ids)]})
        res.update({'sale_id': sale_id})
        return res

    @api.one
    def action_confirm(self):
        if self.ignore:
            self.sale_id.ignore_exceptions = True
        return {'type': 'ir.actions.act_window_close'}
