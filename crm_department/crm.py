# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2010 Camptocamp SA (http://www.camptocamp.com) 
# All Right Reserved
#
# Author : Joel Grand-guillaume (Camptocamp)
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

from osv import osv
from osv import fields

class crm_sales_team(osv.osv):
    _inherit = "crm.case.section"

    _columns = {
        'department_id': fields.many2one('hr.department', 'Department'),
    }
    _defaults = {
        'department_id': lambda s,cr,uid,c: s.pool.get('res.users').browse(cr,uid,uid).context_department_id.id,
    }

crm_sales_team()

class crm_lead(osv.osv):
    _inherit = "crm.lead"

    _columns = {
        'department_id': fields.related('section_id', 'department_id', type='many2one', relation='hr.department', \
            string='Department', store=True, readonly=True)
    }

crm_lead()

