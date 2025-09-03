from odoo.tests.common import SavepointCase


class TestSaleOrder(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        SaleOrder = cls.env["sale.order"]
        SaleWorkflowProcess = cls.env["sale.workflow.process"]
        ProductProduct = cls.env["product.product"]
        StockLocationRoute = cls.env["stock.location.route"]

        partner = cls.env["res.partner"].create({"name": "John Doe"})
        uom_unit = cls.env.ref("uom.product_uom_unit")
        product_1 = ProductProduct.create(
            {
                "name": "product_a",
            }
        )
        product_2 = ProductProduct.create(
            {
                "name": "product_b",
            }
        )
        product_3 = ProductProduct.create(
            {
                "name": "product_b",
                "type": "service",
            }
        )
        cls.so_1 = SaleOrder.create(
            {
                "partner_id": partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": p.name,
                            "product_id": p.id,
                            "product_uom_qty": 2,
                            "product_uom": uom_unit.id,
                        },
                    )
                    for p in (
                        product_1,
                        product_2,
                        product_3,
                    )
                ],
                "workflow_process_id": False,
            }
        )
        cls.so_2 = SaleOrder.create(
            {
                "partner_id": partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": p.name,
                            "product_id": p.id,
                            "product_uom_qty": 2,
                            "product_uom": uom_unit.id,
                        },
                    )
                    for p in (
                        product_1,
                        product_2,
                        product_3,
                    )
                ],
                "workflow_process_id": False,
            }
        )
        cls.sale_orders = SaleOrder.browse([cls.so_1.id, cls.so_2.id])
        cls.wkflow_1 = SaleWorkflowProcess.create(
            {
                "name": "Test process without route",
                "sale_line_route_id": False,
            }
        )
        cls.route_1 = StockLocationRoute.create({"name": "My Route 1"})
        cls.route_2 = StockLocationRoute.create({"name": "My Route 2"})
        cls.wkflow_2 = SaleWorkflowProcess.create(
            {
                "name": "Test process with route",
                "sale_line_route_id": cls.route_2.id,
            }
        )

    def test_01_automatic_set_route_on_sol(self):
        self.assertEqual(
            self.sale_orders.order_line.mapped("route_id.id"),
            [],
        )
        self.assertEqual(
            self.so_2.order_line[2].product_id.type,
            "service",
        )
        # this should do nothing, and no crash
        self.sale_orders.automatic_set_route_on_sol()
        self.assertEqual(
            self.sale_orders.order_line.mapped("route_id.id"),
            [],
        )

        self.so_2.order_line[0].route_id = self.route_1
        self.so_2.order_line[1].route_id = False
        self.so_2.order_line[2].route_id = False

        self.so_1.workflow_process_id = self.wkflow_1
        self.wkflow_2.sale_line_route_policy = "fill_empty"
        self.so_2.workflow_process_id = self.wkflow_2
        self.sale_orders.automatic_set_route_on_sol()
        # workflow 1 has no route_id, so does nothing
        self.assertEqual(
            self.so_1.order_line.mapped("route_id.id"),
            [],
        )

        # workflow 2 with policy fill_empty should set only
        # lines with no route already, and not type service
        self.assertEqual(
            self.so_2.order_line[0].route_id,
            self.route_1,
        )
        self.assertEqual(
            self.so_2.order_line[1].route_id,
            self.route_2,
        )
        self.assertFalse(
            self.so_2.order_line[2].route_id,
        )

        self.wkflow_2.sale_line_route_policy = "replace"
        self.sale_orders.automatic_set_route_on_sol()
        # workflow 2 with policy replace sholud set everything
        # except on product service
        self.assertEqual(
            self.so_2.order_line[0].route_id,
            self.route_2,
        )
        self.assertEqual(
            self.so_2.order_line[1].route_id,
            self.route_2,
        )
        self.assertFalse(
            self.so_2.order_line[2].route_id,
        )
