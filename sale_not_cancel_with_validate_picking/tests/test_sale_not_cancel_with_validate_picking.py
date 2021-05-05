# Copyright 2021 Daniel Domínguez - https://xtendoo.es
# Copyright 2021 Manuel Calero - https://xtendoo.es
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.exceptions import UserError
from odoo.tests import common


class TestSaleNotCancelWithValidatePicking(common.TransactionCase):
    def setUp(self):
        super(TestSaleNotCancelWithValidatePicking, self).setUp()
        self.partner_model = self.env["res.partner"]
        self.product_model = self.env["product.product"]
        self.warehouse_model = self.env["stock.warehouse"]
        self.move_model = self.env["stock.move"]
        self.location_model = self.env["stock.location"]

        self.partner = self.partner_model.create({"name": "Test partner"})
        self.warehouse = self.env.ref("stock.warehouse0")
        self.stock_location = self.env.ref("stock.stock_location_stock")
        self.product = self.product_model.create(
            {"name": "Test product", "type": "product"}
        )

        # Create a SO with a couple of lines:
        self.so = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "partner_invoice_id": self.partner.id,
                "partner_shipping_id": self.partner.id,
                "warehouse_id": self.warehouse.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": self.product.name,
                            "product_id": self.product.id,
                            "product_uom_qty": 2,
                            "product_uom": self.product.uom_id.id,
                            "price_unit": self.product.list_price,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": self.product.name,
                            "product_id": self.product.id,
                            "product_uom_qty": 5,
                            "product_uom": self.product.uom_id.id,
                            "price_unit": self.product.list_price,
                        },
                    ),
                ],
            }
        )

    def test_sale_order_without_validate_picking(self):
        sale_order = self.so
        sale_order.action_confirm()
        self.assertEqual(len(sale_order.picking_ids), 1)
        sale_order.action_cancel()
        self.assertEqual(sale_order.state, "cancel")

    def test_sale_order_with_validate_picking(self):
        self.qty_on_hand()
        sale_order = self.so
        sale_order.action_confirm()
        picking = sale_order.picking_ids[:1]
        picking.action_confirm()
        picking.action_assign()
        for line in picking.move_lines.mapped("move_line_ids"):
            line.qty_done = line.product_qty
        picking.action_done()
        with self.assertRaises(UserError):
            sale_order.action_cancel()

    def qty_on_hand(self):
        """Update Product quantity."""
        wiz = self.env["stock.inventory"].create(
            {
                "name": "Stock Inventory",
                "product_ids": [(4, self.product.id, 0)],
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "product_uom_id": self.product.uom_id.id,
                            "location_id": self.stock_location.id,
                            "product_qty": 10,
                        },
                    ),
                ],
            }
        )
        wiz.action_start()
        wiz.action_validate()
