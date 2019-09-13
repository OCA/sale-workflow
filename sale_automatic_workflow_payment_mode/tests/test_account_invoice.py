# -*- coding: utf-8 -*-
# Copyright 2019 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from uuid import uuid4
from odoo.addons.sale_automatic_workflow.tests.test_automatic_workflow_base \
    import TestAutomaticWorkflowBase


class TestAutomaticWorkflowPaymentMode(TestAutomaticWorkflowBase):

    def setUp(self):
        super(TestAutomaticWorkflowPaymentMode, self).setUp()
        self.invoice_obj = self.env['account.invoice']
        self.partner_obj = self.env['res.partner']
        self.product_obj = self.env['product.product']
        self.product_uom_unit = self.env.ref('product.product_uom_unit')
        self.workflow = self.create_full_automatic()
        self._create_payment_mode()
        self._create_invoice()

    def _create_payment_mode(self):
        self.journal = self.env['account.journal'].create({
            'name': 'Test journal',
            'code': 'TEST',
            'type': 'general',
        })
        self.payment_mode = self.env['account.payment.mode'].create({
            'name': 'Payment Mode Inbound',
            'payment_method_id':
                self.env.ref('account.account_payment_method_manual_in').id,
            'bank_account_link': 'fixed',
            'fixed_journal_id': self.journal.id,
        })
        method_out = self.env.ref('account.account_payment_method_manual_out')
        method_out.bank_account_required = True
        self.mode_out = self.env['account.payment.mode'].create({
            'name': 'Payment Mode Outbound',
            'payment_method_id': method_out.id,
            'bank_account_link': 'fixed',
            'fixed_journal_id': self.journal.id,
        })

    def _create_invoice(self):
        partner_values = {
            'name': str(uuid4()),
        }
        partner = self.partner_obj.create(partner_values)
        product_values = {
            'name': 'Bread',
            'list_price': 5,
            'type': 'product'
        }
        product = self.product_obj.create(product_values)
        account = product.categ_id.property_account_income_categ_id
        values = {
            'partner_id': partner.id,
            'invoice_line_ids': [(0, 0, {
                'name': product.name,
                'product_id': product.id,
                'price_unit': product.list_price,
                'account_id': account.id,
            })],
        }
        self.invoice = self.invoice_obj.create(values)

    def test_onchange_workflow(self):
        """
        Check if the workflow is automatically set when the payment mode is
        filled.
        :return:
        """
        self.payment_mode.write({
            'workflow_process_id': self.workflow.id,
        })
        self.invoice.write({
            'payment_mode_id': self.payment_mode.id
        })
        self.assertFalse(self.invoice.workflow_process_id)
        self.assertTrue(self.payment_mode.workflow_process_id)
        self.invoice.onchange_payment_mode_set_workflow()
        self.assertEqual(
            self.invoice.workflow_process_id,
            self.invoice.payment_mode_id.workflow_process_id)
