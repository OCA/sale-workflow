# © 2017 Acsone SA/NV (http://www.acsone.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import odoo.tests.common as common


class TestSaleOrderInvoicePolicy(common.TransactionCase):
    def setUp(self):
        super(TestSaleOrderInvoicePolicy, self).setUp()
        self.product_obj = self.env["product.product"]
        self.sale_obj = self.env["sale.order"]
        self.partner = self.env.ref("base.res_partner_2")
        self.product = self.product_obj.create(
            {"name": "Test", "type": "consu", "list_price": 20.0}
        )
        self.product2 = self.product_obj.create(
            {"name": "Test 2", "type": "consu", "list_price": 45.0}
        )
        self.product3 = self.product_obj.create(
            {
                "name": "Test 3 (service)",
                "type": "service",
                "list_price": 850.5,
            }
        )

    def test_sale_order_invoice_order(self):
        """Test invoicing based on ordered quantities"""
        so = self.env["sale.order"].create(
            {
                "partner_id": self.env.ref("base.res_partner_2").id,
                "order_line": [
                    (0, 0, {"product_id": self.product.id, "product_uom_qty": 2.0}),
                    (0, 0, {"product_id": self.product2.id, "product_uom_qty": 3.0}),
                ],
                "invoice_policy": "order",
            }
        )

        so.action_confirm()

        self.assertEqual(len(so.picking_ids), 1)

        for picking in so.picking_ids:
            picking.action_assign()
            self.assertEqual(picking.state, "assigned")
        so_line = so.order_line[0]
        self.assertEqual(so_line.qty_to_invoice, 2)
        self.assertEqual(so_line.invoice_status, "to invoice")
        so_line = so.order_line[1]
        self.assertEqual(so_line.qty_to_invoice, 3)
        self.assertEqual(so_line.invoice_status, "to invoice")

    def test_sale_order_invoice_deliver(self):
        """Test invoicing based on delivered quantities"""
        so = self.env["sale.order"].create(
            {
                "partner_id": self.env.ref("base.res_partner_2").id,
                "invoice_policy": "delivery",
                "order_line": [
                    (0, 0, {"product_id": self.product.id, "product_uom_qty": 2.0}),
                    (0, 0, {"product_id": self.product2.id, "product_uom_qty": 3.0}),
                ],
            }
        )

        so.action_confirm()

        self.assertEqual(len(so.picking_ids), 1)

        for picking in so.picking_ids:
            picking.action_assign()
            self.assertEqual(picking.state, "assigned")

        so_line = so.order_line[0]
        self.assertEqual(so_line.qty_to_invoice, 0)
        self.assertEqual(so_line.invoice_status, "no")

        so_line = so.order_line[1]
        self.assertEqual(so_line.qty_to_invoice, 0)
        self.assertEqual(so_line.invoice_status, "no")

        for mv in picking.move_lines:
            mv.quantity_done = mv.product_uom_qty
        picking.button_validate()
        self.assertEqual(picking.state, "done")

        so_line = so.order_line[0]
        self.assertEqual(so_line.qty_to_invoice, 2)
        self.assertEqual(so_line.invoice_status, "to invoice")

        so_line = so.order_line[1]
        self.assertEqual(so_line.qty_to_invoice, 3)
        self.assertEqual(so_line.invoice_status, "to invoice")

    def test_sale_order_invoice_policy_service1(self):
        """
        For this test, we check if the invoice policy is correctly updated
        (into the product) when the type is 'service'.
        The behaviour should be:
        - Get the value of the context but if the type is 'service': use the
        default_invoice_policy field value
        :return: bool
        """
        product = self.product3
        invoice_policy = "delivery"
        product.write(
            {
                "default_invoice_policy": invoice_policy,
            }
        )
        self.assertEqual(product.invoice_policy, invoice_policy)
        product = product.with_context(
            invoice_policy="order",
        )
        # Shouldn't be impacted by the context because the type is service
        self.assertEqual(product.invoice_policy, invoice_policy)
        return True

    def test_sale_order_invoice_policy_service2(self):
        """
        For this test, we check if the invoice policy is correctly updated
        (into the product) when the type is 'service'.
        The behaviour should be:
        - Get the value of the context but if the type is 'service': use the
        default_invoice_policy field value
        :return: bool
        """
        product = self.product3
        invoice_policy = "order"
        product.write(
            {
                "default_invoice_policy": invoice_policy,
            }
        )
        self.assertEqual(product.invoice_policy, invoice_policy)
        product = product.with_context(
            invoice_policy="delivery",
        )
        # Shouldn't be impacted by the context because the type is service
        self.assertEqual(product.invoice_policy, invoice_policy)
        return True

    def test_sale_order_invoice_policy_service3(self):
        """
        For this test, we check if the invoice policy is correctly updated
        (into the product) when the type is 'service'.
        The behaviour should be:
        - Get the value of the context but if the type is 'service': use the
        default_invoice_policy field value
        :return: bool
        """
        product = self.product3
        product2 = self.product2
        products = product
        products |= product2
        invoice_policy = "order"
        products.write(
            {
                "default_invoice_policy": invoice_policy,
            }
        )
        self.assertEqual(product.invoice_policy, invoice_policy)
        self.assertEqual(product2.invoice_policy, invoice_policy)
        new_invoice_policy = "delivery"
        product = product.with_context(
            invoice_policy=new_invoice_policy,
        )
        product2 = product2.with_context(
            invoice_policy=new_invoice_policy,
        )
        # Shouldn't be impacted by the context because the type is service
        self.assertEqual(product.invoice_policy, invoice_policy)

        # This one is not a service so it must be impacted by the context
        self.assertEqual(product2.invoice_policy, new_invoice_policy)
        product = product.with_context(
            invoice_policy=invoice_policy,
        )
        product2 = product2.with_context(
            invoice_policy=invoice_policy,
        )
        # Shouldn't be impacted by the context because the type is service
        self.assertEqual(product.invoice_policy, invoice_policy)
        # This one is not a service so it must be impacted by the context
        self.assertEqual(product2.invoice_policy, invoice_policy)
        return True

    def test_inverse_invoice_policy(self):
        self.product.default_invoice_policy = "order"
        self.assertEquals("order", self.product.default_invoice_policy)
        self.product.invoice_policy = "delivery"
        self.assertEquals("delivery", self.product.default_invoice_policy)

    def test_settings(self):
        settings = self.env["res.config.settings"].create({})
        settings.sale_default_invoice_policy = "delivery"
        settings.sale_invoice_policy_required = True
        settings.execute()
        so = self.env["sale.order"].create(
            {
                "partner_id": self.env.ref("base.res_partner_2").id,
            }
        )
        self.assertEqual(so.invoice_policy, "delivery")
        self.assertTrue(so.invoice_policy_required)
