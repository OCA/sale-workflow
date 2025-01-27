from psycopg2.errors import UniqueViolation

from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase, mute_logger


class TestSaleInvoiceBlocking(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.sale_order_model = cls.env["sale.order"]
        cls.sale_order_line_model = cls.env["sale.order.line"]

        # Data
        product_ctg = cls._create_product_category()
        cls.service_1 = cls._create_product("test_product1", product_ctg)
        cls.service_2 = cls._create_product("test_product2", product_ctg)
        cls.customer = cls._create_customer("Test Customer")

    @classmethod
    def _create_customer(cls, name):
        """Create a Partner."""
        return cls.env["res.partner"].create(
            {"name": name, "email": "example@yourcompany.com", "phone": 123456}
        )

    @classmethod
    def _create_product_category(cls):
        product_ctg = cls.env["product.category"].create({"name": "test_product_ctg"})
        return product_ctg

    @classmethod
    def _create_product(cls, name, product_ctg):
        product = cls.env["product.product"].create(
            {
                "name": name,
                "categ_id": product_ctg.id,
                "type": "service",
                "invoice_policy": "order",
            }
        )
        return product

    @mute_logger("odoo.sql_db")
    def test_duplicate_reason(self):
        self.env["invoice.blocking.reason"].create({"name": "Test Reason"})
        with self.assertRaises(UniqueViolation):
            self.env["invoice.blocking.reason"].create({"name": "Test Reason"})

    def test_sales_order_invoicing(self):
        so = self.sale_order_model.create({"partner_id": self.customer.id})
        sol1 = self.sale_order_line_model.create(
            {"product_id": self.service_1.id, "product_uom_qty": 1, "order_id": so.id}
        )
        sol2 = self.sale_order_line_model.create(
            {"product_id": self.service_2.id, "product_uom_qty": 2, "order_id": so.id}
        )

        # confirm quotation
        so.action_confirm()
        # update quantities delivered
        sol1.qty_delivered = 1
        sol2.qty_delivered = 2

        self.assertEqual(
            so.invoice_status, "to invoice", "The invoice status should be To Invoice"
        )

        so.invoice_blocking_reason_id = self.env["invoice.blocking.reason"].create(
            {"name": "Test Reason"}
        )

        self.assertEqual(
            so.invoice_status, "no", "The invoice status should be Nothing to Invoice"
        )

        with self.assertRaisesRegex(
            UserError, "Cannot create an invoice. No items are available to invoice"
        ):
            so._create_invoices()

        so.invoice_blocking_reason_id = False
        self.assertEqual(
            so.invoice_status, "to invoice", "The invoice status should be To Invoice"
        )
        so._create_invoices()
