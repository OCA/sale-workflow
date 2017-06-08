# -*- coding: utf-8 -*-
from openerp.osv import orm, fields


class AccountInvoice(orm.Model):
    _inherit = "account.invoice"
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
