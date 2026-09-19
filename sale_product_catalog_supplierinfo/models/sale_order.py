# Copyright 2026 Tecnativa - Carlos Roca
# Copyright 2026 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from collections import defaultdict

from odoo import models
from odoo.http import request


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _get_product_catalog_order_line_info(
        self, product_ids, catalog_origin_supplierinfo=False, **kwargs
    ):
        """When the ``supplierinfo`` origin is active, split every product card
        into one card per ``product.supplierinfo`` row so the catalog shows
        the vendor information and adding it transfers the exact vendor/row
        pair to the created sale order line.
        """
        result = super()._get_product_catalog_order_line_info(product_ids, **kwargs)
        if not catalog_origin_supplierinfo:
            return result
        products = self.env["product.product"].browse(list(result.keys()))
        products_by_id = {product.id: product for product in products}
        for product_id, data in result.items():
            vendor_lines = self._get_catalog_supplier_lines(
                products_by_id[product_id], **kwargs
            )
            if not vendor_lines:
                continue
            # Replace the per-order-line split coming from
            # ``sale_product_catalog_extended`` with the per-vendor split.
            data.pop("lines", None)
            data["vendorLines"] = vendor_lines
        return result

    def _get_catalog_supplier_lines(self, product, **kwargs):
        """Build the list of vendor cards for ``product``: one entry per
        ``product.supplierinfo`` row found in the product suppliers - not one
        per vendor, since the same vendor can concurrently have more than one
        valid row (different price, min_qty or comment) and each must stay
        individually selectable rather than being silently collapsed into a
        single card (real report: a product with two vendor prices only ever
        showed one of them). Cards are matched against the existing order
        lines of that product through their pinned ``supplierinfo_id``; a
        line predating that pin (created before this module, or by hand) is
        matched to its vendor's first remaining card instead, so it is never
        silently hidden. When a vendor/supplierinfo has more than one order
        line, one card per line is produced so they are all reflected.
        """
        self.ensure_one()
        lines_by_supplierinfo = defaultdict(lambda: self.env["sale.order.line"])
        lines_by_vendor = defaultdict(lambda: self.env["sale.order.line"])
        for line in self.order_line:
            if line.display_type or line.product_id != product:
                continue
            if line.supplierinfo_id:
                lines_by_supplierinfo[line.supplierinfo_id.id] |= line
            else:
                lines_by_vendor[line.vendor_id.id] |= line
        vendor_lines = []
        # ``product.seller_ids`` (delegated from the template) lists every
        # supplierinfo of the WHOLE template, including sibling variants'
        # own rows - a vendor with a different row per variant would
        # otherwise get whichever row sorts first across ALL of them, not
        # the one that actually applies to this variant. ``_prepare_sellers()``
        # is core's own filtered-to-this-variant-or-template-wide list.
        for seller in product._prepare_sellers():
            partner = seller.partner_id
            if not partner:
                continue
            lines = lines_by_supplierinfo.pop(seller.id, self.env["sale.order.line"])
            if not lines:
                # Claim a not-yet-pinned line of the same vendor for its
                # first (preferred) remaining card only, so it still shows up.
                lines = lines_by_vendor.pop(partner.id, self.env["sale.order.line"])
            vendor_lines.extend(
                self._prepare_catalog_supplier_vendor_cards(
                    product, partner, seller, lines, **kwargs
                )
            )
        # Keep showing order lines whose vendor/supplierinfo is not (or no
        # longer) one of the product suppliers so they are not silently
        # hidden from the catalog.
        for lines in lines_by_supplierinfo.values():
            seller = lines[:1].supplierinfo_id
            vendor_lines.extend(
                self._prepare_catalog_supplier_vendor_cards(
                    product, seller.partner_id, seller, lines, **kwargs
                )
            )
        for lines in lines_by_vendor.values():
            partner = lines[:1].vendor_id
            vendor_lines.extend(
                self._prepare_catalog_supplier_vendor_cards(
                    product,
                    partner,
                    self.env["product.supplierinfo"],
                    lines,
                    **kwargs,
                )
            )
        return vendor_lines

    def _prepare_catalog_supplier_vendor_cards(
        self, product, partner, seller, lines, **kwargs
    ):
        """Return the card(s) for a ``(product, vendor)`` pair: a single empty
        card when there is no order line yet, or one card per existing line so
        several lines of the same vendor are all shown.
        """
        if not lines:
            return [
                self._prepare_catalog_supplier_line_data(
                    product, partner, seller, self.env["sale.order.line"], **kwargs
                )
            ]
        return [
            self._prepare_catalog_supplier_line_data(
                product, partner, seller, line, **kwargs
            )
            for line in lines
        ]

    def _prepare_catalog_supplier_line_data(
        self, product, partner, seller, line, **kwargs
    ):
        """Return the catalog card data for a given ``(product, vendor)`` pair."""
        data = {
            **line._get_product_catalog_lines_data(**kwargs),
            "productType": product.type,
        }
        data.setdefault("readOnly", self._is_readonly())
        if not line:
            # No order line yet for this vendor: show the sale price so the card
            # does not appear with an empty/zero price before being added. The
            # vendor is forwarded through the context so ``supplierinfo`` based
            # pricelist rules (product_pricelist_supplierinfo) price this card
            # for its own vendor.
            data["price"] = self.pricelist_id._get_product_price(
                product=self._catalog_supplier_price_product(product, partner, seller),
                quantity=1.0,
                currency=self.currency_id,
                date=self.date_order,
            )
        if partner:
            data["vendorId"] = partner.id
            data["vendorName"] = partner.display_name
        if seller:
            data["supplierinfoId"] = seller.id
        # Comment shown on the card: the line's own (possibly edited)
        # vendor_comment when the line already exists, otherwise the supplier
        # info comment that would be copied when adding the product.
        comment = (
            line.vendor_comment if line else self._catalog_supplier_comment(seller)
        )
        if comment:
            data["vendorComment"] = comment
        if line:
            data["lineId"] = line.id
        return data

    def _catalog_supplier_price_product(self, product, partner, seller=False):
        """Return the product (with context) used to price a vendor card.

        The ``force_filter_supplier_id`` context key is read by
        ``product_pricelist_supplierinfo`` to compute ``supplierinfo`` based
        pricelist rules for the given vendor. It is a soft integration: the key
        is ignored when that module is not installed.

        ``force_supplierinfo_item_id`` (this module's own ``_select_seller()``
        short-circuit) additionally pins the exact row, so two cards of the
        *same* vendor with different concurrently valid rows each price for
        their own row instead of both resolving to whichever one
        ``_select_seller()`` would pick for the vendor alone (its cheapest, by
        default) - the same collapsing this card split exists to avoid.
        """
        if not partner:
            return product
        # ``product_pricelist_supplierinfo`` expects a partner record here (its
        # default is ``rule.filter_supplier_id``), not an id.
        product = product.with_context(force_filter_supplier_id=partner)
        if seller:
            product = product.with_context(force_supplierinfo_item_id=seller.id)
        return product

    def _catalog_supplier_comment(self, seller):
        """Return the vendor comment (product_supplierinfo_comment) for a
        supplier info card.
        """
        return seller.comment if seller else False

    def _catalog_supplier_seller(self, product, vendor_id):
        """Fallback used only when a caller does not know the exact
        supplierinfo shown (e.g. an older client bundle sending just
        ``vendor_id``): the first, of this variant's own (or template-wide)
        rows - see ``_get_catalog_supplier_lines()`` - that belongs to the
        given vendor. Deliberately not ``product.seller_ids`` (the whole
        template's rows, sibling variants included): a vendor with a
        different row per variant would otherwise resolve to whichever one
        sorts first across ALL of them instead of the one for this variant.

        The real per-card flow (``_update_order_line_info`` below) instead
        receives ``supplierinfo_id`` straight from the card that was clicked,
        since a vendor can now have several cards and ``vendor_id`` alone
        cannot tell them apart.
        """
        return product._prepare_sellers().filtered(
            lambda seller: seller.partner_id.id == vendor_id
        )[:1]

    def _catalog_quantity_vals(self, product, quantity):
        """Size ``quantity`` (as typed on a vendor card) into the line vals
        it must end up as.

        ``sale_order_secondary_unit`` treats the catalog quantity as
        expressed in the product's own secondary sale unit
        (``product.sale_secondary_uom_id``) whenever one is configured,
        converting it into ``product_uom_qty`` itself rather than letting it
        through as-is - it does this from its own ``_update_order_line_info``
        override, which the vendor-card path above never reaches (it creates
        the line directly, and updates an existing one with a plain write,
        so no other module's ``_update_order_line_info`` ever runs for a
        vendor card). Without mirroring that conversion here, a product with
        a secondary unit configured would silently get the typed quantity
        written to ``product_uom_qty`` unconverted, and ``secondary_uom_qty``
        would stay unset/stale - showing 0 (or a wrong quantity) when the
        catalog is reopened, even though the line itself has real stock/
        procurement quantities. Soft dependency: a no-op when
        ``sale_order_secondary_unit`` isn't installed or the product has no
        secondary unit of its own.
        """
        secondary_uom = (
            "sale_secondary_uom_id" in product._fields and product.sale_secondary_uom_id
        )
        if not secondary_uom:
            return {"product_uom_qty": quantity}
        vals = {"secondary_uom_id": secondary_uom.id, "secondary_uom_qty": quantity}
        if secondary_uom.dependency_type != "independent":
            qty_base = quantity * secondary_uom.factor
            vals["product_uom_qty"] = product.uom_id._compute_quantity(
                qty_base, product.uom_id
            )
        return vals

    def _get_catalog_order_line_filter_domain(
        self, product_id, vendor_id=None, supplierinfo_id=None, **kwargs
    ):
        domain = super()._get_catalog_order_line_filter_domain(product_id, **kwargs)
        if supplierinfo_id:
            domain += [("supplierinfo_id", "=", supplierinfo_id)]
        elif vendor_id:
            domain += [("vendor_id", "=", vendor_id)]
        return domain

    def _get_catalog_supplier_order_line(self, product_id, vendor_id, supplierinfo_id):
        """Find the order line a vendor card's ``+``/qty update targets.

        A vendor can now have several concurrently valid cards (one per
        ``product.supplierinfo`` row - see ``_get_catalog_supplier_lines()``),
        so ``vendor_id`` alone cannot tell which card's line is meant: two
        cards of the same vendor must never collapse onto, or steal, each
        other's line. ``supplierinfo_id`` (sent by the client for the exact
        card that was clicked) disambiguates them; a line predating the pin
        (no ``supplierinfo_id`` of its own - created before this module, or by
        hand) is still claimed as a fallback, matching the same "first
        remaining card wins it" rule ``_get_catalog_supplier_lines()`` uses to
        display it.
        """
        lines = self.order_line.filtered(
            lambda line: line.product_id.id == product_id
            and line.vendor_id.id == vendor_id
        )
        if not supplierinfo_id:
            return lines
        pinned = lines.filtered(lambda line: line.supplierinfo_id.id == supplierinfo_id)
        if pinned:
            return pinned
        return lines.filtered(lambda line: not line.supplierinfo_id)

    def _update_order_line_info(
        self, product_id, quantity, vendor_id=None, supplierinfo_id=None, **kwargs
    ):
        """Vendor aware variant of the catalog update: lines are matched (and
        created) per ``(product, supplierinfo)`` pair - not just vendor, since
        the same vendor can have several cards - so each vendor card manages
        its own order line and the exact supplierinfo it was created from is
        stored on it.
        """
        if not vendor_id:
            return super()._update_order_line_info(product_id, quantity, **kwargs)
        request.update_context(catalog_skip_tracking=True)
        sol = self._get_catalog_supplier_order_line(
            product_id, vendor_id, supplierinfo_id
        )
        if sol:
            if quantity != 0:
                sol.write(self._catalog_quantity_vals(sol.product_id, quantity))
            elif self.state in ["draft", "sent"]:
                price_unit = self.pricelist_id._get_product_price(
                    product=self._catalog_supplier_price_product(
                        sol.product_id, sol.vendor_id, sol.supplierinfo_id
                    ),
                    quantity=1.0,
                    currency=self.currency_id,
                    date=self.date_order,
                )
                sol.unlink()
                return price_unit
            else:
                sol.product_uom_qty = 0
        elif quantity > 0:
            product = self.env["product.product"].browse(product_id)
            # Pin the exact supplierinfo the card is showing: a vendor can have
            # more than one concurrently valid row (see
            # ``sale.order.line.supplierinfo_id``'s docstring), and without this
            # the line would only remember the vendor, leaving
            # ``_select_seller()`` free to re-resolve a different row - possibly
            # at a different price than the one the card actually displayed -
            # once the order is confirmed. ``supplierinfo_id`` is trusted as-is
            # when the client sent it (the exact card clicked); only re-derived
            # through the vendor's first row as a fallback for a caller that
            # doesn't know it.
            seller = (
                self.env["product.supplierinfo"].browse(supplierinfo_id)
                if supplierinfo_id
                else self._catalog_supplier_seller(product, vendor_id)
            )
            vals = {
                "order_id": self.id,
                "product_id": product_id,
                "vendor_id": vendor_id,
                "supplierinfo_id": seller.id,
                "sequence": (
                    (self.order_line and self.order_line[-1].sequence + 1) or 10
                ),
                **self._catalog_quantity_vals(product, quantity),
            }
            # Copy the supplier info comment shown on the card to the line
            # (sale_line_vendor_comment).
            comment = self._catalog_supplier_comment(seller)
            if comment:
                vals["vendor_comment"] = comment
            sol = self.env["sale.order.line"].create(vals)
            # Replay the line onchanges that the base catalog ``create`` skips.
            self._play_catalog_line_onchanges(sol)
        else:
            product = self.env["product.product"].browse(product_id)
            partner = self.env["res.partner"].browse(vendor_id)
            seller = (
                self.env["product.supplierinfo"].browse(supplierinfo_id)
                if supplierinfo_id
                else self._catalog_supplier_seller(product, vendor_id)
            )
            return self.pricelist_id._get_product_price(
                product=self._catalog_supplier_price_product(product, partner, seller),
                quantity=1.0,
                currency=self.currency_id,
                date=self.date_order,
            )
        return sol._get_discounted_price()
