# -*- coding: utf-8 -*-
##############################################################################
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
##############################################################################
from openerp.osv import orm, fields


class SaleExceptionConfirm(orm.TransientModel):

    _name = 'sale.exception.confirm'

    _columns = {
        'sale_id': fields.many2one('sale.order', 'Sale'),
        'exception_ids': fields.many2many('sale.exception',
                                          string='Exceptions to resolve',
                                          readonly=True),
        'ignore': fields.boolean('Ignore Exceptions'),
    }

    def default_get(self, cr, uid, fields, context=None):
        if context is None:
            context = {}
        res = super(SaleExceptionConfirm, self).default_get(
            cr, uid, fields, context=context)
        order_obj = self.pool.get('sale.order')
        sale_id = context.get('active_ids')
        assert len(sale_id) == 1, "Only 1 ID accepted, got %r" % sale_id
        sale_id = sale_id[0]
        sale = order_obj.browse(cr, uid, sale_id, context=context)
        exception_ids = [e.id for e in sale.exceptions_ids]
        res.update({'exception_ids': [(6, 0, exception_ids)]})
        res.update({'sale_id': sale_id})
        return res

    def action_confirm(self, cr, uid, ids, context=None):
        if hasattr(ids, '__iter__'):
            assert len(ids) == 1, "Only 1 ID accepted, got %r" % ids
            ids = ids[0]
        form = self.browse(cr, uid, ids, context=context)
        if form.ignore:
            self.pool.get('sale.order').write(
                cr, uid,
                form.sale_id.id,
                {'ignore_exceptions': True},
                context=context)
        return {'type': 'ir.actions.act_window_close'}
