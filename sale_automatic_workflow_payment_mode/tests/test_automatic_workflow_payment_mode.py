# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo.addons.sale_automatic_workflow.tests.test_automatic_workflow_base \
    import TestAutomaticWorkflowBase


class TestAutomaticWorkflowPaymentMode(TestAutomaticWorkflowBase):

    def create_sale_order(self, workflow, override=None):
        new_order = super(TestAutomaticWorkflowPaymentMode, self).\
            create_sale_order(workflow, override)
        self.pay_method = self.env['account.payment.method'].create({
            'name': 'default inbound',
            'code': 'definb',
            'payment_type': 'inbound'})
        self.acc_journ = self.env['account.journal'].create({
            'name': 'Bank US',
            'type': 'bank',
            'code': 'BNK68'})
        self.pay_mode = self.env['account.payment.mode'].create({
            'name': "Julius Caesare payment",
            'bank_account_link': 'fixed',
            'fixed_journal_id': self.acc_journ.id,
            'payment_method_id': self.pay_method.id,
            'workflow_process_id': workflow.id})
        new_order.payment_mode_id = self.pay_mode
        new_order.payment_mode_id.workflow_process_id = \
            new_order.workflow_process_id.id
        return new_order

    def create_full_automatic(self, override=None):
        values = super(TestAutomaticWorkflowPaymentMode, self).\
            create_full_automatic(override)
        reg_pay_dict = {'register_payment': True}
        values.update(reg_pay_dict)
        return values

    def test_full_automatic(self):
        workflow = self.create_full_automatic()
        sale = self.create_sale_order(workflow)
        sale._onchange_workflow_process_id()
        sale.onchange_payment_mode_set_workflow()
        self.assertEqual(sale.state, 'draft')
        self.assertEqual(sale.workflow_process_id, workflow)
        self.progress()
        self.assertEqual(sale.state, 'sale')
        self.assertTrue(sale.picking_ids)
        self.assertTrue(sale.invoice_ids)
        invoice = sale.invoice_ids
        self.assertEqual(invoice.state, 'paid')
        picking = sale.picking_ids
        self.assertEqual(picking.state, 'done')
