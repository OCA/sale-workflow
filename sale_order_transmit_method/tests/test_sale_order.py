# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase


class TestSaleOrder(SavepointCase):
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

    def test_onchange_partner_transmit_method(self):
        self.assertFalse(self.sale.transmit_method_id)
        self.sale.onchange_partner_transmit_method()
        self.assertEqual(self.sale.transmit_method_id, self.transmit_method_mail)

    def test_transmit_method_when_invoicing_1(self):
        self.assertFalse(self.sale.transmit_method_id)
        self.sale.onchange_partner_transmit_method()
        self.assertEqual(self.sale.transmit_method_id, self.transmit_method_mail)
        self.sale.transmit_method_id = self.transmit_method_post
        self.sale.action_confirm()
        self.sale._create_invoices()
        invoices = self.sale.order_line.mapped("invoice_lines.move_id")
        self.assertEqual(invoices[0].transmit_method_id, self.transmit_method_post)

    def test_transmit_method_when_invoicing_2(self):
        self.assertFalse(self.sale.transmit_method_id)
        self.sale.onchange_partner_transmit_method()
        self.assertEqual(self.sale.transmit_method_id, self.transmit_method_mail)
        self.sale.transmit_method_id = self.transmit_method_post
        self.sale.action_confirm()
        payment_wizard = self.env["sale.advance.payment.inv"].create(
            {"advance_payment_method": "fixed", "amount": 10}
        )
        payment_wizard.with_context(active_ids=self.sale.ids).create_invoices()
        invoices = self.sale.order_line.mapped("invoice_lines.move_id")
        self.assertEqual(invoices[0].transmit_method_id, self.transmit_method_post)
