# -*- coding: utf-8 -*-
##############################################################################
#
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
##############################################################################

from datetime import datetime, timedelta

from openerp import fields
from openerp.tests import common


class TestAutomaticWorkflow(common.TransactionCase):

    def _create_sale_order(self, workflow, override=None):
        sale_obj = self.env['sale.order']
        partner_values = {'name': 'Imperator Caius Julius Caesar Divus'}
        partner = self.env['res.partner'].create(partner_values)
        product_values = {'name': 'Bread',
                          'list_price': 5,
                          'type': 'product'}
        product = self.env['product.product'].create(product_values)
        values = {
            'partner_id': partner.id,
            'order_line': [(0, 0, {'product_id': product.id,
                                   'product_uom_qty': 1})],
            'workflow_process_id': workflow.id,
        }
        if override:
            values.update(override)
        return sale_obj.create(values)

    def _create_full_automatic(self, override=None):
        workflow_obj = self.env['sale.workflow.process']
        values = workflow_obj.create({
            'name': 'Full Automatic',
            'picking_policy': 'one',
            #             'order_policy': 'manual',
            #             'invoice_quantity': 'order',
            'validate_order': True,
            'validate_picking': True,
            'validate_invoice': True,
            #             'create_invoice_on': 'on_order_confirm',
            'invoice_date_is_order_date': True,
        })
        if override:
            values.update(override)
        return values

    def progress(self):
        self.env['automatic.workflow.job'].run()

    def test_full_automatic(self):
        workflow = self._create_full_automatic()
        sale = self._create_sale_order(workflow)
        sale.onchange_workflow_process_id()
        self.assertEqual(sale.state, 'draft')
        self.assertEqual(sale.workflow_process_id, workflow)
        self.progress()
        self.assertEqual(sale.state, 'progress')
        self.assertTrue(sale.picking_ids)
        self.assertTrue(sale.invoice_ids)
        invoice = sale.invoice_ids
        self.assertEqual(invoice.state, 'open')
        picking = sale.picking_ids
        self.progress()
        self.assertEqual(picking.state, 'done')

    def test_onchange(self):
        workflow = self._create_full_automatic()
        sale = self._create_sale_order(workflow)
        sale.onchange_workflow_process_id()
        self.assertEqual(sale.picking_policy, 'one')
#         self.assertEqual(sale.order_policy, 'manual')
#         self.assertEqual(sale.invoice_quantity, 'order')
        workflow2 = self._create_full_automatic(
            override={
                'picking_policy': 'direct',
                #                 'order_policy': 'prepaid',
                #                 'invoice_quantity': 'procurement',
            }
        )
        sale.workflow_process_id = workflow2.id
        sale.onchange_workflow_process_id()
        self.assertEqual(sale.picking_policy, 'direct')
#         self.assertEqual(sale.order_policy, 'prepaid')
#         self.assertEqual(sale.invoice_quantity, 'procurement')

    def test_date_invoice_from_sale_order(self):
        workflow = self._create_full_automatic(
            override={
                #                       'order_policy': 'prepaid',
                #                       'invoice_quantity': 'order',
            },
        )
        # date_order on sale.order is date + time
        # date_invoice on account.invoice is date only
        last_week_time = datetime.now() - timedelta(days=7)
        last_week_time = fields.Datetime.to_string(last_week_time)
        last_week_date = last_week_time[:10]
        override = {
            'date_order': last_week_time,
        }
        sale = self._create_sale_order(workflow, override=override)
        sale.onchange_workflow_process_id()
        self.assertEqual(sale.date_order, last_week_time)
        self.progress()
        self.assertTrue(sale.invoice_ids)
        invoice = sale.invoice_ids
        self.assertEqual(invoice.date_invoice, last_week_date)
        self.assertEqual(invoice.workflow_process_id, sale.workflow_process_id)

    def test_date_invoice_from_picking(self):
        workflow = self._create_full_automatic(
            override={
                #                       'order_policy': 'picking',
                #                       'invoice_quantity': 'procurement',
            },
        )
        # date_order on sale.order is date + time
        # date_invoice on account.invoice is date only
        last_week_time = datetime.now() - timedelta(days=7)
        last_week_time = fields.Datetime.to_string(last_week_time)
        last_week_date = last_week_time[:10]
        override = {
            'date_order': last_week_time,
        }
        sale = self._create_sale_order(workflow, override=override)
        sale.onchange_workflow_process_id()
        self.assertEqual(sale.date_order, last_week_time)
        self.progress()
        self.assertTrue(sale.picking_ids)
        picking = sale.picking_ids
        self.assertEqual(picking.workflow_process_id, sale.workflow_process_id)
        # invoice is not created automatically from pickings, create
        # them
        wizard_obj = self.env['stock.invoice.onshipping']
        wizard_obj = wizard_obj.with_context(active_ids=picking.ids)
        wizard_obj.create({}).create_invoice()
        self.assertTrue(sale.invoice_ids)
        invoice = sale.invoice_ids
        self.assertEqual(invoice.date_invoice, last_week_date)
        self.assertEqual(invoice.workflow_process_id, sale.workflow_process_id)

    def test_invoice_from_picking_with_service_product(self):
        workflow = self._create_full_automatic(
            override={
                #                       'order_policy': 'picking',
                #                       'create_invoice_on': 'on_picking_done',
            },
        )

        product_service = self.env.ref('product.product_product_consultant')
        override = {
            'order_line': [(0, 0, {'product_id': product_service.id,
                                   'product_uom_qty': 1})],
        }
        sale = self._create_sale_order(workflow, override=override)
        sale.onchange_workflow_process_id()
        self.progress()
#         self.assertEqual(sale.order_policy, 'manual')
        self.assertFalse(sale.picking_ids)
        self.assertTrue(sale.invoice_ids)
        invoice = sale.invoice_ids
        self.assertEqual(invoice.workflow_process_id, sale.workflow_process_id)

    def test_journal_on_invoice(self):
        new_sale_journal = self.env['account.journal'].create({"name": "TTSA",
                                                               "code": "TTSA",
                                                               "type": "sale"})
        sale_journal = self.env.ref("account.sales_journal")

        workflow = self._create_full_automatic()
        sale = self._create_sale_order(workflow)
        sale.onchange_workflow_process_id()
        self.progress()
        self.assertTrue(sale.invoice_ids)
        invoice = sale.invoice_ids
        self.assertEqual(invoice.journal_id.id, sale_journal.id)

        workflow = self._create_full_automatic(
            override={'property_journal_id': new_sale_journal.id,
                      },
        )
        sale = self._create_sale_order(workflow)
        sale.onchange_workflow_process_id()
        self.progress()
        self.assertTrue(sale.invoice_ids)
        invoice = sale.invoice_ids
        self.assertEqual(invoice.journal_id.id, new_sale_journal.id)
