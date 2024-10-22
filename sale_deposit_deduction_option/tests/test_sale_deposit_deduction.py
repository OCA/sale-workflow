# Copyright 2023 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo.tests.common import Form, TransactionCase


class TestSaleDepositDeductionOption(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env.ref("base.partner_demo")
        cls.product = cls.env.ref("product.product_product_4")
        cls.order = cls._create_sale_order(cls, cls.partner, cls.product)
        cls.wizard_object = cls.env["sale.advance.payment.inv"]
        cls.move_object = cls.env["account.move"]

    def _create_sale_order(self, partner, product):
        sale_form = Form(self.env["sale.order"])
        sale_form.partner_id = partner
        with sale_form.order_line.new() as line_form:
            line_form.product_id = product
        sale = sale_form.save()
        sale.action_confirm()
        return sale

    def test_01_sale_deposit_deduct(self):
        self.context = {
            "active_model": "sale.order",
            "active_ids": [self.order.id],
            "active_id": self.order.id,
        }
        # Create invoice deposit 20%
        payment = self.wizard_object.with_context(**self.context).create(
            {"advance_payment_method": "percentage", "amount": 20}
        )
        res = payment.with_context(open_invoices=1).create_invoices()
        invoice_id = res["res_id"]
        move = self.move_object.browse(invoice_id)
        self.assertEqual(move.state, "draft")
        move.action_post()
        self.assertEqual(move.state, "posted")
        # Create invoice deduction proportionally
        payment2 = self.wizard_object.with_context(**self.context).create(
            {"advance_payment_method": "delivered"}
        )
        with Form(payment2) as p:
            p.deposit_deduction_option = "proportional"
        p.save()
        self.assertTrue(payment2.deduct_down_payments)
        res = payment2.with_context(open_invoices=1).create_invoices()
        move_deduct = self.order.invoice_ids - move
        # Quantity depend on delivery order.
        # if not install 'stock' module,
        # 'proportional' option will use full deposit.
        self.assertEqual(move_deduct.amount_total, self.order.amount_total * 0.2)
