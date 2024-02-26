from odoo.tests.common import SavepointCase


class TestSaleOrderDiscountFastChange(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.product1 = cls.env["product.product"].create(
            {
                "name": "Product 1",
                "list_price": 10.0,
                "taxes_id": False,
            }
        )
        cls.product2 = cls.env["product.product"].create(
            {
                "name": "Product 2",
                "list_price": 20.0,
                "taxes_id": False,
            }
        )

        cls.partner = cls.env["res.partner"].create(
            {
                "name": "John Doe",
            }
        )

        cls.order = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
            }
        )

        cls.env["sale.order.line"].create(
            {
                "product_id": cls.product1.id,
                "name": "Product 1",
                "product_uom_qty": 1.0,
                "product_uom": cls.env.ref("uom.product_uom_unit").id,
                "discount": 10.0,
                "order_id": cls.order.id,
            }
        )
        cls.env["sale.order.line"].create(
            {
                "product_id": cls.product2.id,
                "name": "Product 1",
                "product_uom_qty": 2.0,
                "product_uom": cls.env.ref("uom.product_uom_unit").id,
                "order_id": cls.order.id,
            }
        )

    def test_01_apply_global_discount_on_all_lines(self):
        self.assertEqual(self.order.amount_total, 49.0)
        wizard = self.env["sale.order.discount.fast.change"]
        wiz = wizard.create({})
        wiz = self.env["sale.order.discount.fast.change"].create(
            {
                "discount": 5.0,
                "application_policy": "all",
            }
        )
        wiz.with_context(active_id=self.order.id).apply_global_discount()
        self.assertEqual(self.order.amount_total, 47.5)

    def test_02_apply_global_discount_on_not_discounted_lines(self):
        self.assertEqual(self.order.amount_total, 49.0)
        wizard = self.env["sale.order.discount.fast.change"]
        wiz = wizard.create({})
        wiz = self.env["sale.order.discount.fast.change"].create(
            {
                "discount": 5.0,
                "application_policy": "not_discounted",
            }
        )
        wiz.with_context(active_id=self.order.id).apply_global_discount()
        self.assertEqual(self.order.amount_total, 47.0)
