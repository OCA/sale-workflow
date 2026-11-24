# Copyright 2026 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests.common import HttpCase, tagged


@tagged("post_install", "-at_install")
class TestSaleProductCatalogLastPriceCategory(HttpCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Catalog Test Partner"})
        cls.categ_ignore = cls.env["product.category"].create(
            {"name": "Catalog Pricelist Category", "catalog_ignore_last_price": True}
        )
        cls.product_last_price, cls.product_pricelist = cls.env[
            "product.product"
        ].create(
            [
                {"name": "Catalog Last Price Product", "list_price": 10.0},
                {
                    "name": "Catalog Pricelist Product",
                    "list_price": 10.0,
                    "categ_id": cls.categ_ignore.id,
                },
            ]
        )
        # The sale history the catalog takes the last sale prices from
        history_order = cls.env["sale.order"].create({"partner_id": cls.partner.id})
        cls.env["sale.order.line"].create(
            [
                {
                    "order_id": history_order.id,
                    "product_id": product.id,
                    "product_uom_qty": 1,
                    "qty_delivered": 1.0,
                    "price_unit": 7.0,
                }
                for product in cls.product_last_price + cls.product_pricelist
            ]
        )
        cls.order = cls.env["sale.order"].create({"partner_id": cls.partner.id})

    def setUp(self):
        super().setUp()
        self.authenticate("admin", "admin")

    def test_catalog_cards_without_last_price(self):
        """The cards of the products of the category do not show the last sale
        price, the cards of the other products do."""
        info = self.make_jsonrpc_request(
            "/product/catalog/order_lines_info",
            {
                "res_model": "sale.order",
                "order_id": self.order.id,
                "product_ids": (self.product_last_price + self.product_pricelist).ids,
                "catalog_show_last_price": True,
            },
        )
        self.assertAlmostEqual(info[str(self.product_last_price.id)]["lastPrice"], 7.0)
        self.assertNotIn("lastPrice", info[str(self.product_pricelist.id)])

    def test_catalog_line_with_pricelist_price(self):
        """The line added from the card of a product of the category takes the
        pricelist price."""
        price = self.make_jsonrpc_request(
            "/product/catalog/update_order_line_info",
            {
                "res_model": "sale.order",
                "order_id": self.order.id,
                "product_id": self.product_pricelist.id,
                "quantity": 1,
                "catalog_show_last_price": True,
            },
        )
        self.assertAlmostEqual(price, 10.0)
        self.assertAlmostEqual(self.order.order_line.price_unit, 10.0)
