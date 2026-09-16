# Copyright 2026 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestSaleProductCatalogExtended(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Catalog Test Partner"})
        cls.product_a, cls.product_b, cls.product_c = cls.env["product.product"].create(
            [
                {"name": "Catalog Product A", "sale_ok": True},
                {"name": "Catalog Product B", "sale_ok": True},
                {"name": "Catalog Product C", "sale_ok": True},
            ]
        )
        # A past, already-delivered order: this is the sale history the
        # catalog looks up. It must be a *different* order than the one
        # being edited, which the domain explicitly excludes (id != order_id).
        cls.history_order = cls.env["sale.order"].create({"partner_id": cls.partner.id})
        cls.line_a, cls.line_b = cls.env["sale.order.line"].create(
            [
                {
                    "order_id": cls.history_order.id,
                    "product_id": cls.product_a.id,
                    "product_uom_qty": 3,
                    "qty_delivered": 3.0,
                },
                {
                    "order_id": cls.history_order.id,
                    "product_id": cls.product_b.id,
                    "product_uom_qty": 1,
                    "qty_delivered": 1.0,
                },
            ]
        )
        # The order currently being edited, whose catalog is under test.
        cls.order = cls.env["sale.order"].create({"partner_id": cls.partner.id})

    def _last_sales_products(self):
        return (
            self.env["product.product"]
            .with_context(
                product_catalog_partner_id=self.partner.id,
                product_catalog_order_id=self.order.id,
            )
            .search_fetch([("catalog_origin_data", "=", "sale_order")], ["id"])
        )

    def test_search_fetch_last_sales_origin(self):
        """Only products delivered to the matched partner are returned, most
        frequently/heavily sold first, and unrelated leaves are preserved."""
        products = self._last_sales_products()
        self.assertIn(self.product_a, products)
        self.assertIn(self.product_b, products)
        self.assertNotIn(self.product_c, products)
        self.assertLess(
            list(products.ids).index(self.product_a.id),
            list(products.ids).index(self.product_b.id),
        )

    def test_search_fetch_combines_with_other_domain_leaves(self):
        """The rest of the catalog filters (e.g. name) still apply on top of
        the products coming from the chosen origin."""
        products = (
            self.env["product.product"]
            .with_context(
                product_catalog_partner_id=self.partner.id,
                product_catalog_order_id=self.order.id,
            )
            .search_fetch(
                [
                    ("catalog_origin_data", "=", "sale_order"),
                    ("name", "=", self.product_b.name),
                ],
                ["id"],
            )
        )
        self.assertEqual(products, self.product_b)

    def test_get_catalog_origin_product_ids_ignores_unknown_origin(self):
        """A leftover origin value from an uninstalled module must not crash
        the catalog, it should simply be ignored."""
        self.assertIsNone(
            self.env["product.product"]._get_catalog_origin_product_ids(
                [("catalog_origin_data", "=", "unknown_origin")]
            )
        )

    def test_last_sales_exclusion_is_idempotent(self):
        exclusion_id_1 = self.order._add_catalog_last_sales_exclusion(self.product_a.id)
        exclusion_id_2 = self.order._add_catalog_last_sales_exclusion(self.product_a.id)
        self.assertEqual(exclusion_id_1, exclusion_id_2)
        self.assertNotIn(self.product_a, self._last_sales_products())

    def test_last_sales_exclusion_dropped_on_resale(self):
        self.order._add_catalog_last_sales_exclusion(self.product_a.id)
        self.assertNotIn(self.product_a, self._last_sales_products())
        # Selling the product again (on any order) must free the exclusion.
        resale_order = self.env["sale.order"].create({"partner_id": self.partner.id})
        self.env["sale.order.line"].create(
            {
                "order_id": resale_order.id,
                "product_id": self.product_a.id,
                "product_uom_qty": 1,
            }
        )
        resale_order.action_confirm()
        self.assertIn(self.product_a, self._last_sales_products())

    def test_last_order_limit_config_parameter(self):
        self.env["ir.config_parameter"].sudo().set_param(
            "sale_product_catalog_extended.catalog_last_order_limit", "1"
        )
        products = self._last_sales_products()
        self.assertEqual(len(products), 1)
        self.assertEqual(products, self.product_a)
