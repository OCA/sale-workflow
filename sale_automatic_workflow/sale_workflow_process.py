# -*- encoding: utf-8 -*-
#################################################################################
#                                                                               #
#    sale_automatic_workflow for OpenERP                                        #
#    Copyright (C) 2011 Akretion Sébastien BEAU <sebastien.beau@akretion.com>   #
#                                                                               #
#    This program is free software: you can redistribute it and/or modify       #
#    it under the terms of the GNU Affero General Public License as             #
#    published by the Free Software Foundation, either version 3 of the         #
#    License, or (at your option) any later version.                            #
#                                                                               #
#    This program is distributed in the hope that it will be useful,            #
#    but WITHOUT ANY WARRANTY; without even the implied warranty of             #
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the              #
#    GNU Affero General Public License for more details.                        #
#                                                                               #
#    You should have received a copy of the GNU Affero General Public License   #
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.      #
#                                                                               #
#################################################################################

from openerp.osv import orm, fields


class sale_workflow_process(orm.Model):
    _name = "sale.workflow.process"
    _description = "sale workflow process"

    _columns = {
        'name': fields.char('Name', size=64),
        'picking_policy': fields.selection([('direct', 'Partial Delivery'),
                                            ('one', 'Complete Delivery')],
                                           string='Packing Policy'),
        'order_policy': fields.selection([
            ('prepaid', 'Before Delivery'),
            ('manual', 'On Demand'),
            # https://bugs.launchpad.net/openobject-addons/+bug/1160835
            # ('postpaid', 'Invoice on Order After Delivery'),
            ('picking', 'On Delivery Order'),
        ], 'Shipping Policy'),
        'invoice_quantity': fields.selection([('order', 'Ordered Quantities'),
                                              ('procurement', 'Shipped Quantities')],
                                             string='Invoice on'),
        'validate_order': fields.boolean('Validate Order'),
        'create_invoice': fields.boolean('Create Invoice'),
        'validate_invoice': fields.boolean('Validate Invoice'),
        'validate_picking': fields.boolean('Validate Picking'),
        # TODO not implemented actually
        # 'validate_manufactoring_order': fields.boolean('Validate Manufactoring Order'),
        'invoice_date_is_order_date': fields.boolean(
            'Force Invoice Date',
            help="When checked, the invoice date will be "
                 "the same than the order's date"),
    }

    _defaults = {
        'picking_policy': 'direct',
        'order_policy': 'manual',
        'invoice_quantity': 'order',
        'validate_invoice': False,
    }
