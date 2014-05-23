# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Joël Grand-guillaume (Camptocamp)
#    Contributor: Yannick Vaucher (Camptocamp)
#    Contributor: Eficent
#    Copyright 2011 Camptocamp SA
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

class CrmSalesTeam(orm.Model):
    _inherit = "crm.case.section"
    _columns = {
        'department_id': fields.many2one('hr.department', 'Department'),
        }

    def _get_department(self, cr, uid, ids, context=None):
        employee_obj = self.pool['hr.employee']
        department_id = False
        employee_ids = employee_obj.search(cr, uid, [('user_id','=', uid)])
        if employee_ids:
            department_id = employee_obj.browse(cr, uid, 
                                                employee_ids[0], 
                                                context=context).department_id.id
        return department_id

    _defaults = {
        'department_id': _get_department,
        }


class CrmLead(orm.Model):
    _inherit = "crm.lead"

    def on_change_user(self, cr, uid, ids, user_id, context=None):
        """ Updates res dictionary with the department 
        corresponding to the section """
        employee_obj = self.pool['hr.employee']
        res = {}        
        res['department_id'] = False
        if user_id:
            employee_ids = employee_obj.search(cr, uid, 
                                               [('user_id','=',user_id)],
                                                context=context)
            for employee in employee_obj.browse(cr, uid, 
                                               employee_ids, context=context):
                if employee.department_id.id:
                    res['department_id'] = employee.department_id.id
        return {'value': res}
    
    _columns = {
        'department_id': fields.many2one('hr.department', 'Department'),
        }


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
