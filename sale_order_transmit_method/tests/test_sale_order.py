# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import Command
from odoo.tests.common import TransactionCase


class TestSaleOrder(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.sale = cls.env.ref("sale.sale_order_2")
        cls.sale.order_line.mapped("product_id").write({"invoice_policy": "order"})
        cls.customer = cls.sale.partner_id
        cls.transmit_method_mail = cls.env.ref("account_invoice_transmit_method.mail")
        cls.transmit_method_post = cls.env.ref("account_invoice_transmit_method.post")
        cls.customer.customer_invoice_transmit_method_id = cls.transmit_method_mail

    def test_0(self):
        self.sale.partner_id = False
        self.assertFalse(self.sale.transmit_method_id)
        self.sale.partner_id = self.customer
        self.assertEqual(self.sale.transmit_method_id, self.transmit_method_mail)

    def test_transmit_method_when_invoicing_1(self):
        self.test_0()
        self.sale.transmit_method_id = self.transmit_method_post
        self.sale.action_confirm()
        self.sale._create_invoices()
        invoices = self.sale.order_line.invoice_lines.move_id
        self.assertEqual(invoices.transmit_method_id, self.transmit_method_post)

    def test_transmit_method_when_invoicing_2(self):
        self.test_0()
        self.sale.transmit_method_id = self.transmit_method_post
        self.sale.action_confirm()
        payment_wizard = self.env["sale.advance.payment.inv"].create(
            {
                "advance_payment_method": "fixed",
                "fixed_amount": 10,
                "sale_order_ids": [Command.set(self.sale.ids)],
            }
        )
        payment_wizard.create_invoices()
        invoices = self.sale.order_line.invoice_lines.move_id
        self.assertEqual(invoices.transmit_method_id, self.transmit_method_post)
