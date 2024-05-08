# © 2017 Acsone SA/NV (http://www.acsone.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import odoo.tests.common as common


class TestSaleOrderInvoicePolicy(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product_obj = cls.env["product.product"]
        cls.sale_obj = cls.env["sale.order"]
        cls.partner = cls.env.ref("base.res_partner_2")
        cls.product = cls.product_obj.create(
            {"name": "Test", "detailed_type": "consu", "list_price": 20.0}
        )
        cls.product2 = cls.product_obj.create(
            {"name": "Test 2", "detailed_type": "consu", "list_price": 45.0}
        )
        cls.product3 = cls.product_obj.create(
            {
                "name": "Test 3 (service)",
                "detailed_type": "service",
                "list_price": 850.5,
            }
        )

    def test_sale_order_invoice_order(self):
        """Test invoicing based on ordered quantities"""
        settings = self.env["res.config.settings"].create({})
        settings.sale_invoice_policy_required = True
        settings.execute()
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
        self.assertTrue(so.invoice_policy_required)
        self.assertTrue(so.invoice_policy == "order")

        so.action_confirm()

        self.assertEqual(len(so.picking_ids), 1)

        picking = so.picking_ids
        picking.action_assign()
        self.assertEqual(picking.state, "assigned")
        so_line = so.order_line[0]
        self.assertEqual(so_line.qty_to_invoice, 2)
        self.assertEqual(so_line.invoice_status, "to invoice")
        self.assertEqual(so_line.product_id.invoice_policy, "order")

        so_line = so.order_line[1]
        self.assertEqual(so_line.qty_to_invoice, 3)
        self.assertEqual(so_line.invoice_status, "to invoice")
        self.assertEqual(so_line.product_id.invoice_policy, "order")

    def test_sale_order_invoice_deliver(self):
        """Test invoicing based on delivered quantities"""
        settings = self.env["res.config.settings"].create({})
        settings.sale_invoice_policy_required = True
        settings.execute()
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
        self.assertTrue(so.invoice_policy_required)
        self.assertTrue(so.invoice_policy == "delivery")

        so.action_confirm()

        self.assertEqual(len(so.picking_ids), 1)

        picking = so.picking_ids
        picking.action_assign()
        self.assertEqual(picking.state, "assigned")

        so_line = so.order_line[0]
        self.assertEqual(so_line.qty_to_invoice, 0)
        self.assertEqual(so_line.invoice_status, "no")

        so_line = so.order_line[1]
        self.assertEqual(so_line.qty_to_invoice, 0)
        self.assertEqual(so_line.invoice_status, "no")

        picking.button_validate()
        self.assertEqual(picking.state, "done")

        so_line = so.order_line[0]
        self.assertEqual(so_line.qty_to_invoice, 2)
        self.assertEqual(so_line.invoice_status, "to invoice")

        so_line = so.order_line[1]
        self.assertEqual(so_line.qty_to_invoice, 3)
        self.assertEqual(so_line.invoice_status, "to invoice")

    def test_settings(self):
        # delivery policy is the default
        settings = self.env["res.config.settings"].create({})
        settings.default_invoice_policy = "delivery"
        settings.sale_invoice_policy_required = True
        settings.execute()
        so = self.env["sale.order"].create(
            {"partner_id": self.env.ref("base.res_partner_2").id}
        )
        self.assertEqual(so.invoice_policy, "delivery")
        self.assertTrue(so.invoice_policy_required)
        # order policy is the default
        settings.default_invoice_policy = "order"
        settings.execute()
        so = self.env["sale.order"].create(
            {"partner_id": self.env.ref("base.res_partner_2").id}
        )
        self.assertEqual(so.invoice_policy, "order")
        self.assertTrue(so.invoice_policy_required)
