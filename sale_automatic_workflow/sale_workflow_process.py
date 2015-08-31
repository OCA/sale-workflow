# -*- encoding: utf-8 -*-
###############################################################################
#
#    sale_automatic_workflow for OpenERP
#    Copyright (C) 2011 Akretion Sébastien BEAU <sebastien.beau@akretion.com>
#    Author: Guewen Baconnier
#    Copyright 2014 Camptocamp SA
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

from openerp import models, fields


class SaleWorkflowProcess(models.Model):
    """ A workflow process is the setup of the automation of a sales order.

    Each sales order can be linked to a workflow process.
    Then, the options of the workflow will change how the sales order
    behave, and how it is automatized.

    A workflow process may be linked with a Sales payment method, so
    each time a payment method is used, the workflow will be applied.
    """
    _name = "sale.workflow.process"
    _description = "Sale Workflow Process"

    name = fields.Char()
    picking_policy = fields.Selection(
        selection=[('direct', 'Deliver each product when available'),
                   ('one', 'Deliver all products at once')],
        string='Shipping Policy',
        default='direct',
    )
    order_policy = fields.Selection(
        selection=[('prepaid', 'Before Delivery'),
                   ('manual', 'On Demand'),
                   ('picking', 'On Delivery Order')],
        string='Invoice Policy',
        default='manual',
    )
    invoice_quantity = fields.Selection(
        selection=[('order', 'Ordered Quantities'),
                   ('procurement', 'Shipped Quantities')],
        string='Invoice on',
        default='order',
    )
    validate_order = fields.Boolean(string='Validate Order')
    create_invoice_on = fields.Selection(
        selection=[('manual', 'No automatic invoice'),
                   ('on_order_confirm', 'On confirmation of Sale Order'),
                   ('on_picking_done', 'After Delivery')],
        required=True,
        string='Create Invoice',
        default='manual',
    )
    validate_invoice = fields.Boolean(string='Validate Invoice')
    validate_picking = fields.Boolean(string='Confirm and Close Picking')
    invoice_date_is_order_date = fields.Boolean(
        string='Force Invoice Date',
        help="When checked, the invoice date will be "
             "the same than the order's date"
    )
    warning = fields.Text('Warning Message', translate=True,
                          help='If set, display the message when a '
                               'user selects the process on a sale order')
    section_id = fields.Many2one(comodel_name='crm.case.section',
                                 string='Sales Team')
