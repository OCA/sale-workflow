# -*- coding: utf-8 -*-
#
#
#    OpenERP, Open Source Management Solution
#    Authors: Raphaël Valyi, Renato Lima
#    Copyright (C) 2011 Akretion LTDA.
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

from openerp import models, fields


class SaleException(models.Model):
    _name = 'sale.exception'
    _description = "Sale Exceptions"
    _order = 'active desc, sequence asc'

    name = fields.Char('Exception Name', required=True, translate=True)
    description = fields.Text('Description', translate=True)
    sequence = fields.Integer(
        string='Sequence',
        help="Gives the sequence order when applying the test")
    model = fields.Selection(
        [('sale.order', 'Sale Order'),
         ('sale.order.line', 'Sale Order Line')],
        string='Apply on', required=True)
    active = fields.Boolean('Active')
    code = fields.Text(
        'Python Code',
        help="Python code executed to check if the exception apply or "
             "not. The code must apply block = True to apply the "
             "exception.",
        default="""
# Python code. Use failed = True to block the sale order.
# You can use the following variables :
#  - self: ORM model of the record which is checked
#  - order or line: browse_record of the sale order or sale order line
#  - object: same as order or line, browse_record of the sale order or
#    sale order line
#  - pool: ORM model pool (i.e. self.pool)
#  - time: Python time module
#  - cr: database cursor
#  - uid: current user id
#  - context: current context
""")
    sale_order_ids = fields.Many2many(
        'sale.order',
        'sale_order_exception_rel', 'exception_id', 'sale_order_id',
        string='Sale Orders',
        readonly=True)
