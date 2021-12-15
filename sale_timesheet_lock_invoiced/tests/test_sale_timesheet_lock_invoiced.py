# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.sale_timesheet.tests.common import CommonTest
from odoo.exceptions import ValidationError


class TestSaleTimesheetLockInvoiced(CommonTest):

    @classmethod
    def setUpClass(cls):
        super(TestSaleTimesheetLockInvoiced, cls).setUpClass()
        cls.AnalyticLine = cls.env['account.analytic.line']
        cls.SaleAdvancePaymentWiz = cls.env['sale.advance.payment.inv']
        cls.SaleOrder = cls.env['sale.order']

    def test_update_invoice_timesheet_line(self):
        partner = self.partner_eur
        product = self.product_delivery_timesheet3
        so = self.SaleOrder.create({
            'partner_id': partner.id,
            'partner_invoice_id': partner.id,
            'partner_shipping_id': partner.id,
            'order_line': [
                (0, 0, {
                    'name': "Flat Fee",
                    'product_id': product.id,
                    'product_uom_qty': product.uom_id.id,
                    'price_unit': product.list_price,
                }),
            ]
        })

        so.action_confirm()
        so_line = so.order_line[0]
        task = so_line.task_id

        analytic_line = self.AnalyticLine.create({
            'name': "Test",
            'project_id': task.project_id.id,
            'task_id': task.id,
            'unit_amount': 2,
        })
        self.assertEqual(analytic_line.so_line, so_line)

        # Create the invoice
        self.SaleAdvancePaymentWiz.with_context(active_ids=so.ids).create({
            'advance_payment_method': 'all',
        }).create_invoices()
        invoice = so.invoice_ids

        analytic_line.write({'name': "test update"})
        invoice.action_invoice_open()

        self.assertEqual(analytic_line.timesheet_invoice_id, invoice)

        with self.assertRaises(ValidationError), self.env.cr.savepoint():
            analytic_line.write({'name': "test"})

        with self.assertRaises(ValidationError), self.env.cr.savepoint():
            analytic_line.unlink()
