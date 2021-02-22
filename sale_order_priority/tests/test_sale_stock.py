# Copyright 2018 Simone Rubino - Agile Business Group
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.addons.sale.tests.test_sale_common import TestSale


class TestSaleStock(TestSale):
    def test_sale_order_priority(self):
        sale_order_priority = "3"
        self.sale_order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "priority": sale_order_priority,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": p.name,
                            "product_id": p.id,
                            "product_uom_qty": 2,
                            "product_uom": p.uom_id.id,
                            "price_unit": p.list_price,
                        },
                    )
                    for (_, p) in self.products.items()
                ],
            }
        )
        sale_order_line_priority = "2"
        for sol in self.sale_order.order_line:
            # Test that the order's priority has been
            # correctly assigned to the order lines
            self.assertEqual(
                sol.priority,
                sale_order_priority,
                "Priority of order lines does not match",
            )
            sol.priority = sale_order_line_priority
        # Confirm the order and check the picking
        self.sale_order.action_confirm()
        # Test that the lines' priority has been
        # correctly assigned to the generated pickings
        self.assertEqual(
            max(self.sale_order.picking_ids.mapped("priority")),
            sale_order_line_priority,
            "Priority of generated picking does not match",
        )
