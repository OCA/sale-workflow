# Copyright (C) 2024 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestSaleForceInvoicedQTY(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

        cls.sale_order_obj = cls.env["sale.order"]
        cls.sale_order_line_obj = cls.env["sale.order.line"]

        cls.customer = cls._create_customer("test_customer")
        cls.product_1 = cls._create_product("test_product_1")
        cls.product_2 = cls._create_product("test_product_2")
        cls.tax = cls.env["account.tax"].create(
            {
                "name": "Tax 15",
                "type_tax_use": "sale",
                "amount": 20,
                "price_include": True,
            }
        )

    @classmethod
    def _create_customer(cls, name):
        """Create a Partner."""
        return cls.env["res.partner"].create(
            {"name": name, "email": "example@yourcompany.com"}
        )

    @classmethod
    def _create_product(cls, name):
        return cls.env["product.product"].create(
            {
                "name": name,
                "type": "service",
                "invoice_policy": "delivery",
            }
        )

    def test_sales_order_1(self):
        so = self.sale_order_obj.create({"partner_id": self.customer.id})
        sol1 = self.sale_order_line_obj.create(
            {
                "product_id": self.product_1.id,
                "product_uom_qty": 3,
                "order_id": so.id,
                "price_unit": 100,
            }
        )
        sol2 = self.sale_order_line_obj.create(
            {
                "product_id": self.product_2.id,
                "product_uom_qty": 2,
                "order_id": so.id,
                "price_unit": 100,
            }
        )

        # confirm quotation
        so.action_confirm()
        # update quantities delivered
        sol1.qty_delivered = 3
        sol2.qty_delivered = 2

        sol2.force_invoiced_quantity = 3
        self.assertEqual(
            sol2.qty_to_invoice, -1, msg="The quantity to invoice should be -1"
        )
        self.assertEqual(
            so.invoice_status, "to invoice", "The invoice status should be To Invoice"
        )

        self.assertEqual(
            sol1.untaxed_amount_to_invoice,
            300,
            msg="The untaxed amount to invoice should be 300",
        )

        self.assertEqual(
            sol2.untaxed_amount_to_invoice,
            -100,
            msg="The untaxed amount to invoice should be -100",
        )

        so._create_invoices()
        self.assertEqual(
            so.invoice_status, "to invoice", "The invoice status should be To Invoice"
        )

    def test_sales_order_2(self):
        so = self.sale_order_obj.create({"partner_id": self.customer.id})
        sol1 = self.sale_order_line_obj.create(
            {
                "product_id": self.product_1.id,
                "product_uom_qty": 3,
                "order_id": so.id,
                "price_unit": 100,
                "tax_id": self.tax,
            }
        )
        sol2 = self.sale_order_line_obj.create(
            {
                "product_id": self.product_2.id,
                "product_uom_qty": 2,
                "order_id": so.id,
                "price_unit": 100,
                "tax_id": self.tax,
            }
        )

        # confirm quotation
        so.action_confirm()
        # update quantities delivered
        sol1.qty_delivered = 3
        sol2.qty_delivered = 2

        sol2.force_invoiced_quantity = 3
        self.assertEqual(
            sol2.qty_to_invoice, -1, msg="The quantity to invoice should be -1"
        )
        self.assertEqual(
            so.invoice_status, "to invoice", "The invoice status should be To Invoice"
        )

        self.assertEqual(
            sol1.untaxed_amount_to_invoice,
            250,
            msg="The untaxed amount to invoice should be 250",
        )

        self.assertEqual(
            sol2.untaxed_amount_to_invoice,
            -83.33,
            msg="The untaxed amount to invoice should be -83.33",
        )

        so._create_invoices()
        self.assertEqual(
            so.invoice_status, "to invoice", "The invoice status should be To Invoice"
        )

    def test_sales_order_3(self):
        so = self.sale_order_obj.create({"partner_id": self.customer.id})
        sol1 = self.sale_order_line_obj.create(
            {
                "product_id": self.product_1.id,
                "product_uom_qty": 3,
                "order_id": so.id,
                "price_unit": 100,
                "tax_id": self.tax,
                "discount": 15.0,
            }
        )
        sol2 = self.sale_order_line_obj.create(
            {
                "product_id": self.product_2.id,
                "product_uom_qty": 2,
                "order_id": so.id,
                "price_unit": 100,
                "tax_id": self.tax,
                "discount": 50.0,
            }
        )

        # confirm quotation
        so.action_confirm()
        # update quantities delivered
        sol1.qty_delivered = 3
        sol2.qty_delivered = 2

        sol2.force_invoiced_quantity = 3
        self.assertEqual(
            sol2.qty_to_invoice, -1, msg="The quantity to invoice should be -1"
        )
        self.assertEqual(
            so.invoice_status, "to invoice", "The invoice status should be To Invoice"
        )

        self.assertEqual(
            sol1.untaxed_amount_to_invoice,
            212.5,
            msg="The untaxed amount to invoice should be 212.5",
        )

        self.assertEqual(
            sol2.untaxed_amount_to_invoice,
            -41.67,
            msg="The untaxed amount to invoice should be -41.67",
        )

        so._create_invoices()
        inv_line = sol1._get_invoice_lines()
        inv_line.discount = 10.0
        so.order_line._compute_untaxed_amount_to_invoice()
        self.assertEqual(
            so.invoice_status, "to invoice", "The invoice status should be To Invoice"
        )
