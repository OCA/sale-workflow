# Copyright 2018 Simone Rubino - Agile Business Group
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.addons.sale.tests.common import TestSaleCommonBase


class TestSaleStock(TestSaleCommonBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.company = cls.env["res.company"].create(
            {
                "name": "Test Company",
                "currency_id": cls.env.ref("base.EUR").id,
            }
        )

        cls.company_data = cls.setup_sale_configuration_for_company(cls.company)

        cls.partner = cls.env["res.partner"].create(
            {
                "name": "partner1",
                "company_id": False,
            }
        )

    def test_sale_order_priority(self):
        sale_order_priority = "1"
        self.sale_order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "priority": sale_order_priority,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": self.company_data["product_order_cost"].name,
                            "product_id": self.company_data["product_order_cost"].id,
                            "product_uom_qty": 2,
                            "qty_delivered": 1,
                            "product_uom": self.company_data[
                                "product_order_cost"
                            ].uom_id.id,
                            "price_unit": self.company_data[
                                "product_order_cost"
                            ].list_price,
                        },
                    ),
                ],
            }
        )
        sale_order_line_priority = "0"
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
