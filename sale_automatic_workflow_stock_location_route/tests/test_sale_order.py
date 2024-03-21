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
        self.sale_orders.automatic_set_route_on_sol()
        self.assertEqual(
            self.sale_orders.order_line.mapped("route_id.id"),
            [],
        )
        self.so_1.workflow_process_id = self.wkflow_1
        self.so_2.workflow_process_id = self.wkflow_2
        self.sale_orders.automatic_set_route_on_sol()
        self.assertEqual(
            self.so_1.order_line.mapped("route_id.id"),
            [],
        )
        self.assertEqual(
            self.so_2.order_line.mapped("route_id.id"),
            [self.wkflow_2.sale_line_route_id.id],
        )
        # not on qty_delivered_method != 'stock_move'
        self.assertEqual(
            self.so_2.order_line[2].route_id.id,
            False,
        )
        # note : this will set a route_id on our service product,
        # we will use that later on to test the function
        self.so_1.order_line.route_id = self.route_1
        self.so_2.order_line.route_id = self.route_1
        self.sale_orders.automatic_set_route_on_sol()
        self.assertEqual(
            self.so_1.order_line.mapped("route_id.id"),
            [self.route_1.id],
        )
        # the service product on so_2 should have been untouched
        self.assertEqual(
            self.so_2.order_line[2].route_id.id,
            self.route_1.id,
        )
        # fix that and check the whole thing
        self.so_2.order_line[2].route_id = False
        self.assertEqual(
            self.so_2.order_line.mapped("route_id.id"),
            [self.wkflow_2.sale_line_route_id.id],
        )

    def test_02_onchange_automatic(self):
        self.assertEqual(
            self.sale_orders.order_line.mapped("route_id.id"),
            [],
        )
        # note : this will set a route_id on our service product,
        # we will use that later on to test the function
        self.so_1.order_line.route_id = self.route_1
        self.assertEqual(
            self.so_1.order_line.mapped("route_id.id"),
            [self.route_1.id],
        )
        self.so_1.workflow_process_id = self.wkflow_1
        self.so_1._onchange_workflow_process_id()
        self.assertEqual(
            self.so_1.order_line.mapped("route_id.id"),
            [self.route_1.id],
        )
        self.so_1.workflow_process_id = False
        self.so_1._onchange_workflow_process_id()
        self.assertEqual(
            self.so_1.order_line.mapped("route_id.id"),
            [self.route_1.id],
        )
        self.so_1.workflow_process_id = self.wkflow_2
        self.so_1._onchange_workflow_process_id()
        # the service product should have been untouched
        self.assertEqual(
            self.so_1.order_line[2].route_id.id,
            self.route_1.id,
        )
        # fix that and check the whole thing
        self.so_1.order_line[2].route_id = False
        self.assertEqual(
            self.so_1.order_line.mapped("route_id.id"),
            [],
        )
