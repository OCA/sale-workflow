from odoo.tests.common import TransactionCase


class TestSaleOrderTaxBreakdown(TransactionCase):
    def setUp(self):
        super().setUp()
        self.partner = self.env["res.partner"].create({"name": "Cliente Test"})
        self.product = self.env["product.product"].create(
            {
                "name": "Producto Test",
                "list_price": 100.0,
            }
        )
        self.tax_21 = self.env["account.tax"].create(
            {
                "name": "IVA 21%",
                "amount": 21.0,
                "amount_type": "percent",
                "type_tax_use": "sale",
            }
        )
        self.tax_10 = self.env["account.tax"].create(
            {
                "name": "IVA 10%",
                "amount": 10.0,
                "amount_type": "percent",
                "type_tax_use": "sale",
            }
        )
        self.order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
            }
        )
        self.env["sale.order.line"].create(
            {
                "order_id": self.order.id,
                "product_id": self.product.id,
                "product_uom_qty": 1,
                "price_unit": 100.0,
                "tax_id": [(6, 0, [self.tax_21.id])],
            }
        )
        self.env["sale.order.line"].create(
            {
                "order_id": self.order.id,
                "product_id": self.product.id,
                "product_uom_qty": 1,
                "price_unit": 100.0,
                "tax_id": [(6, 0, [self.tax_10.id])],
            }
        )

    def test_amount_by_group_splits_by_tax_name(self):
        self.order._amount_by_group()
        groups = {g[0]: g for g in self.order.amount_by_group}
        self.assertIn("IVA 21%", groups)
        self.assertIn("IVA 10%", groups)
        self.assertAlmostEqual(groups["IVA 21%"][2], 100.0, places=2)
        self.assertAlmostEqual(groups["IVA 10%"][2], 100.0, places=2)
        self.assertAlmostEqual(groups["IVA 21%"][1], 21.0, places=2)
        self.assertAlmostEqual(groups["IVA 10%"][1], 10.0, places=2)
