# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import tagged

from odoo.addons.base.tests.common import BaseCommon


@tagged("post_install", "-at_install")
class TestSaleOrderLine(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Test Customer"})
        cls.product = cls._create_product("Storable Product", is_storable=True)
        cls.service_product = cls._create_product(
            "Service Product", product_type="service"
        )
        cls.warehouse = cls.env["stock.warehouse"].search(
            [("company_id", "=", cls.env.company.id)], limit=1
        )
        if not cls.warehouse:
            cls.warehouse = cls.env["stock.warehouse"].create(
                {
                    "name": "Test Warehouse 1",
                    "code": "QBW1",
                    "company_id": cls.env.company.id,
                }
            )
        cls.extra_warehouse = cls.env["stock.warehouse"].create(
            {
                "name": "Test Warehouse 2",
                "code": "QBW2",
                "company_id": cls.env.company.id,
            }
        )
        cls.order = cls.env["sale.order"].create({"partner_id": cls.partner.id})
        cls.line = cls._create_order_line(cls.product)
        cls.service_line = cls._create_order_line(cls.service_product)

    @classmethod
    def _create_product(cls, name, product_type="consu", is_storable=False):
        return (
            cls.env["product.template"]
            .create(
                {
                    "name": name,
                    "sale_ok": True,
                    "type": product_type,
                    "is_storable": is_storable,
                }
            )
            .product_variant_id
        )

    @classmethod
    def _create_order_line(cls, product):
        return cls.env["sale.order.line"].create(
            {
                "order_id": cls.order.id,
                "product_id": product.id,
                "name": product.display_name,
                "product_uom_qty": 1.0,
                "price_unit": 1.0,
            }
        )

    @classmethod
    def _update_available_quantity(cls, warehouse, quantity):
        cls.env["stock.quant"]._update_available_quantity(
            cls.product, warehouse.lot_stock_id, quantity
        )

    def test_display_widget_only_for_storable_products(self):
        self.assertTrue(self.line.display_qty_by_warehouse_widget)
        self.assertFalse(self.service_line.display_qty_by_warehouse_widget)

    def test_qty_by_warehouse_widget_data(self):
        self._update_available_quantity(self.warehouse, 7.0)
        self._update_available_quantity(self.extra_warehouse, 3.0)

        self.line.invalidate_recordset(["qty_by_warehouse_widget_data"])
        data = self.line.qty_by_warehouse_widget_data

        warehouse_row = data[self.warehouse.lot_stock_id.id]
        self.assertEqual(warehouse_row["warehouse_name"], self.warehouse.name)
        self.assertEqual(
            warehouse_row["location_name"], self.warehouse.lot_stock_id.display_name
        )
        self.assertEqual(warehouse_row["qty_available"], 7.0)

        extra_warehouse_row = data[self.extra_warehouse.lot_stock_id.id]
        self.assertEqual(
            extra_warehouse_row["warehouse_name"], self.extra_warehouse.name
        )
        self.assertEqual(
            extra_warehouse_row["location_name"],
            self.extra_warehouse.lot_stock_id.display_name,
        )
        self.assertEqual(extra_warehouse_row["qty_available"], 3.0)

    def test_qty_by_warehouse_widget_data_empty_for_non_storable_product(self):
        self.assertEqual(self.service_line.qty_by_warehouse_widget_data, [])
