# -*- coding: utf-8 -*-
from openerp.osv import fields, orm


class SaleOrder(orm.Model):
    _inherit = 'sale.order'
    _columns = {
        'department_id': fields.many2one('hr.department', 'Department'),
    }

    def _get_department(self, cr, uid, ids, context=None):
        employee_obj = self.pool['hr.employee']
        department_id = False
        employee_ids = employee_obj.search(cr, uid, [('user_id', '=', uid)],
                                           context=context)
        if employee_ids:
            employee = employee_obj.browse(cr, uid, employee_ids[0],
                                           context=context)
            if employee.department_id:
                department_id = employee.department_id.id
        return department_id

    _defaults = {
        'department_id': _get_department,
    }

    def _make_invoice(self, cr, uid, order, lines, context=None):
        invoice_obj = self.pool['account.invoice']
        res = super(SaleOrder, self)._make_invoice(cr, uid, order,
                                                   lines, context=context)
        invoice_obj.write(cr, uid, res,
                          {'department_id': order.department_id.id},
                          context=context)
        return res
