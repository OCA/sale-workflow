# -*- encoding: utf-8 -*-
###############################################################################
#
#    sale_automatic_workflow for OpenERP
#    Copyright (C) 2011 Akretion Sébastien BEAU <sebastien.beau@akretion.com>
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
###############################################################################

from openerp.osv import orm, fields


class sale_workflow_process(orm.Model):
    """
    A workflow process is the setup of the automation of a sales order.

    Each sales order can be linked to a workflow process.
    Then, the options of the workflow will change how the sales order
    behave, and how it is automatized.

    A workflow process may be linked with a Sales payment method, so
    each time a payment method is used, the workflow will be applied.
    """
    _name = "sale.workflow.process"
    _description = "Sale Workflow Process"

    _columns = {
        'name': fields.char('Name', size=64),
        'picking_policy': fields.selection(
            [('direct', 'Deliver each product when available'),
             ('one', 'Deliver all products at once')],
            string='Shipping Policy'),
        'order_policy': fields.selection([('prepaid', 'Before Delivery'),
                                          ('manual', 'On Demand'),
                                          ('picking', 'On Delivery Order')],
                                         string='Invoice Policy'),
        'invoice_quantity': fields.selection(
            [('order', 'Ordered Quantities'),
             ('procurement', 'Shipped Quantities')],
            string='Invoice on'),
        'validate_order': fields.boolean('Validate Order'),
        'create_invoice_on': fields.selection(
            [('manual', 'No automatic invoice'),
             ('on_order_confirm', 'On confirmation of Sale Order'),
             ('on_picking_done', 'After Delivery')],
            required=True,
            string='Create Invoice'),
        'validate_invoice': fields.boolean('Validate Invoice'),
        'validate_picking': fields.boolean('Confirm and Close Picking'),
        'invoice_date_is_order_date': fields.boolean(
            'Force Invoice Date',
            help="When checked, the invoice date will be "
                 "the same than the order's date"),
        'warning': fields.text('Warning Message', translate=True,
                               help='if set, display the message when a '
                               'user selects the process on a sale order'),
    }

    _defaults = {
        'picking_policy': 'direct',
        'order_policy': 'manual',
        'create_invoice_on': 'manual',
        'invoice_quantity': 'order',
        'validate_invoice': False,
    }
