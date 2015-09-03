# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Alexandre Fayolle, Guewen Baconnier
#    Copyright 2015 Camptocamp SA
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
"""
run the tests from sale_automatic_workflow with autopay enabled
"""

from openerp.addons.sale_automatic_workflow.tests.test_flow \
    import TestAutomaticWorkflow


class TestAutomaticWorkflowPayment(TestAutomaticWorkflow):
    def _create_sale_order(self, workflow, override=None):
        payment_method_obj = self.env['payment.method']
        method = payment_method_obj.search(
            [('workflow_process_id', '=', workflow.id)]
            )
        if override is None:
            override = {}
        override['payment_method_id'] = method[0].id
        return super(TestAutomaticWorkflowPayment,
                     self)._create_sale_order(workflow, override)

    def _create_payment_method(self, workflow):
        payment_method_obj = self.env['payment.method']
        journal = self.env.ref('account.sales_journal')
        term = self.env.ref('account.account_payment_term_immediate')
        values = {'name': 'test',
                  'journal_id': journal.id,
                  'payment_term_id': term.id,
                  'workflow_process_id': workflow.id,
                  }
        return payment_method_obj.create(values)

    def _create_full_automatic(self, override=None):
        if override is None:
            override = {}
        override['autopay'] = True
        values = super(TestAutomaticWorkflowPayment,
                       self)._create_full_automatic(override)
        self._create_payment_method(values)
        return values

    def test_full_automatic(self):
        workflow = self._create_full_automatic()
        sale = self._create_sale_order(workflow)
        sale.onchange_workflow_process_id()
        self.assertEqual(sale.state, 'draft')
        self.assertEqual(sale.workflow_process_id, workflow)
        self.progress()
        # changed: is "progress" without autopay
        self.assertEqual(sale.state, 'done')
        self.assertTrue(sale.picking_ids)
        self.assertTrue(sale.invoice_ids)
        invoice = sale.invoice_ids
        # changed: is "open" without autopay
        self.assertEqual(invoice.state, 'paid')
        picking = sale.picking_ids
        self.progress()
        self.assertEqual(picking.state, 'done')
