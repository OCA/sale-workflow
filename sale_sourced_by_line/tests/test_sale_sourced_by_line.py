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

        # Refs
        cls.customer = cls.env.ref("base.res_partner_2")
        cls.product_1 = cls.env.ref("product.product_product_27")
        cls.product_2 = cls.env.ref("product.product_product_24")
        cls.service_product = cls.env["product.product"].create(
            {"name": "Service Product", "type": "service"}
        )
        cls.warehouse0 = cls.env.ref("stock.warehouse0")
        cls.warehouse1 = cls.stock_warehouse_model.create(
            {"name": "Test Warehouse", "code": "TWH"}
        )

    def _create_order(self, warehouse=None):
        vals = {"partner_id": self.customer.id}
        if warehouse:
            vals["warehouse_id"] = warehouse.id
        return self.sale_order_model.create(vals)

    def _create_line(self, order, product, warehouse=None):
        vals = {"product_id": product.id, "product_uom_qty": 8, "order_id": order.id}
        if warehouse:
            vals["warehouse_id"] = warehouse.id
        return self.sale_order_line_model.create(vals)

    def test_sales_order_multi_source(self):
        so = self._create_order()
        self._create_line(so, self.product_1, self.warehouse1)
        self._create_line(so, self.product_2, self.warehouse0)
        # confirm quotation
        so.action_confirm()
        self.assertEqual(
            len(so.picking_ids),
            2,
            f"2 delivery orders expected. Got {len(so.picking_ids)} instead",
        )
        for line in so.order_line:
            self.assertEqual(
                line.procurement_group_id.name,
                line.order_id.name + "/" + line.warehouse_id.name,
                "Wrong procurement group name",
            )
            for move in line.move_ids:
                self.assertEqual(
                    move.group_id, line.procurement_group_id, "Wrong move group"
                )
                self.assertEqual(
                    move.picking_id.group_id,
                    line.procurement_group_id,
                    "Wrong picking group",
                )
                # the warehouse of the line is used for its stock moves
                self.assertEqual(
                    move.warehouse_id, line.warehouse_id, "Wrong move warehouse"
                )

    def test_sales_order_no_source(self):
        so = self._create_order(self.warehouse1)
        line = self._create_line(so, self.product_1)
        self._create_line(so, self.product_2)
        # confirm quotation
        so.action_confirm()
        self.assertEqual(line.warehouse_id, self.warehouse1)
        self.assertEqual(
            len(so.picking_ids),
            1,
            f"1 delivery order expected. Got {len(so.picking_ids)} instead",
        )

    def test_warehouse_change_on_confirm(self):
        # all lines from the same warehouse, different from the order one:
        # it becomes the warehouse of the order
        so = self._create_order(self.warehouse0)
        self._create_line(so, self.product_1, self.warehouse1)
        self._create_line(so, self.product_2, self.warehouse1)
        so.action_confirm()
        self.assertEqual(so.warehouse_id, self.warehouse1)

        # several source warehouses: the order's warehouse is left untouched
        so_2 = self._create_order(self.warehouse0)
        self._create_line(so_2, self.product_1, self.warehouse1)
        self._create_line(so_2, self.product_2, self.warehouse0)
        so_2.action_confirm()
        self.assertEqual(so_2.warehouse_id, self.warehouse0)

    def test_multiple_source_warehouses_message(self):
        so = self._create_order()
        line_1 = self._create_line(so, self.product_1, self.warehouse1)
        self.assertFalse(so.multiple_source_warehouses_message)

        self._create_line(so, self.product_2, self.warehouse0)
        self.assertIn(self.warehouse0.name, so.multiple_source_warehouses_message)
        self.assertIn(self.warehouse1.name, so.multiple_source_warehouses_message)

        # a single source warehouse again hides the message
        line_1.warehouse_id = self.warehouse0
        self.assertFalse(so.multiple_source_warehouses_message)

    def test_multiple_source_warehouses_no_goods_lines(self):
        # section, note and service lines are not source warehouses
        so = self._create_order(self.warehouse0)
        self._create_line(so, self.product_1, self.warehouse1)
        self.sale_order_line_model.create(
            {"order_id": so.id, "display_type": "line_section", "name": "Section"}
        )
        self.sale_order_line_model.create(
            {"order_id": so.id, "display_type": "line_note", "name": "Note"}
        )
        self._create_line(so, self.service_product)
        self.assertFalse(so.multiple_source_warehouses_message)

        # the order warehouse is switched to the only goods source on confirm
        so.action_confirm()
        self.assertEqual(so.warehouse_id, self.warehouse1)
