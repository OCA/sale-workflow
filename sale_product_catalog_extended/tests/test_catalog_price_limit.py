# Copyright 2026 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from unittest.mock import patch

from odoo.tests.common import TransactionCase, tagged

from odoo.addons.sale_product_catalog_extended.models.product_product import (
    CATALOG_PRICE_CACHE_KEY,
)


@tagged("post_install", "-at_install")
class TestCatalogPriceLimit(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Price Limit Partner"})
        cls.pricelist = cls.env["product.pricelist"].create(
            {"name": "Price Limit Pricelist"}
        )
        cls.category_cheap, cls.category_expensive = cls.env["product.category"].create(
            [{"name": "Price Limit Cheap"}, {"name": "Price Limit Expensive"}]
        )
        cls.product_10, cls.product_20, cls.product_30 = cls.env[
            "product.product"
        ].create(
            [
                {
                    "name": "Price Limit 10",
                    "list_price": 10.0,
                    "categ_id": cls.category_cheap.id,
                },
                {
                    "name": "Price Limit 20",
                    "list_price": 20.0,
                    "categ_id": cls.category_cheap.id,
                },
                {
                    "name": "Price Limit 30",
                    "list_price": 30.0,
                    "categ_id": cls.category_expensive.id,
                },
            ]
        )
        cls.products = cls.product_10 | cls.product_20 | cls.product_30
        cls.order = cls.env["sale.order"].create(
            {"partner_id": cls.partner.id, "pricelist_id": cls.pricelist.id}
        )

    def setUp(self):
        super().setUp()
        # The prices are cached in the cursor, shared by the tests of the class
        self.env.cr.cache.pop(CATALOG_PRICE_CACHE_KEY, None)

    def _catalog(self):
        return self.env["product.product"].with_context(
            **self.order._get_action_add_from_catalog_extra_context()
        )

    def _domain(self, limit, *leaves):
        return [
            ("id", "in", self.products.ids),
            ("catalog_price_limit", "<=", limit),
            *leaves,
        ]

    def _create_history_lines(self, vals_list):
        history_order = self.env["sale.order"].create(
            {"partner_id": self.partner.id, "pricelist_id": self.pricelist.id}
        )
        return self.env["sale.order.line"].create(
            [
                {
                    "order_id": history_order.id,
                    "product_uom_qty": 1,
                    "qty_delivered": 1.0,
                    **vals,
                }
                for vals in vals_list
            ]
        )

    def test_price_limit_pricelist_price(self):
        """Only the products whose pricelist price is under the limit are
        shown, and the pager counts the same products."""
        catalog = self._catalog()
        domain = self._domain(20.0)
        self.assertEqual(
            catalog.search_fetch(domain, ["id"]), self.product_10 | self.product_20
        )
        self.assertEqual(catalog.search_count(domain), 2)

    def test_price_limit_uses_the_pricelist_rules(self):
        """The limit is compared with the pricelist price of the order, not
        with the sales price of the product."""
        self.env["product.pricelist.item"].create(
            [
                {
                    "pricelist_id": self.pricelist.id,
                    "applied_on": "0_product_variant",
                    "product_id": self.product_30.id,
                    "compute_price": "fixed",
                    "fixed_price": 5.0,
                },
                {
                    "pricelist_id": self.pricelist.id,
                    "applied_on": "0_product_variant",
                    "product_id": self.product_10.id,
                    "compute_price": "fixed",
                    "fixed_price": 50.0,
                },
            ]
        )
        self.assertEqual(
            self._catalog().search_fetch(self._domain(20.0), ["id"]),
            self.product_20 | self.product_30,
        )

    def test_price_limit_before_pagination(self):
        """The limit is applied before paginating, keeping the order, so every
        page is full of products under the limit."""
        catalog = self._catalog()
        domain = self._domain(20.0)
        # In this order the product over the limit would be the first one
        self.assertEqual(
            catalog.search_fetch(domain, ["id"], limit=1, order="name desc"),
            self.product_20,
        )
        self.assertEqual(
            catalog.search_fetch(domain, ["id"], offset=1, limit=1, order="name desc"),
            self.product_10,
        )
        self.assertEqual(catalog.search_count(domain, limit=1), 1)

    def test_price_limit_last_sale_price(self):
        """With the Last sale price, the last sale price is compared for the
        products that have one, and the pricelist price for the rest."""
        self._create_history_lines(
            [{"product_id": self.product_30.id, "price_unit": 8.0}]
        )
        catalog = self._catalog()
        self.assertEqual(
            catalog.search_fetch(self._domain(10.0), ["id"]), self.product_10
        )
        self.assertEqual(
            catalog.search_fetch(
                self._domain(10.0, ("catalog_price_mode", "=", "last_price")),
                ["id"],
            ),
            self.product_10 | self.product_30,
        )

    def test_price_limit_combined_with_origin(self):
        """The limit applies on top of the products of the chosen origin."""
        self._create_history_lines(
            [
                {"product_id": self.product_10.id, "price_unit": 10.0},
                {"product_id": self.product_30.id, "price_unit": 30.0},
            ]
        )
        catalog = self._catalog()
        domain = self._domain(20.0, ("catalog_last_sales", "=", "last_sales"))
        self.assertEqual(catalog.search_fetch(domain, ["id"]), self.product_10)
        self.assertEqual(catalog.search_count(domain), 1)

    def test_price_limit_ignored_outside_sale_orders(self):
        """Other catalogs (e.g. the purchase one) have no sale order to price
        the products with, so the limit does not filter."""
        catalog = self.env["product.product"].with_context(
            product_catalog_order_id=self.order.id,
            product_catalog_order_model="purchase.order",
        )
        self.assertEqual(
            catalog.search_fetch(self._domain(20.0), ["id"]), self.products
        )

    def test_price_limit_search_panel(self):
        """The search panel only offers the categories of the products under
        the limit."""
        result = self._catalog().search_panel_select_range(
            "categ_id", search_domain=self._domain(20.0)
        )
        category_ids = {value["id"] for value in result["values"]}
        self.assertIn(self.category_cheap.id, category_ids)
        self.assertNotIn(self.category_expensive.id, category_ids)

    def test_price_limit_prices_computed_once(self):
        """The records, their count and the search panel of a catalog load
        price each product once."""
        sale_order_class = type(self.env["sale.order"])
        with patch.object(
            sale_order_class,
            "_get_catalog_filter_prices",
            autospec=True,
            side_effect=sale_order_class._get_catalog_filter_prices,
        ) as mock:
            catalog = self._catalog()
            domain = self._domain(20.0)
            catalog.search_fetch(domain, ["id"])
            catalog.search_count(domain)
            catalog.search_panel_select_range("categ_id", search_domain=domain)
        self.assertEqual(mock.call_count, 1)
