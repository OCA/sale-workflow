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
            {"name": "Test", "type": "consu", "list_price": 20.0}
        )
        cls.product2 = cls.product_obj.create(
            {"name": "Test 2", "type": "consu", "list_price": 45.0}
        )
        cls.product3 = cls.product_obj.create(
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
        self.assertEqual(so.invoice_policy, "order")

        # SO is not confirmed yet
        self.assertEqual([0.0, 0.0], so.order_line.mapped("untaxed_amount_to_invoice"))

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
        self.assertEqual("order", self.product.invoice_policy)
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
        self.assertEqual(so.invoice_policy, "delivery")

        # SO is not confirmed yet
        self.assertEqual([0.0, 0.0], so.order_line.mapped("untaxed_amount_to_invoice"))

        so.action_confirm()

        # SO is not delivered
        self.assertEqual([0.0, 0.0], so.order_line.mapped("untaxed_amount_to_invoice"))

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

        for mv in picking.move_line_ids:
            mv.quantity = mv.quantity_product_uom
        picking.button_validate()
        self.assertEqual(picking.state, "done")

        so_line = so.order_line[0]
        self.assertEqual(so_line.qty_to_invoice, 2)
        self.assertEqual(so_line.invoice_status, "to invoice")

        self.assertEqual(40.0, so_line.untaxed_amount_to_invoice)
        # Check that product has still its original invoice policy
        self.assertEqual("order", self.product.invoice_policy)

        so_line = so.order_line[1]
        self.assertEqual(so_line.qty_to_invoice, 3)
        self.assertEqual(so_line.invoice_status, "to invoice")

        self.assertEqual(135.0, so_line.untaxed_amount_to_invoice)

    def test_settings(self):
        # delivery policy is the default
        settings = self.env["res.config.settings"].create({})
        settings.sale_default_invoice_policy = "delivery"
        settings.execute()
        so = self.env["sale.order"].create(
            {"partner_id": self.env.ref("base.res_partner_2").id}
        )
        self.assertEqual(so.invoice_policy, "delivery")
        # order policy is the default
        settings.sale_default_invoice_policy = "order"
        settings.execute()
        so = self.env["sale.order"].create(
            {"partner_id": self.env.ref("base.res_partner_2").id}
        )
        self.assertEqual(so.invoice_policy, "order")

    def test_context_manager_exception(self):
        """Check the exception is well managed when called with several
        invoice policies"""
        self.assertEqual("order", self.product.invoice_policy)
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

        so2 = self.env["sale.order"].create(
            {
                "partner_id": self.env.ref("base.res_partner_2").id,
                "invoice_policy": "order",
                "order_line": [
                    (0, 0, {"product_id": self.product.id, "product_uom_qty": 2.0}),
                    (0, 0, {"product_id": self.product2.id, "product_uom_qty": 3.0}),
                ],
            }
        )
        lines = (so | so2).order_line
        with self.assertRaises(Exception) as exc:
            with self.env["sale.order.line"]._sale_invoice_policy(
                lines
            ):  # pragma: no cover
                pass
        self.assertEqual(
            "The method _sale_invoice_policy() must be called with lines sharing "
            "the same invoice policy",
            exc.exception.args[0],
        )
