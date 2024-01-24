# Copyright (C) 2024 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import tagged
from odoo.tests.common import Form, TransactionCase


@tagged("post_install", "-at_install")
class TestSaleOrderInvoiceAmount(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        # Partners
        res_partner_obj = cls.env["res.partner"]
        product_obj = cls.env["product.product"]
        cls.res_partner_1 = res_partner_obj.create({"name": "Test Partner 1"})
        # Products
        cls.product_1 = product_obj.create(
            {"name": "Desk Combination 1", "type": "consu", "invoice_policy": "order"}
        )
        cls.product_2 = product_obj.create(
            {
                "name": "Desk Combination 2",
                "type": "consu",
                "invoice_policy": "delivery",
            }
        )
        # Sale Order
        cls.sale_order_1 = cls.env["sale.order"].create(
            {"partner_id": cls.res_partner_1.id}
        )

    def test_add_product(self):
        """Check add product to sale order"""
        with Form(self.sale_order_1) as form:
            with form.order_line.new() as line_1:
                line_1.product_id = self.product_1
                line_1.price_unit = 100.0
            with form.order_line.new() as line_2:
                line_2.product_id = self.product_2
                line_2.price_unit = 150.0

        sale_order = form.save()

        self.assertEqual(
            sale_order.untaxed_amount_to_invoice,
            0,
            msg="Amount to invoice must be equal 0",
        )
        sale_order.action_confirm()
        self.assertEqual(
            sale_order.untaxed_amount_to_invoice,
            100.0,
            msg="Amount to invoice must be equal 100.0",
        )

        sale_order.order_line[1].qty_delivered = 1
        self.assertEqual(
            sale_order.untaxed_amount_to_invoice,
            250.0,
            msg="Amount to invoice must be equal 250.0",
        )
