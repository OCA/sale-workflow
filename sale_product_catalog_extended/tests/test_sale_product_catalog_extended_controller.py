# Copyright 2026 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests.common import HttpCase, tagged


@tagged("post_install", "-at_install")
class TestSaleProductCatalogExtendedController(HttpCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Catalog Test Partner"})
        cls.product = cls.env["product.product"].create(
            {"name": "Catalog Controller Product", "sale_ok": True}
        )
        cls.order = cls.env["sale.order"].create({"partner_id": cls.partner.id})
        cls.line = cls.env["sale.order.line"].create(
            {
                "order_id": cls.order.id,
                "product_id": cls.product.id,
                "product_uom_qty": 1,
            }
        )

    def test_open_order_line_returns_matching_line(self):
        self.authenticate("admin", "admin")
        result = self.make_jsonrpc_request(
            "/product/catalog/sale/open_order_line",
            {"order_id": self.order.id, "product_id": self.product.id},
        )
        self.assertEqual(result, self.line.ids)

    def test_get_order_line_data_returns_product_type(self):
        self.authenticate("admin", "admin")
        result = self.make_jsonrpc_request(
            "/product/catalog/sale/get_order_line_data",
            {"order_line_ids": self.line.ids},
        )
        self.assertEqual(result["productType"], self.product.type)
        self.assertEqual(result["quantity"], self.line.product_uom_qty)

    def test_exclude_from_last_sales_then_reappears_after_resale(self):
        self.authenticate("admin", "admin")
        exclusion_id = self.make_jsonrpc_request(
            "/product/catalog/sale/exclude_from_last_sales",
            {"order_id": self.order.id, "product_id": self.product.id},
        )
        self.assertTrue(exclusion_id)
        exclusion = self.env["sale.catalog.product.exclusion"].browse(exclusion_id)
        self.assertEqual(exclusion.partner_id, self.partner)
        self.assertEqual(exclusion.product_id, self.product)
