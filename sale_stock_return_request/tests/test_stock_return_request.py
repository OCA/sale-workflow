# Copyright 2019 Tecnativa - David Vidal
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.addons.stock_return_request.tests.test_stock_return_request_common import (
    StockReturnRequestCase,
)


class SaleReturnRequestCase(StockReturnRequestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner_customer_2 = cls.env["res.partner"].create(
            {
                "name": "Mr. Sale",
                "property_stock_supplier": cls.supplier_loc.id,
                "property_stock_customer": cls.customer_loc.id,
            }
        )
        cls.wh1.delivery_route_id.rule_ids.location_id = cls.customer_loc.id
        cls.so_1 = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner_customer_2.id,
                "warehouse_id": cls.wh1.id,
                "picking_policy": "direct",
                "order_line": [
                    (
                        0,
                        False,
                        {
                            "product_id": cls.prod_3.id,
                            "name": cls.prod_3.name,
                            "product_uom_qty": 14.0,
                            "price_unit": 10.0,
                            "product_uom": cls.prod_3.uom_id.id,
                        },
                    ),
                ],
            }
        )
        cls.so_2 = cls.so_1.copy()
        cls.sale_orders = cls.so_1 | cls.so_2
        # Confirm all the sale orders
        for order in cls.sale_orders:
            order.action_confirm()
        # Adjust quants to avoid reservation quircks
        quant_lot_1 = cls.env["stock.quant"].search(
            [
                ("product_id", "=", cls.prod_3.id),
                ("lot_id", "=", cls.prod_3_lot1.id),
                ("location_id", "=", cls.wh1.lot_stock_id.id),
            ]
        )
        quant_lot_2 = cls.env["stock.quant"].search(
            [
                ("product_id", "=", cls.prod_3.id),
                ("lot_id", "=", cls.prod_3_lot2.id),
                ("location_id", "=", cls.wh1.lot_stock_id.id),
            ]
        )
        quant_lot_1.reserved_quantity = 90.0
        quant_lot_2.reserved_quantity = 10.0
        # Deliver products. For each picking:
        # 10 units of TSTPROD3LOT0001 -> -20 units of 90 already existing
        # 2 units of TSTPROD3LOT0002 -> -4 units of 10 already existing
        for picking in cls.sale_orders.mapped("picking_ids"):
            for ml in picking.move_line_ids:
                ml.write(
                    {
                        "lot_id": cls.prod_3_lot1.id,
                        "product_uom_qty": 0.0,
                        "qty_done": 10.0,
                    }
                )
                ml.create(
                    {
                        "move_id": ml.move_id.id,
                        "picking_id": ml.picking_id.id,
                        "location_id": ml.location_id.id,
                        "location_dest_id": ml.location_dest_id.id,
                        "product_uom_id": ml.product_uom_id.id,
                        "product_id": cls.prod_3.id,
                        "product_uom_qty": 0.0,
                        "lot_id": cls.prod_3_lot2.id,
                        "qty_done": 4.0,
                    }
                )
            picking.action_done()
        quant_lot_1.reserved_quantity = quant_lot_2.reserved_quantity = 0.0

    def test_01_return_sale_stock_from_customer(self):
        """Return stock from customer and the corresponding
           sales will be ready for refund"""
        self.return_request_customer.write(
            {
                "partner_id": self.partner_customer_2.id,
                "to_refund": True,
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.prod_3.id,
                            "lot_id": self.prod_3_lot1.id,
                            "quantity": 12.0,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "product_id": self.prod_3.id,
                            "lot_id": self.prod_3_lot2.id,
                            "quantity": 4.0,
                        },
                    ),
                ],
            }
        )
        self.return_request_customer.action_confirm()
        sale_orders = self.return_request_customer.sale_order_ids
        pickings = self.return_request_customer.returned_picking_ids
        moves = self.return_request_customer.returned_picking_ids.mapped("move_lines")
        # For lot TSTPROD3LOT0001 we'll be returning:
        # ==> 10 units from SO01
        # ==> 2 units from SO02
        # For lot TSTPROD3LOT0002 we'll be returning:
        # ==> 4 units from SO01
        self.assertEqual(len(sale_orders), 2)
        self.assertEqual(len(pickings), 2)
        # Two moves with two move lines each
        self.assertEqual(len(moves), 2)
        self.assertAlmostEqual(sum(moves.mapped("product_uom_qty")), 16.0)
        # Process the return to validate all the pickings
        self.return_request_customer.action_validate()
        self.assertTrue(
            all([True if x == "done" else False for x in pickings.mapped("state")])
        )
        # For lot TSTPROD3LOT0001 we had 70 units
        prod_3_qty_lot_1 = self.prod_3.with_context(
            location=self.wh1.lot_stock_id.id, lot_id=self.prod_3_lot1.id
        ).qty_available
        # For lot TSTPROD3LOT0002 we had 2 units
        prod_3_qty_lot_2 = self.prod_3.with_context(
            location=self.wh1.lot_stock_id.id, lot_id=self.prod_3_lot2.id
        ).qty_available
        self.assertAlmostEqual(prod_3_qty_lot_1, 82.0)
        self.assertAlmostEqual(prod_3_qty_lot_2, 6.0)
        # There were 28 units in the sale orders.
        self.assertAlmostEqual(
            sum(sale_orders.mapped("order_line.qty_delivered")), 12.0
        )
        # Test the view action
        res = self.return_request_customer.action_view_sales()
        self.assertDictContainsSubset(
            {
                "type": "ir.actions.act_window",
                "res_model": "sale.order",
                "domain": "[('id', 'in', %s)]" % (sorted(sale_orders.ids)),
            },
            res,
        )

    def test_02_return_sale_stock_from_customer_single_sale(self):
        """Return stock from customer with a single result"""
        self.return_request_customer.write(
            {
                "partner_id": self.partner_customer_2.id,
                "to_refund": True,
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.prod_3.id,
                            "lot_id": self.prod_3_lot1.id,
                            "quantity": 1.0,
                        },
                    ),
                ],
            }
        )
        self.return_request_customer.action_confirm()
        sale_order = self.return_request_customer.sale_order_ids
        self.assertEqual(len(sale_order), 1)
        # Test the view action
        res = self.return_request_customer.action_view_sales()
        self.assertDictContainsSubset(
            {
                "type": "ir.actions.act_window",
                "res_model": "sale.order",
                "views": [(self.env.ref("sale.view_order_form").id, "form")],
                "res_id": sale_order.id,
            },
            res,
        )
