# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Joël Grand-guillaume (Camptocamp)
#    Copyright 2010 Camptocamp SA
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
from openerp.osv import orm, fields

class SaleOrder(orm.Model):
    _inherit = 'sale.order'
    _columns = {
        'department_id': fields.many2one('hr.department', 'Department'),
        }

    def _get_department(self, cr, uid, ids, context=None):
        employee_obj = self.pool.get('hr.employee')
        department_id = False
        employee_ids = employee_obj.search(
                cr, uid,
                [('user_id','=', uid)],
                context=context)
        if employee_ids:
            department_id = employee_obj.browse(
                    cr, uid, employee_ids[0],
                    context=context).department_id.id
        return department_id

    _defaults = {
        'department_id': _get_department,
        }

    def _make_invoice(self, cr, uid, order, lines, context=None):
        invoice_obj = self.pool.get('account.invoice')
        res = super(SaleOrder, self)._make_invoice(
                cr, uid, order,
                lines, context=context)
        invoice_obj.write(
                cr, uid, res,
                {'department_id': order.department_id.id},
                context=context)
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
