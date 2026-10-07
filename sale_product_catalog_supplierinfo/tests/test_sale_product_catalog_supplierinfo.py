# Copyright 2026 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from types import SimpleNamespace

from odoo import Command
from odoo.tests import tagged

from odoo.addons.base.tests.common import BaseCommon
from odoo.addons.sale_product_catalog_supplierinfo.models import sale_order


@tagged("post_install", "-at_install")
class TestSaleProductCatalogSupplierinfo(BaseCommon):
    """Regression coverage for the vendor-price reactivity this module ported
    over from 15.0's sale_order_product_picker_supplierinfo (see this
    commit's message for the full root-cause writeup: real report was a
    product with 2 different, concurrently valid vendor prices always
    showing the same price regardless of which vendor was picked).
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Test customer"})
        cls.vendor_a = cls.env["res.partner"].create({"name": "Vendor A"})
        cls.vendor_b = cls.env["res.partner"].create({"name": "Vendor B"})
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test product",
                "standard_price": 999.0,
                "seller_ids": [
                    Command.create({"partner_id": cls.vendor_a.id, "price": 10.0}),
                    Command.create({"partner_id": cls.vendor_b.id, "price": 20.0}),
                ],
            }
        )
        cls.pricelist = cls.env["product.pricelist"].create({"name": "Test pricelist"})
        # Same setup found in the real report: a category rule based on
        # supplierinfo (created first, lower id) *and* one based on
        # standard_price (created after, higher id) for the very same
        # category - a generic cost-based price with a vendor-specific
        # override. Nothing besides "a vendor was requested" should decide
        # which one applies; product.pricelist.item's own _order otherwise
        # always resolves the higher id, i.e. standard_price, regardless.
        cls.supplierinfo_item = cls.env["product.pricelist.item"].create(
            {
                "pricelist_id": cls.pricelist.id,
                "applied_on": "2_product_category",
                "categ_id": cls.product.categ_id.id,
                "base": "supplierinfo",
                "compute_price": "formula",
            }
        )
        cls.standard_price_item = cls.env["product.pricelist.item"].create(
            {
                "pricelist_id": cls.pricelist.id,
                "applied_on": "2_product_category",
                "categ_id": cls.product.categ_id.id,
                "base": "standard_price",
                "compute_price": "formula",
            }
        )
        cls.mto = cls.env.ref("stock.route_warehouse0_mto")
        cls.mto.active = True
        cls.buy = cls.env.ref("purchase_stock.route_warehouse0_buy")
        cls.buy.sale_selectable = True

    def _create_line(self, vendor=False, supplierinfo=False):
        order = self.env["sale.order"].create(
            {"partner_id": self.partner.id, "pricelist_id": self.pricelist.id}
        )
        return self.env["sale.order.line"].create(
            {
                "order_id": order.id,
                "product_id": self.product.id,
                "product_uom_qty": 1,
                "vendor_id": vendor.id if vendor else False,
                "supplierinfo_id": supplierinfo.id if supplierinfo else False,
            }
        )

    def test_tie_break_without_vendor_keeps_generic_price(self):
        """No vendor requested: falls back to the generic (standard_price)
        rule, same as before this fix - this must NOT regress."""
        self.assertAlmostEqual(
            self.pricelist._get_product_price(self.product, 1), 999.0
        )

    def test_tie_break_with_vendor_forced_via_context(self):
        """force_filter_supplier_id alone (bypassing the sale order line
        entirely) already breaks the tie in favor of the vendor rule - this
        is the layer product_pricelist.py._get_applicable_rules() fixes."""
        price_a = self.pricelist._get_product_price(
            self.product.with_context(force_filter_supplier_id=self.vendor_a), 1
        )
        price_b = self.pricelist._get_product_price(
            self.product.with_context(force_filter_supplier_id=self.vendor_b), 1
        )
        self.assertAlmostEqual(price_a, 10.0)
        self.assertAlmostEqual(price_b, 20.0)

    def test_sale_order_line_price_differs_by_vendor(self):
        """End-to-end through a real sale.order.line: this is the exact
        report reproduced (2 vendor prices, same product, price used to be
        identical regardless of which vendor was picked) - covers the
        deeper layer too (_compute_pricelist_item_id resolving the rule
        against the vendor-annotated product, not core's bare product_id)."""
        line_a = self._create_line(vendor=self.vendor_a)
        line_b = self._create_line(vendor=self.vendor_b)
        self.assertAlmostEqual(line_a.price_unit, 10.0)
        self.assertAlmostEqual(line_b.price_unit, 20.0)
        self.assertNotEqual(line_a.price_unit, line_b.price_unit)

    def test_vendor_change_on_existing_line_recomputes_price(self):
        """Editing just vendor_id on an existing line (no product/qty
        change) must refresh price_unit - core's own _compute_price_unit
        only depends on product_id/product_uom/product_uom_qty, so without
        this module's extended @api.depends nothing would react at all."""
        line = self._create_line()
        self.assertAlmostEqual(line.price_unit, 999.0)
        line.vendor_id = self.vendor_b
        self.assertAlmostEqual(line.price_unit, 20.0)

    def test_supplierinfo_id_pins_the_exact_row(self):
        """A vendor with more than one concurrently valid supplierinfo row
        (real, confirmed data on the original report) can't be
        disambiguated by vendor_id alone - _select_seller() would just pick
        the cheapest one. Pinning supplierinfo_id must win instead."""
        expensive = self.env["product.supplierinfo"].create(
            {
                "partner_id": self.vendor_a.id,
                "product_tmpl_id": self.product.product_tmpl_id.id,
                "price": 50.0,
            }
        )
        # Default resolution (no pin): the cheaper of vendor_a's two rows.
        cheap_line = self._create_line(vendor=self.vendor_a)
        self.assertAlmostEqual(cheap_line.price_unit, 10.0)
        # Pinned to the pricier row: that one wins instead.
        pinned_line = self._create_line(vendor=self.vendor_a, supplierinfo=expensive)
        self.assertAlmostEqual(pinned_line.price_unit, 50.0)

    def test_select_seller_honors_forced_supplierinfo_item(self):
        """Direct coverage of product.product._select_seller()'s
        short-circuit, independent of any pricelist."""
        vendor_a_seller = self.product.seller_ids.filtered(
            lambda s: s.partner_id == self.vendor_a
        )
        seller = self.product.with_context(
            force_supplierinfo_item_id=vendor_a_seller.id
        )._select_seller(partner_id=self.vendor_b)
        # Even though partner_id points at vendor_b, the pinned row wins.
        self.assertEqual(seller, vendor_a_seller)

    def test_select_seller_ignores_forced_item_of_another_product(self):
        """The pinned row travels in the context, so it is only honoured for
        the product it belongs to."""
        other_product = self.env["product.product"].create(
            {
                "name": "Other product",
                "seller_ids": [
                    Command.create({"partner_id": self.vendor_b.id, "price": 30.0})
                ],
            }
        )
        vendor_a_seller = self.product.seller_ids.filtered(
            lambda s: s.partner_id == self.vendor_a
        )
        seller = other_product.with_context(
            force_supplierinfo_item_id=vendor_a_seller.id
        )._select_seller(partner_id=self.vendor_b)
        self.assertEqual(seller, other_product.seller_ids)

    def test_purchase_price_in_line_units(self):
        """The vendor price is converted to the sale line UoM and currency."""
        if "purchase_price" not in self.env["sale.order.line"]._fields:
            self.skipTest("sale_margin is not installed")
        line = self._create_line(vendor=self.vendor_a)
        self.assertAlmostEqual(line.purchase_price, 10.0)
        line.product_uom = self.env.ref("uom.product_uom_dozen")
        self.assertAlmostEqual(line.purchase_price, 120.0)
        currency = self.env["res.currency"].create(
            {
                "name": "SPC",
                "symbol": "S",
                "rate_ids": [Command.create({"name": "2000-01-01", "rate": 2.0})],
            }
        )
        line.product_id.seller_ids.filtered(
            lambda s: s.partner_id == self.vendor_a
        ).currency_id = currency
        line = self._create_line(vendor=self.vendor_a)
        expected = currency._convert(
            10.0, line.currency_id, line.company_id, line.order_id.date_order
        )
        self.assertAlmostEqual(line.purchase_price, expected)

    def test_supplierinfo_origin_shows_the_supplierinfo_variants(self):
        """A variant supplierinfo only brings that variant to the Suppliers
        origin, while a template one brings every variant, and each card shows
        the rows of its own variant plus the template ones."""
        attribute = self.env["product.attribute"].create({"name": "Origin size"})
        values = self.env["product.attribute.value"].create(
            [{"name": name, "attribute_id": attribute.id} for name in "SML"]
        )
        template_variant_row, template_wide_row = self.env["product.template"].create(
            [
                {
                    "name": name,
                    "attribute_line_ids": [
                        Command.create(
                            {
                                "attribute_id": attribute.id,
                                "value_ids": [Command.set(values.ids)],
                            }
                        )
                    ],
                }
                for name in ("Variant row product", "Template row product")
            ]
        )
        small = template_variant_row.product_variant_ids[0]
        self.env["product.supplierinfo"].create(
            [
                {
                    "partner_id": self.vendor_a.id,
                    "product_tmpl_id": template_variant_row.id,
                    "product_id": small.id,
                    "price": 5.0,
                },
                {
                    "partner_id": self.vendor_b.id,
                    "product_tmpl_id": template_wide_row.id,
                    "price": 6.0,
                },
            ]
        )
        product_ids = self.env[
            "product.product"
        ]._get_product_picker_data_supplierinfo()
        self.assertIn(small.id, product_ids)
        self.assertFalse(
            set(product_ids)
            & set((template_variant_row.product_variant_ids - small).ids)
        )
        self.assertTrue(
            set(template_wide_row.product_variant_ids.ids) <= set(product_ids)
        )
        order = self.env["sale.order"].create(
            {"partner_id": self.partner.id, "pricelist_id": self.pricelist.id}
        )
        cards = order._get_product_catalog_order_line_info(
            template_wide_row.product_variant_ids.ids, catalog_origin_supplierinfo=True
        )
        for variant in template_wide_row.product_variant_ids:
            self.assertEqual(
                [card.get("vendorId") for card in cards[variant.id]["vendorLines"]],
                [self.vendor_b.id],
            )

    def test_purchase_order_line_uses_the_pinned_supplierinfo(self):
        """MTO/buy flow: the purchase order line generated from the sale
        line's procurement must price from the exact supplierinfo the sale
        line resolved to, not whichever one core's own _select_seller()
        would re-derive from the vendor alone (the cheapest, by default)."""
        expensive = self.env["product.supplierinfo"].create(
            {
                "partner_id": self.vendor_a.id,
                "product_tmpl_id": self.product.product_tmpl_id.id,
                "price": 50.0,
            }
        )
        order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "pricelist_id": self.pricelist.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": self.product.id,
                            "product_uom_qty": 1,
                            "route_id": self.mto.id,
                            "vendor_id": self.vendor_a.id,
                            "supplierinfo_id": expensive.id,
                        }
                    )
                ],
            }
        )
        order.action_confirm()
        purchase_orders = order._get_purchase_orders()
        self.assertEqual(len(purchase_orders), 1)
        self.assertEqual(purchase_orders.partner_id, self.vendor_a)
        self.assertAlmostEqual(purchase_orders.order_line.price_unit, 50.0)

    def test_catalog_shows_one_card_per_supplierinfo_not_per_vendor(self):
        """A vendor with more than one concurrently valid ``product.supplierinfo``
        row must get one catalog card PER ROW, not a single card collapsing
        them - real report: a product with 2 vendor prices only ever showed
        one of them in the catalog. Adding from each card must pin THAT
        card's exact row, not just the vendor, on its own, separate order
        line - both in the sale order line and, end-to-end through MTO/buy,
        in the purchase order line generated from it."""
        cheap = self.product.seller_ids.filtered(
            lambda s: s.partner_id == self.vendor_a
        )
        cheap.sequence = 1
        expensive = self.env["product.supplierinfo"].create(
            {
                "partner_id": self.vendor_a.id,
                "product_tmpl_id": self.product.product_tmpl_id.id,
                "price": 50.0,
                "sequence": 0,
                "comment": "Comentario caro",
            }
        )
        # The cached ``seller_ids`` value (fetched, and so already ordered,
        # the first time it was read above) is not re-sorted on a plain field
        # write to one of its records - force a fresh, correctly ordered read.
        self.product.product_tmpl_id.invalidate_recordset(["seller_ids"])
        self.product.product_tmpl_id.route_ids = [(6, 0, (self.mto | self.buy).ids)]
        order = self.env["sale.order"].create(
            {"partner_id": self.partner.id, "pricelist_id": self.pricelist.id}
        )
        cards = order._get_product_catalog_order_line_info(
            [self.product.id], catalog_origin_supplierinfo=True
        )
        vendor_a_cards = [
            card
            for card in cards[self.product.id]["vendorLines"]
            if card.get("vendorId") == self.vendor_a.id
        ]
        # Two cards for vendor_a alone (one per row) - not collapsed into one.
        self.assertEqual(len(vendor_a_cards), 2)
        self.assertEqual(
            {card["supplierinfoId"] for card in vendor_a_cards},
            {cheap.id, expensive.id},
        )
        expensive_card = next(
            card for card in vendor_a_cards if card["supplierinfoId"] == expensive.id
        )
        self.assertAlmostEqual(expensive_card["price"], 50.0)
        self.assertEqual(expensive_card["vendorComment"], "Comentario caro")
        # ``_update_order_line_info`` calls ``request.update_context()`` (view
        # tracking), only bound during a real HTTP request - irrelevant here.
        self.patch(
            sale_order, "request", SimpleNamespace(update_context=lambda **kw: None)
        )
        order._update_order_line_info(
            self.product.id,
            1,
            vendor_id=self.vendor_a.id,
            supplierinfo_id=cheap.id,
        )
        order._update_order_line_info(
            self.product.id,
            1,
            vendor_id=self.vendor_a.id,
            supplierinfo_id=expensive.id,
        )
        cheap_line = order.order_line.filtered(lambda sol: sol.supplierinfo_id == cheap)
        expensive_line = order.order_line.filtered(
            lambda sol: sol.supplierinfo_id == expensive
        )
        # Two distinct lines, not one line stolen/overwritten by the other.
        self.assertEqual(len(order.order_line), 2)
        self.assertAlmostEqual(cheap_line.price_unit, 10.0)
        self.assertAlmostEqual(expensive_line.price_unit, 50.0)
        self.assertEqual(expensive_line.vendor_comment, "Comentario caro")
        # Confirming must send each line's purchase to the vendor priced from
        # its own exact row, not the vendor's cheapest one by default.
        order.action_confirm()
        purchase_orders = order._get_purchase_orders()
        po_lines = purchase_orders.order_line
        self.assertEqual(len(po_lines), 2)
        self.assertEqual(sorted(po_lines.mapped("price_unit")), [10.0, 50.0])

    def test_catalog_add_pins_the_exact_supplierinfo_shown_on_the_card(self):
        """Going through the actual catalog RPC (``_update_order_line_info``,
        what a click on a vendor card triggers) must pin the exact row the
        card showed, not just the vendor - otherwise a vendor with more than
        one concurrently valid row could get billed at a different one than
        what the card actually displayed once the order is confirmed."""
        cheap = self.product.seller_ids.filtered(
            lambda s: s.partner_id == self.vendor_a
        )
        cheap.sequence = 1
        preferred = self.env["product.supplierinfo"].create(
            {
                "partner_id": self.vendor_a.id,
                "product_tmpl_id": self.product.product_tmpl_id.id,
                "price": 50.0,
                "sequence": 0,
            }
        )
        # The cached ``seller_ids`` value (fetched, and so already ordered,
        # the first time it was read above) is not re-sorted on a plain field
        # write to one of its records - force a fresh, correctly ordered read.
        self.product.product_tmpl_id.invalidate_recordset(["seller_ids"])
        order = self.env["sale.order"].create(
            {"partner_id": self.partner.id, "pricelist_id": self.pricelist.id}
        )
        cards = order._get_product_catalog_order_line_info(
            [self.product.id], catalog_origin_supplierinfo=True
        )
        preferred_card = next(
            card
            for card in cards[self.product.id]["vendorLines"]
            if card.get("vendorId") == self.vendor_a.id
            and card.get("supplierinfoId") == preferred.id
        )
        self.assertAlmostEqual(preferred_card["price"], 50.0)
        # ``_update_order_line_info`` calls ``request.update_context()`` (view
        # tracking), only bound during a real HTTP request - irrelevant here.
        self.patch(
            sale_order, "request", SimpleNamespace(update_context=lambda **kw: None)
        )
        order._update_order_line_info(
            self.product.id,
            1,
            vendor_id=self.vendor_a.id,
            supplierinfo_id=preferred.id,
        )
        line = order.order_line.filtered(lambda sol: sol.supplierinfo_id == preferred)
        self.assertEqual(line.vendor_id, self.vendor_a)
        self.assertAlmostEqual(line.price_unit, 50.0)

    def test_catalog_add_associates_price_and_comment_per_vendor(self):
        """Two vendors, same product, each with its own comment
        (product_supplierinfo_comment) and price: adding the product from
        each vendor's card must associate the right supplierinfo/price/
        comment with the right line - no cross-contamination between the two
        cards of the same product."""
        # The catalog RPC does not set a line-level route_id override (unlike
        # the manually built line in the pinning test above): put the MTO/buy
        # routes on the product itself so procurement still triggers.
        self.product.product_tmpl_id.route_ids = [(6, 0, (self.mto | self.buy).ids)]
        seller_a = self.product.seller_ids.filtered(
            lambda s: s.partner_id == self.vendor_a
        )
        seller_a.comment = "Comentario del proveedor A"
        seller_b = self.product.seller_ids.filtered(
            lambda s: s.partner_id == self.vendor_b
        )
        seller_b.comment = "Comentario del proveedor B"
        order = self.env["sale.order"].create(
            {"partner_id": self.partner.id, "pricelist_id": self.pricelist.id}
        )
        cards = order._get_product_catalog_order_line_info(
            [self.product.id], catalog_origin_supplierinfo=True
        )
        cards_by_vendor = {
            card["vendorId"]: card for card in cards[self.product.id]["vendorLines"]
        }
        self.assertEqual(
            cards_by_vendor[self.vendor_a.id]["vendorComment"],
            "Comentario del proveedor A",
        )
        self.assertEqual(
            cards_by_vendor[self.vendor_b.id]["vendorComment"],
            "Comentario del proveedor B",
        )
        self.patch(
            sale_order, "request", SimpleNamespace(update_context=lambda **kw: None)
        )
        order._update_order_line_info(self.product.id, 4, vendor_id=self.vendor_a.id)
        order._update_order_line_info(self.product.id, 6, vendor_id=self.vendor_b.id)
        line_a = order.order_line.filtered(lambda sol: sol.vendor_id == self.vendor_a)
        line_b = order.order_line.filtered(lambda sol: sol.vendor_id == self.vendor_b)
        self.assertEqual(line_a.supplierinfo_id, seller_a)
        self.assertEqual(line_b.supplierinfo_id, seller_b)
        self.assertEqual(line_a.vendor_comment, "Comentario del proveedor A")
        self.assertEqual(line_b.vendor_comment, "Comentario del proveedor B")
        self.assertAlmostEqual(line_a.price_unit, 10.0)
        self.assertAlmostEqual(line_b.price_unit, 20.0)
        # Confirming must not create/duplicate any supplierinfo and must keep
        # each purchase order priced from its own vendor's row.
        baseline_sellers = sorted((seller_a | seller_b).ids)
        order.action_confirm()
        self.assertEqual(sorted(self.product.seller_ids.ids), baseline_sellers)
        purchase_orders = order._get_purchase_orders()
        self.assertEqual(len(purchase_orders), 2)
        po_a = purchase_orders.filtered(lambda po: po.partner_id == self.vendor_a)
        po_b = purchase_orders.filtered(lambda po: po.partner_id == self.vendor_b)
        self.assertAlmostEqual(po_a.order_line.price_unit, 10.0)
        self.assertAlmostEqual(po_b.order_line.price_unit, 20.0)

    def test_catalog_card_uses_this_variant_row_not_a_sibling_variants(self):
        """A vendor can have a different product.supplierinfo row per
        variant of the same template (real, confirmed data: the same
        vendor, one row per variant, each at a different price). The card
        - and the supplierinfo_id it pins - for one variant must use THAT
        variant's own row, never a cheaper sibling variant's: real report
        was that, after adding two lines from the catalog with different
        vendors, reopening the catalog showed the product not correctly
        linked to its own lines, traced to product.seller_ids listing
        every row of the whole template (sibling variants included) and
        the card picking whichever sorted first across all of them."""
        attribute = self.env["product.attribute"].create({"name": "Size"})
        value_small, value_large = self.env["product.attribute.value"].create(
            [
                {"name": "Small", "attribute_id": attribute.id},
                {"name": "Large", "attribute_id": attribute.id},
            ]
        )
        template = self.env["product.template"].create(
            {
                "name": "Test multi-variant product",
                "attribute_line_ids": [
                    Command.create(
                        {
                            "attribute_id": attribute.id,
                            "value_ids": [
                                Command.set([value_small.id, value_large.id])
                            ],
                        }
                    )
                ],
            }
        )
        variant_small = template.product_variant_ids.filtered(
            lambda p: value_small
            in p.product_template_attribute_value_ids.product_attribute_value_id
        )
        variant_large = template.product_variant_ids.filtered(
            lambda p: value_large
            in p.product_template_attribute_value_ids.product_attribute_value_id
        )
        # vendor_a: two rows, one per variant - the small one is the
        # cheaper of the two, so a naive price-only sort across the whole
        # template would pick it even for the large variant's own card.
        self.env["product.supplierinfo"].create(
            [
                {
                    "partner_id": self.vendor_a.id,
                    "product_tmpl_id": template.id,
                    "product_id": variant_small.id,
                    "price": 5.0,
                },
                {
                    "partner_id": self.vendor_a.id,
                    "product_tmpl_id": template.id,
                    "product_id": variant_large.id,
                    "price": 50.0,
                },
            ]
        )
        large_seller = variant_large.seller_ids.filtered(
            lambda s: s.product_id == variant_large
        )
        order = self.env["sale.order"].create(
            {"partner_id": self.partner.id, "pricelist_id": self.pricelist.id}
        )
        cards = order._get_product_catalog_order_line_info(
            [variant_large.id], catalog_origin_supplierinfo=True
        )
        card = next(
            c
            for c in cards[variant_large.id]["vendorLines"]
            if c.get("vendorId") == self.vendor_a.id
        )
        self.assertEqual(card["supplierinfoId"], large_seller.id)
        self.patch(
            sale_order, "request", SimpleNamespace(update_context=lambda **kw: None)
        )
        order._update_order_line_info(variant_large.id, 1, vendor_id=self.vendor_a.id)
        line = order.order_line.filtered(lambda sol: sol.vendor_id == self.vendor_a)
        self.assertEqual(line.supplierinfo_id, large_seller)
        self.assertAlmostEqual(line.price_unit, 50.0)

    def test_catalog_add_on_empty_card_does_not_take_unpinned_lines(self):
        """Lines without a pinned supplierinfo are shown on the first card of
        their vendor, so adding from another card of the same vendor creates
        its own line instead of updating them."""
        second_seller = self.env["product.supplierinfo"].create(
            {
                "partner_id": self.vendor_a.id,
                "product_tmpl_id": self.product.product_tmpl_id.id,
                "price": 50.0,
                "sequence": 99,
            }
        )
        order = self.env["sale.order"].create(
            {"partner_id": self.partner.id, "pricelist_id": self.pricelist.id}
        )
        unpinned = self.env["sale.order.line"].create(
            [
                {
                    "order_id": order.id,
                    "product_id": self.product.id,
                    "vendor_id": self.vendor_a.id,
                    "product_uom_qty": qty,
                }
                for qty in (3, 4)
            ]
        )
        unpinned.supplierinfo_id = False
        cards = order._get_product_catalog_order_line_info(
            [self.product.id], catalog_origin_supplierinfo=True
        )[self.product.id]["vendorLines"]
        second_card = next(
            card for card in cards if card.get("supplierinfoId") == second_seller.id
        )
        self.assertNotIn("lineId", second_card)
        self.patch(
            sale_order, "request", SimpleNamespace(update_context=lambda **kw: None)
        )
        order._update_order_line_info(
            self.product.id,
            1,
            vendor_id=self.vendor_a.id,
            supplierinfo_id=second_seller.id,
        )
        self.assertEqual(unpinned.mapped("product_uom_qty"), [3.0, 4.0])
        new_line = order.order_line - unpinned
        self.assertEqual(new_line.supplierinfo_id, second_seller)
        self.assertEqual(new_line.product_uom_qty, 1.0)

    def test_purchase_line_merge_keeps_the_pinned_price(self):
        """A later sale of the same pinned supplierinfo is merged into its
        purchase line keeping that row price, not the cheapest one of the
        vendor. Both sales carry the row comment, as when added from the
        catalog, so they are merged whether or not the purchase lines are split
        by vendor comment."""
        expensive = self.env["product.supplierinfo"].create(
            {
                "partner_id": self.vendor_a.id,
                "product_tmpl_id": self.product.product_tmpl_id.id,
                "price": 50.0,
                "comment": "Expensive row",
            }
        )

        def confirm_sale():
            order = self.env["sale.order"].create(
                {
                    "partner_id": self.partner.id,
                    "pricelist_id": self.pricelist.id,
                    "order_line": [
                        Command.create(
                            {
                                "product_id": self.product.id,
                                "product_uom_qty": 1,
                                "route_id": self.mto.id,
                                "vendor_id": self.vendor_a.id,
                                "supplierinfo_id": expensive.id,
                                "vendor_comment": expensive.comment,
                            }
                        )
                    ],
                }
            )
            order.action_confirm()
            return order._get_purchase_orders()

        purchase = confirm_sale() | confirm_sale()
        self.assertEqual(len(purchase), 1)
        self.assertEqual(purchase.order_line.product_qty, 2)
        self.assertAlmostEqual(purchase.order_line.price_unit, 50.0)

    def test_catalog_last_price_per_vendor_card(self):
        """With the Last sale price mode, each vendor card shows the last price
        of its supplierinfo, or else of its vendor, and adding it uses that
        price."""
        cheap = self.product.seller_ids.filtered(
            lambda s: s.partner_id == self.vendor_a
        )
        expensive = self.env["product.supplierinfo"].create(
            {
                "partner_id": self.vendor_a.id,
                "product_tmpl_id": self.product.product_tmpl_id.id,
                "price": 50.0,
            }
        )
        history = self.env["sale.order"].create({"partner_id": self.partner.id})
        self.env["sale.order.line"].create(
            [
                {
                    "order_id": history.id,
                    "product_id": self.product.id,
                    "product_uom_qty": 1,
                    "qty_delivered": 1,
                    "vendor_id": self.vendor_a.id,
                    "supplierinfo_id": cheap.id,
                    "price_unit": 7.5,
                },
                {
                    "order_id": history.id,
                    "product_id": self.product.id,
                    "product_uom_qty": 1,
                    "qty_delivered": 1,
                    "vendor_id": self.vendor_b.id,
                    "price_unit": 15.0,
                },
            ]
        )
        order = self.env["sale.order"].create(
            {"partner_id": self.partner.id, "pricelist_id": self.pricelist.id}
        )
        cards = order._get_product_catalog_order_line_info(
            [self.product.id],
            catalog_origin_supplierinfo=True,
            catalog_show_last_price=True,
        )[self.product.id]["vendorLines"]
        last_prices = {card["supplierinfoId"]: card.get("lastPrice") for card in cards}
        vendor_b_seller = self.product.seller_ids.filtered(
            lambda s: s.partner_id == self.vendor_b
        )
        self.assertEqual(
            last_prices,
            {cheap.id: 7.5, expensive.id: 7.5, vendor_b_seller.id: 15.0},
        )
        self.assertTrue(all(card["catalogShowLastPrice"] for card in cards))
        self.patch(
            sale_order, "request", SimpleNamespace(update_context=lambda **kw: None)
        )
        order._update_order_line_info(
            self.product.id,
            1,
            vendor_id=self.vendor_b.id,
            supplierinfo_id=vendor_b_seller.id,
            catalog_show_last_price=True,
        )
        self.assertAlmostEqual(order.order_line.price_unit, 15.0)

    def test_supplierinfo_origin_with_last_sales(self):
        """The Suppliers origin combined with the Last sales option only shows
        the products with vendors sold to the customer, most sold first."""
        often_sold = self.env["product.product"].create(
            {
                "name": "Often sold product",
                "seller_ids": [
                    Command.create({"partner_id": self.vendor_a.id, "price": 5.0})
                ],
            }
        )
        without_vendor = self.env["product.product"].create(
            {"name": "Product without vendor"}
        )
        self.env["product.product"].create(
            {
                "name": "Never sold product",
                "seller_ids": [
                    Command.create({"partner_id": self.vendor_a.id, "price": 5.0})
                ],
            }
        )
        history = self.env["sale.order"].create({"partner_id": self.partner.id})
        self.env["sale.order.line"].create(
            [
                {
                    "order_id": history.id,
                    "product_id": product.id,
                    "product_uom_qty": 1,
                    "qty_delivered": 1,
                }
                for product in (often_sold, often_sold, self.product, without_vendor)
            ]
        )
        order = self.env["sale.order"].create({"partner_id": self.partner.id})
        product_ids = (
            self.env["product.product"]
            .with_context(**order._get_catalog_history_context())
            ._get_catalog_origin_product_ids(
                [
                    ("catalog_origin_data", "=", "supplierinfo"),
                    ("catalog_last_sales", "=", "last_sales"),
                ]
            )
        )
        self.assertEqual(product_ids, [often_sold.id, self.product.id])

    def test_supplierinfo_origin_in_settings(self):
        """The Suppliers origin can be set as the default one in the settings."""
        field = self.env["res.config.settings"]._fields["default_catalog_origin_data"]
        self.assertIn(
            "supplierinfo", dict(field._description_selection(self.env)).keys()
        )

    def test_catalog_vendor_name_shown_from_settings(self):
        """The vendor cards show 'On order' unless the vendor is enabled in the
        settings."""
        order = self.env["sale.order"].create(
            {"partner_id": self.partner.id, "pricelist_id": self.pricelist.id}
        )

        def card_names():
            cards = order._get_product_catalog_order_line_info(
                [self.product.id], catalog_origin_supplierinfo=True
            )[self.product.id]["vendorLines"]
            return {card["vendorName"] for card in cards}

        self.assertEqual(card_names(), {"On order"})
        self.env["res.config.settings"].create({"catalog_show_vendor": True}).execute()
        self.assertEqual(card_names(), {"Vendor A", "Vendor B"})
