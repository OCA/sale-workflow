# Copyright 2013-2014 Camptocamp SA - Guewen Baconnier
# © 2016 ForgeFlow, S.L.
# © 2016 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.addons.base.tests.common import BaseCommon


class TestSaleSourcedByLine(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.sale_order_model = cls.env["sale.order"]
        cls.sale_order_line_model = cls.env["sale.order.line"]
        cls.stock_warehouse_model = cls.env["stock.warehouse"]

        cls.customer = cls.env["res.partner"].create({"name": "Test Customer"})
        cls.product_1 = cls.env["product.product"].create(
            {"name": "Test Product 1", "type": "consu", "is_storable": True}
        )
        cls.product_2 = cls.env["product.product"].create(
            {"name": "Test Product 2", "type": "consu", "is_storable": True}
        )
        cls.warehouse0 = cls.env["stock.warehouse"].search(
            [("company_id", "=", cls.env.company.id)], limit=1
        )
        cls.warehouse1 = cls.stock_warehouse_model.create(
            {"name": "Test Warehouse", "code": "TWH"}
        )

    def _create_order(self, warehouse_per_line):
        order = self.sale_order_model.create({"partner_id": self.customer.id})
        for product, warehouse in warehouse_per_line:
            vals = {
                "product_id": product.id,
                "product_uom_qty": 8,
                "order_id": order.id,
            }
            if warehouse:
                vals["warehouse_id"] = warehouse.id
            self.sale_order_line_model.create(vals)
        return order

    def test_sales_order_multi_source(self):
        """Lines sourced from different warehouses give one delivery each."""
        order = self._create_order(
            [(self.product_1, self.warehouse1), (self.product_2, self.warehouse0)]
        )
        order.action_confirm()
        self.assertEqual(len(order.picking_ids), 2)
        for line in order.order_line:
            self.assertEqual(line.move_ids.warehouse_id, line.warehouse_id)

    def test_sales_order_no_source(self):
        """Lines without a warehouse fall back to the order warehouse."""
        order = self._create_order([(self.product_1, False), (self.product_2, False)])
        order.warehouse_id = self.warehouse1
        self.assertEqual(order.order_line.warehouse_id, self.warehouse1)
        order.action_confirm()
        self.assertEqual(len(order.picking_ids), 1)

    def test_line_warehouse_kept_on_recompute(self):
        """A warehouse set on the line is not overwritten by the order one."""
        order = self._create_order([(self.product_1, self.warehouse1)])
        order.warehouse_id = self.warehouse0
        self.assertEqual(order.order_line.warehouse_id, self.warehouse1)
