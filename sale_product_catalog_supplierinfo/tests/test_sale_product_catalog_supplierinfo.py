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

    def test_catalog_add_pins_the_exact_supplierinfo_shown_on_the_card(self):
        """Going through the actual catalog RPC (``_update_order_line_info``,
        what a click on a vendor card triggers) must pin the exact row the
        card showed, not just the vendor - otherwise a vendor with more than
        one concurrently valid row could get billed at a different one than
        what the card actually displayed once the order is confirmed.

        The two rows are set up so the card (``product.supplierinfo``'s own
        ``_order``: sequence first) and a plain, unpinned ``_select_seller()``
        (price first) would each pick a *different* row - proving this isn't
        a coincidental match."""
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
        vendor_a_card = next(
            card
            for card in cards[self.product.id]["vendorLines"]
            if card.get("vendorId") == self.vendor_a.id
        )
        self.assertEqual(vendor_a_card["supplierinfoId"], preferred.id)
        # ``_update_order_line_info`` calls ``request.update_context()`` (view
        # tracking), only bound during a real HTTP request - irrelevant here.
        self.patch(
            sale_order, "request", SimpleNamespace(update_context=lambda **kw: None)
        )
        order._update_order_line_info(self.product.id, 1, vendor_id=self.vendor_a.id)
        line = order.order_line.filtered(lambda sol: sol.vendor_id == self.vendor_a)
        self.assertEqual(line.supplierinfo_id, preferred)
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
        order = self.env["sale.order"].create({"partner_id": self.partner.id})
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

    def test_catalog_add_honors_the_product_secondary_sale_unit(self):
        """sale_order_secondary_unit treats the catalog's typed quantity as
        expressed in the product's own secondary sale unit, converting it
        into product_uom_qty itself - from its own _update_order_line_info,
        which the vendor-card path never reaches (it creates/updates the
        line directly, calling neither super() nor that module's override).
        Real report: reopening the catalog for a product with a secondary
        sale unit showed quantity 0 for a line that actually had a real,
        non-zero quantity - traced to secondary_uom_qty being left unset
        by the vendor-card path while the catalog card prefers displaying
        it over product_uom_qty whenever a secondary unit is set on the
        line."""
        if "sale_secondary_uom_id" not in self.product._fields:
            self.skipTest("sale_order_secondary_unit is not installed")
        secondary_uom = self.env["product.secondary.unit"].create(
            {
                "product_tmpl_id": self.product.product_tmpl_id.id,
                "name": "Box",
                "factor": 2.0,
                "uom_id": self.product.uom_id.id,
            }
        )
        self.product.sale_secondary_uom_id = secondary_uom
        order = self.env["sale.order"].create({"partner_id": self.partner.id})
        self.patch(
            sale_order, "request", SimpleNamespace(update_context=lambda **kw: None)
        )
        order._update_order_line_info(self.product.id, 4, vendor_id=self.vendor_a.id)
        line = order.order_line.filtered(lambda sol: sol.vendor_id == self.vendor_a)
        self.assertEqual(line.secondary_uom_id, secondary_uom)
        self.assertAlmostEqual(line.secondary_uom_qty, 4.0)
        self.assertAlmostEqual(line.product_uom_qty, 8.0)
        cards = order._get_product_catalog_order_line_info(
            [self.product.id], catalog_origin_supplierinfo=True
        )
        card = next(
            c
            for c in cards[self.product.id]["vendorLines"]
            if c.get("vendorId") == self.vendor_a.id
        )
        self.assertAlmostEqual(card["quantity"], 4.0)
        # Bumping the quantity on the already-created line must go through
        # the same conversion, not just overwrite product_uom_qty directly.
        order._update_order_line_info(self.product.id, 6, vendor_id=self.vendor_a.id)
        self.assertAlmostEqual(line.secondary_uom_qty, 6.0)
        self.assertAlmostEqual(line.product_uom_qty, 12.0)
