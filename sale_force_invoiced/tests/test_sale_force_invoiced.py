# Copyright 2017 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestSaleForceInvoiced(TransactionCase):
    def setUp(self):
        super(TestSaleForceInvoiced, self).setUp()
        self.sale_order_model = self.env["sale.order"]
        self.sale_order_line_model = self.env["sale.order.line"]

        # Data
        product_ctg = self._create_product_category()
        self.service_1 = self._create_product("test_product1", product_ctg)
        self.service_2 = self._create_product("test_product2", product_ctg)
        self.customer = self._create_customer("Test Customer")

    def _create_customer(self, name):
        """Create a Partner."""
        return self.env["res.partner"].create(
            {"name": name, "email": "example@yourcompany.com", "phone": 123456}
        )

    def _create_product_category(self):
        product_ctg = self.env["product.category"].create({"name": "test_product_ctg"})
        return product_ctg

    def _create_product(self, name, product_ctg):
        product = self.env["product.product"].create(
            {
                "name": name,
                "categ_id": product_ctg.id,
                "type": "service",
                "invoice_policy": "order",
            }
        )
        return product

    def test_sales_order(self):
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

        so._create_invoices()
        self.assertEqual(
            so.invoice_status, "invoiced", "The invoice status should be Invoiced"
        )

        # Reduce the invoiced qty
        for line in sol2.invoice_lines.with_context(check_move_validity=False):
            line.quantity = 1

        self.assertEqual(
            so.invoice_status, "to invoice", "The invoice status should be To Invoice"
        )

        so.action_done()
        so.force_invoiced = True
        self.assertEqual(
            so.invoice_status, "invoiced", "The invoice status should be Invoiced"
        )

        so.force_invoiced = False
        self.assertEqual(
            so.invoice_status, "to invoice", "The invoice status should be To Invoice"
        )
