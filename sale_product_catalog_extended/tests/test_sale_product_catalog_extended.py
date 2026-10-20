# Copyright 2026 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields
from odoo.tests import Form
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
            .search_fetch([("catalog_last_sales", "=", "last_sales")], ["id"])
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
                    ("catalog_last_sales", "=", "last_sales"),
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

    def test_search_fetch_last_sales_origin_pagination(self):
        """The origin products are paginated keeping their ordering, and the
        count used by the pager only includes the origin products."""
        product_model = self.env["product.product"].with_context(
            product_catalog_partner_id=self.partner.id,
            product_catalog_order_id=self.order.id,
        )
        domain = [("catalog_last_sales", "=", "last_sales")]
        self.assertEqual(
            product_model.search_fetch(domain, ["id"], limit=1), self.product_a
        )
        self.assertEqual(
            product_model.search_fetch(domain, ["id"], offset=1, limit=1),
            self.product_b,
        )
        self.assertEqual(product_model.search_count(domain), 2)
        self.assertEqual(product_model.search_count(domain, limit=1), 1)

    def test_last_sales_across_salespeople(self):
        """A salesperson restricted to their own documents still sees the
        partner history and last prices of the other salespeople's orders."""
        self.history_order.user_id = self.env.ref("base.user_admin")
        self.line_a.price_unit = 7.5
        salesman = self.env["res.users"].create(
            {
                "name": "Own Documents Salesman",
                "login": "catalog_own_documents_salesman",
                "groups_id": [
                    (6, 0, [self.env.ref("sales_team.group_sale_salesman").id])
                ],
            }
        )
        self.order.user_id = salesman
        order = self.order.with_user(salesman)
        products = (
            self.env["product.product"]
            .with_user(salesman)
            .with_context(**order._get_catalog_history_context())
            .search_fetch([("catalog_last_sales", "=", "last_sales")], ["id"])
        )
        self.assertEqual(products, self.product_a | self.product_b)
        self.assertEqual(
            order._get_catalog_last_prices(self.product_a.ids),
            {self.product_a.id: 7.5},
        )

    def test_history_partner_default_preselects_search_panel(self):
        """The field default (ir.default) of the history partner preselects it
        in the catalog search panel."""
        context = self.order._get_action_add_from_catalog_extra_context()
        self.assertNotIn("searchpanel_default_catalog_history_partner", context)
        self.env["ir.default"].set(
            "product.product",
            "catalog_history_partner",
            "delivery_address",
            company_id=self.order.company_id.id,
        )
        context = self.order._get_action_add_from_catalog_extra_context()
        self.assertEqual(
            context["searchpanel_default_catalog_history_partner"],
            "delivery_address",
        )

    def test_history_partner_delivery_address(self):
        """Choosing the delivery address matches the history against it
        instead of against the whole commercial partner."""
        address_a, address_b = self.env["res.partner"].create(
            [
                {"name": "Address A", "type": "delivery", "parent_id": self.partner.id},
                {"name": "Address B", "type": "delivery", "parent_id": self.partner.id},
            ]
        )
        self.history_order.partner_shipping_id = address_a
        self.line_a.price_unit = 7.5
        self.order.partner_shipping_id = address_b
        product_model = self.env["product.product"].with_context(
            **self.order._get_catalog_history_context()
        )
        origin = [("catalog_last_sales", "=", "last_sales")]
        delivery = [("catalog_history_partner", "=", "delivery_address")]
        self.assertEqual(
            product_model.search_fetch(origin, ["id"]),
            self.product_a | self.product_b,
        )
        self.assertFalse(product_model.search_fetch(origin + delivery, ["id"]))
        self.assertEqual(product_model.search_count(origin + delivery), 0)
        self.assertEqual(
            self.order._get_catalog_last_prices(self.product_a.ids),
            {self.product_a.id: 7.5},
        )
        self.assertFalse(
            self.order._get_catalog_last_prices(
                self.product_a.ids, use_delivery_address=True
            )
        )
        self.order.partner_shipping_id = address_a
        product_model = product_model.with_context(
            **self.order._get_catalog_history_context()
        )
        self.assertEqual(
            product_model.search_fetch(origin + delivery, ["id"]),
            self.product_a | self.product_b,
        )

    def test_history_partner_exclusions_dropped_for_both_partners(self):
        """An exclusion made for the delivery address is also dropped when the
        product is sold again."""
        address = self.env["res.partner"].create(
            {"name": "Address", "type": "delivery", "parent_id": self.partner.id}
        )
        self.order.partner_shipping_id = address
        self.order._add_catalog_last_sales_exclusion(
            self.product_a.id, use_delivery_address=True
        )
        exclusion_model = self.env["sale.catalog.product.exclusion"]
        self.assertTrue(exclusion_model.search([("partner_id", "=", address.id)]))
        self.env["sale.order.line"].create(
            {
                "order_id": self.order.id,
                "product_id": self.product_a.id,
                "product_uom_qty": 1,
            }
        )
        self.order.action_confirm()
        self.assertFalse(exclusion_model.search([("partner_id", "=", address.id)]))

    def test_last_price_in_product_uom(self):
        """The last price is expressed in the product UoM, the one the catalog
        adds lines in, whatever the UoM of the previous line."""
        # Created in dozens instead of changing the UoM of an existing line:
        # with sale_project installed, that change recomputes the delivered
        # quantity of a line without stock moves back to 0.
        self.env["sale.order.line"].create(
            {
                "order_id": self.history_order.id,
                "product_id": self.product_c.id,
                "product_uom": self.env.ref("uom.product_uom_dozen").id,
                "product_uom_qty": 1,
                "qty_delivered": 1.0,
                "price_unit": 12.0,
            }
        )
        self.assertAlmostEqual(
            self.order._get_catalog_last_prices(self.product_c.ids)[self.product_c.id],
            1.0,
        )

    def test_last_order_days_config_parameter(self):
        """The Last sales period is configurable in days, 180 by default."""
        self.history_order.date_order = fields.Datetime.subtract(
            fields.Datetime.now(), days=90
        )
        self.assertIn(self.product_a, self._last_sales_products())
        self.env["ir.config_parameter"].sudo().set_param(
            "sale_product_catalog_extended.catalog_last_order_days", "60"
        )
        self.assertNotIn(self.product_a, self._last_sales_products())

    def test_settings_preselect_the_search_panel(self):
        """The Sales settings set the defaults preselected in the catalog search
        panel and the last sales period."""
        settings = self.env["res.config.settings"].create(
            {
                "default_catalog_last_sales": "last_sales",
                "default_catalog_price_mode": "last_price",
                "catalog_last_order_days": 30,
                "catalog_last_order_limit": 5,
            }
        )
        settings.execute()
        context = self.order._get_action_add_from_catalog_extra_context()
        self.assertEqual(
            context["searchpanel_default_catalog_last_sales"], "last_sales"
        )
        self.assertEqual(
            context["searchpanel_default_catalog_price_mode"], "last_price"
        )
        self.assertNotIn("searchpanel_default_catalog_origin_data", context)
        get_param = self.env["ir.config_parameter"].sudo().get_param
        self.assertEqual(
            get_param("sale_product_catalog_extended.catalog_last_order_days"), "30"
        )
        self.assertEqual(
            get_param("sale_product_catalog_extended.catalog_last_order_limit"), "5"
        )

    def test_last_sales_exclusion_deleted_from_its_list(self):
        """Deleting an exclusion from its configuration list offers the product
        again in the Last sales option."""
        action = self.env.ref(
            "sale_product_catalog_extended.sale_catalog_product_exclusion_action"
        )
        self.assertEqual(action.res_model, "sale.catalog.product.exclusion")
        exclusion_id = self.order._add_catalog_last_sales_exclusion(self.product_a.id)
        self.assertNotIn(self.product_a, self._last_sales_products())
        self.env["sale.catalog.product.exclusion"].browse(exclusion_id).unlink()
        self.assertIn(self.product_a, self._last_sales_products())

    def test_settings_show_history_partner(self):
        """The History section is hidden unless it is enabled in the settings."""
        self.assertFalse(
            self.order._get_action_add_from_catalog_extra_context()[
                "catalog_show_history_partner"
            ]
        )
        self.env["res.config.settings"].create(
            {"catalog_show_history_partner": True}
        ).execute()
        self.assertTrue(
            self.order._get_action_add_from_catalog_extra_context()[
                "catalog_show_history_partner"
            ]
        )

    def test_sort_by_name_in_the_language_of_the_user(self):
        """The Name sort orders the products by their name translated to the
        language of the user."""
        self.env["res.lang"]._activate_lang("es_ES")
        zucchini, apple = self.env["product.product"].create(
            [
                {"name": "Zucchini", "sale_ok": True},
                {"name": "Apple", "sale_ok": True},
            ]
        )
        zucchini.with_context(lang="es_ES").name = "Calabacín"
        apple.with_context(lang="es_ES").name = "Manzana"
        domain = [("id", "in", (zucchini | apple).ids), ("catalog_sort", "=", "name")]
        products = self.env["product.product"]
        self.assertEqual(
            products.search_fetch(domain, ["id"]).ids, [apple.id, zucchini.id]
        )
        self.assertEqual(
            products.with_context(lang="es_ES").search_fetch(domain, ["id"]).ids,
            [zucchini.id, apple.id],
        )

    def test_sort_by_category(self):
        """The Category sort orders the products by category, then by name."""
        category_b, category_a = self.env["product.category"].create(
            [{"name": "Catalog Category B"}, {"name": "Catalog Category A"}]
        )
        product_1, product_3, product_2 = self.env["product.product"].create(
            [
                {"name": "Catalog Sort 1", "categ_id": category_b.id},
                {"name": "Catalog Sort 3", "categ_id": category_a.id},
                {"name": "Catalog Sort 2", "categ_id": category_a.id},
            ]
        )
        domain = [
            ("id", "in", (product_1 | product_2 | product_3).ids),
            ("catalog_sort", "=", "category"),
        ]
        self.assertEqual(
            self.env["product.product"].search_fetch(domain, ["id"]).ids,
            [product_2.id, product_3.id, product_1.id],
        )

    def test_sort_last_sales_keeps_the_most_sold(self):
        """With the last sales, the sort orders the products the last sales
        keep, so the limit still keeps the most sold ones."""
        self.product_a.name = "Catalog Product Z"
        products = self.env["product.product"].with_context(
            product_catalog_partner_id=self.partner.id,
            product_catalog_order_id=self.order.id,
        )
        last_sales = [("catalog_last_sales", "=", "last_sales")]
        sorted_last_sales = last_sales + [("catalog_sort", "=", "name")]
        self.assertEqual(
            products.search_fetch(last_sales, ["id"]).ids,
            [self.product_a.id, self.product_b.id],
        )
        self.assertEqual(
            products.search_fetch(sorted_last_sales, ["id"]).ids,
            [self.product_b.id, self.product_a.id],
        )
        self.env["ir.config_parameter"].sudo().set_param(
            "sale_product_catalog_extended.catalog_last_order_limit", "1"
        )
        self.assertEqual(
            products.search_fetch(sorted_last_sales, ["id"]).ids,
            [self.product_a.id],
        )

    def test_settings_sort(self):
        """The sort default preselects it in the search panel, whose section is
        only shown when enabled in the settings."""
        context = self.order._get_action_add_from_catalog_extra_context()
        self.assertFalse(context["catalog_show_sort"])
        self.assertNotIn("searchpanel_default_catalog_sort", context)
        self.env["res.config.settings"].create(
            {"default_catalog_sort": "category", "catalog_show_sort": True}
        ).execute()
        context = self.order._get_action_add_from_catalog_extra_context()
        self.assertTrue(context["catalog_show_sort"])
        self.assertEqual(context["searchpanel_default_catalog_sort"], "category")

    def test_settings_catalog_layout(self):
        """The catalog opens with the grid layout unless the rows layout is
        chosen in the settings."""
        self.assertEqual(
            self.order._get_action_add_from_catalog_extra_context()["catalog_layout"],
            "grid",
        )
        self.env["res.config.settings"].create({"catalog_layout": "rows"}).execute()
        self.assertEqual(
            self.order.action_add_from_catalog()["context"]["catalog_layout"],
            "rows",
        )

    def _new_line_form(self, order, product, **options):
        """The new line form the catalog card of ``product`` opens, with the
        context the catalog kanban record sends (``onClickAddNewOrderLine``)."""
        params = {
            "order_id": order.id,
            "product_id": product.id,
            "quantity": 0,
            "res_model": "sale.order",
            **options,
        }
        return Form(
            self.env["sale.order.line"].with_context(
                default_order_id=order.id,
                default_product_id=product.id,
                catalog_line_params=params,
            ),
            view="sale_product_catalog_extended.sale_order_line_view_form_editable",
        )

    def test_new_line_form_from_card_matches_the_catalog_line(self):
        """The new line form opened from a card of a confirmed order is not
        created until it is saved, and it ends as the line the catalog adds:
        at the end of the order and with the last sale price, kept when the
        quantity changes."""
        self.line_a.price_unit = 7.5
        self.env["sale.order.line"].create(
            {
                "order_id": self.order.id,
                "product_id": self.product_b.id,
                "product_uom_qty": 1,
                "sequence": 15,
            }
        )
        self.order.action_confirm()
        line_form = self._new_line_form(
            self.order, self.product_a, catalog_show_last_price=True
        )
        self.assertAlmostEqual(line_form.price_unit, 7.5)
        line_form.product_uom_qty = 3
        self.assertAlmostEqual(line_form.price_unit, 7.5)
        self.assertNotIn(self.product_a, self.order.order_line.product_id)
        line = line_form.save()
        self.assertEqual(line.order_id, self.order)
        self.assertEqual(line.product_id, self.product_a)
        self.assertEqual(line.sequence, 16)
        self.assertEqual(line.product_uom_qty, 3)
        self.assertAlmostEqual(line.price_unit, 7.5)
        # The pricelist price stays as the reference, so it is taken as a
        # manual price, as on the lines the catalog adds.
        self.assertAlmostEqual(line.technical_price_unit, self.product_a.lst_price)

    def test_new_line_form_from_card_without_last_price(self):
        """Without the last sale price mode the line keeps the pricelist
        price."""
        self.line_a.price_unit = 7.5
        line = self._new_line_form(self.order, self.product_a).save()
        self.assertAlmostEqual(line.price_unit, self.product_a.lst_price)
        self.assertEqual(line.sequence, 10)

    def test_new_line_form_from_card_does_not_leak_defaults(self):
        """The ``default_*`` keys of the form context do not reach the records
        created along with the line (e.g. the stock moves of a confirmed
        order): the line is created in a context without them."""
        contexts = []
        lines_model = type(self.env["sale.order.line"])
        original = lines_model._remove_catalog_last_sales_exclusions

        def remove_exclusions(lines):
            contexts.append(lines.env.context)
            return original(lines)

        self.patch(
            lines_model, "_remove_catalog_last_sales_exclusions", remove_exclusions
        )
        self._new_line_form(self.order, self.product_a).save()
        self.assertEqual(len(contexts), 1)
        self.assertFalse([key for key in contexts[0] if key.startswith("default_")])
        self.assertNotIn("catalog_line_params", contexts[0])

    def test_delivery_address_option_on_the_cards_of_the_lines(self):
        """The cards of the order lines of a product with several lines send
        the delivery address option back too, like the product card."""
        self.env["sale.order.line"].create(
            [
                {
                    "order_id": self.order.id,
                    "product_id": self.product_a.id,
                    "product_uom_qty": qty,
                }
                for qty in (1, 2)
            ]
        )
        data = self.order._get_product_catalog_order_line_info(
            self.product_a.ids, catalog_use_delivery_address=True
        )[self.product_a.id]
        self.assertEqual(len(data["lines"]), 2)
        for card in [data, *data["lines"]]:
            self.assertIs(card["catalogUseDeliveryAddress"], True)
