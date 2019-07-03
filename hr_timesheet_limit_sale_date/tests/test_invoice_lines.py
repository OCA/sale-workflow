# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from datetime import datetime

from .common import TestCommonMixin


class TestInvoice(TestCommonMixin):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.selected_lines = cls.lines.filtered(
            lambda l: datetime.strptime(l.date, "%Y-%m-%d")
            <= datetime.strptime('2019-05-08', "%Y-%m-%d")
        )
        cls.unselected_lines = cls.lines - cls.selected_lines
        cls.context = {
            "active_model": 'sale.order',
            "active_ids": [cls.sale_order.id],
            "active_id": cls.sale_order.id,
            'open_invoices': True,
        }

    def get_invoice(self):
        wizard = self.env['sale.advance.payment.inv'].create(
            {'advance_payment_method': 'delivered'}
        )
        action_invoice = wizard.with_context(self.context).create_invoices()
        invoice_id = action_invoice['res_id']
        invoice = self.env['account.invoice'].browse(invoice_id)
        return invoice

    def test_invoice_partial_validation(self):
        self.sale_order.timesheet_limit_date = '2019-05-08'
        self.assertEqual(self.so_line.qty_delivered, 1)
        invoice = self.get_invoice()
        invoice.action_invoice_open()
        self.assertEqual(len(invoice.invoice_line_ids), 1)
        self.assertEqual(sum(invoice.invoice_line_ids.mapped('quantity')), 1)
        self.assertEquals(self.selected_lines.timesheet_invoice_id, invoice)
        self.assertFalse(self.unselected_lines.mapped('timesheet_invoice_id'))

    def test_invoice_delivered_limited(self):
        # despite of that all lines validated we constrain them
        # with limit_date
        self.assertEqual(self.so_line.qty_delivered, 3)
        self.sale_order.timesheet_limit_date = '2019-05-08'
        # will call apropriate recomputation
        self.assertEqual(self.so_line.qty_delivered, 1)
        invoice = self.get_invoice()
        invoice.action_invoice_open()
        self.assertEqual(len(invoice.invoice_line_ids), 1)
        self.assertEqual(sum(invoice.invoice_line_ids.mapped('quantity')), 1)
        self.assertEquals(self.selected_lines.timesheet_invoice_id, invoice)
        self.assertFalse(self.unselected_lines.mapped('timesheet_invoice_id'))

    def test_invoice_multiple_invoices(self):
        # test if multiple invoices get rigth dates
        self.sale_order.timesheet_limit_date = '2019-05-08'
        self.assertEqual(self.so_line.qty_delivered, 1)
        first_invoice = self.get_invoice()
        first_invoice.action_invoice_open()
        self.assertFalse(self.unselected_lines.mapped('timesheet_invoice_id'))
        # restricting date removed after invoice creation
        self.assertFalse(self.sale_order.timesheet_limit_date)
        self.sale_order.write({'timesheet_limit_date': '2019-05-10'})
        self.assertEqual(self.so_line.qty_delivered, 3)
        self.get_invoice()
        second_invoice = self.sale_order.mapped('invoice_ids')[0]
        second_invoice.action_invoice_open()

        self.assertEqual(first_invoice.timesheet_limit_date, '2019-05-08')
        self.assertEqual(second_invoice.timesheet_limit_date, '2019-05-10')
        self.assertEqual(len(first_invoice.invoice_line_ids), 1)
        self.assertEqual(
            sum(first_invoice.invoice_line_ids.mapped('quantity')), 1
        )
        self.assertEquals(
            self.selected_lines.timesheet_invoice_id, first_invoice
        )

        self.assertEqual(len(second_invoice.invoice_line_ids), 1)
        self.assertEqual(
            sum(second_invoice.invoice_line_ids.mapped('quantity')), 2
        )
        self.assertEquals(
            self.unselected_lines.mapped('timesheet_invoice_id'),
            second_invoice,
        )

    def test_invoice_force_invoice_date(self):
        # test if multiple invoices get rigth dates
        self.sale_order.timesheet_limit_date = '2019-05-08'
        invoice = self.get_invoice()
        self.assertFalse(self.sale_order.timesheet_limit_date)
        self.sale_order.write({'timesheet_limit_date': '2019-05-09'})
        domain = invoice._get_compute_timesheet_revenue_domain(
            self.so_line.ids
        )
        self.assertTrue(('date', '<=', '2019-05-08') in domain)
