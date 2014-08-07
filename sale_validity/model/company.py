# -*- coding: utf-8 -*-
#
#
#    Copyright (C) 2014 Akretion (http://www.akretion.com)
#    @author Alexis de Lattre <alexis.delattre@akretion.com>
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

from openerp.osv import fields, orm


class res_company(orm.Model):
    _inherit = "res.company"

    _columns = {
        'default_sale_order_validity_days': fields.integer(
            "Default Validity of Sale Orders (in days)",
            help="By default, the validity date of sale orders will be "
            "the date of the sale order plus the number of days defined "
            "in this field. If the value of this field is 0, the sale orders "
            "will not have a validity date by default."),
    }

    _sql_constraints = [
        ('sale_order_validity_days_positive',
         'CHECK (default_sale_order_validity_days >= 0)',
         "The value of the field 'Default Validity Duration of Sale Orders' "
         "must be positive or 0."),
    ]
