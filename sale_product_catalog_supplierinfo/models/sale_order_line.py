# Copyright 2026 Tecnativa - Carlos Roca
# Copyright 2026 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    # The vendor card clicked in the catalog (or picked by hand) can carry
    # more than one valid ``product.supplierinfo`` row for the same partner
    # (e.g. two overlapping date ranges with different prices). ``vendor_id``
    # alone cannot disambiguate that; this pins the exact row that was
    # actually shown/chosen.
    supplierinfo_id = fields.Many2one(comodel_name="product.supplierinfo")

    def _get_product_price_context(self):
        """Make the line vendor available to the pricelist price computation.

        ``product_pricelist_supplierinfo`` reads ``force_filter_supplier_id``
        from the product context to pick the supplier info used by
        ``supplierinfo`` based pricelist rules. Forwarding the line vendor here
        makes those rules compute the tariff price for the line's vendor without
        adding a hard dependency on that module (the key is simply ignored when
        it is not installed).
        """
        context = super()._get_product_price_context()
        if self.vendor_id:
            # A partner record is expected (the module default is
            # ``rule.filter_supplier_id``), not an id.
            context["force_filter_supplier_id"] = self.vendor_id
        if self.supplierinfo_id:
            # Pin the exact row so a vendor with several concurrently valid
            # ones (see ``supplierinfo_id``'s docstring) prices for the one
            # that was actually picked instead of whichever _select_seller()
            # alone would have resolved.
            context["force_supplierinfo_item_id"] = self.supplierinfo_id.id
        return context

    @api.depends(
        "product_id", "product_uom", "product_uom_qty", "vendor_id", "supplierinfo_id"
    )
    def _compute_pricelist_item_id(self):
        """Resolve the pricelist rule against the vendor-annotated product.

        Core's own compute (``sale/models/sale_order_line.py``) calls
        ``pricelist_id._get_product_rule(product_id, ...)`` with the bare
        ``product_id`` - never through ``_get_product_price_context()``. So
        without this override, ``force_filter_supplier_id`` never reaches
        rule *selection* (``_get_applicable_rules`` above) even though
        ``_get_pricelist_price()`` already uses it correctly to compute the
        *value* once a rule is known - the two would silently disagree,
        landing back on the same "always resolves the standard_price rule"
        symptom this whole fix exists for, on this specific compute.
        """
        for line in self:
            if (
                not line.product_id
                or line.display_type
                or not line.order_id.pricelist_id
            ):
                line.pricelist_item_id = False
            else:
                line.pricelist_item_id = line.order_id.pricelist_id._get_product_rule(
                    line.product_id.with_context(**line._get_product_price_context()),
                    quantity=line.product_uom_qty or 1.0,
                    uom=line.product_uom,
                    date=line._get_order_date(),
                )

    @api.depends(
        "product_id", "product_uom", "product_uom_qty", "vendor_id", "supplierinfo_id"
    )
    def _compute_price_unit(self):
        """Extend the base dependencies with ``vendor_id``/``supplierinfo_id``.

        ``_compute_price_unit`` already prices through
        ``_get_product_price_context()`` (extended above), but core only
        depends on ``product_id``/``product_uom``/``product_uom_qty`` - editing
        just the vendor on an existing line (the catalog itself always sets
        ``vendor_id`` together with ``product_id`` at line creation, so this
        matters mainly for a manual edit on the form view) would otherwise
        leave a stale ``price_unit`` around.
        """
        return super()._compute_price_unit()

    @api.depends("vendor_id", "supplierinfo_id")
    def _compute_purchase_price(self):
        """Get purchase_price from supplierinfo_id or vendor_id.

        Extends the base dependencies (``sale_margin``/``sale_stock_margin``)
        so that forcing/changing the vendor on a line also refreshes its
        purchase cost - which is what makes
        ``sale_purchase_price_unit_update``'s own ``_compute_purchase_price``
        hook fire and recompute ``price_unit`` from the new cost.
        """
        processed_lines = self.browse()
        for line in self:
            if not line.supplierinfo_id and not line.vendor_id:
                continue
            if line.state == "sale" and line.move_ids:
                # If a purchase order line already exists for this delivery
                # chain (the MTO/buy flow already ran), its own price is the
                # real cost, more accurate than re-deriving a supplierinfo.
                orig_move_ids = line.move_ids._rollup_move_origs()
                orig_moves = self.env["stock.move"].browse(orig_move_ids)
                purchase_line_id = orig_moves.filtered(
                    lambda sm: sm.state != "cancel" and sm.purchase_line_id
                ).purchase_line_id[-1:]
                if purchase_line_id:
                    if line.purchase_price != purchase_line_id.price_unit:
                        line.purchase_price = purchase_line_id.price_unit
                    processed_lines += line
                    continue
            supplier_info = line.supplierinfo_id or line._get_vendor_supplier_info()
            if supplier_info:
                line.purchase_price = supplier_info.price
                processed_lines += line
        return super(SaleOrderLine, self - processed_lines)._compute_purchase_price()

    def _get_vendor_supplier_info(self):
        self.ensure_one()
        return self.product_id.with_company(self.company_id.id)._select_seller(
            partner_id=self.vendor_id,
            quantity=self.product_uom_qty,
            uom_id=self.product_uom,
        )

    def _prepare_procurement_values(self, group_id=False):
        """Prefer the exact picked ``supplierinfo_id`` over the one
        ``sale_purchase_force_vendor`` re-derives from ``vendor_id`` alone -
        relevant when the vendor has more than one concurrently valid row.
        """
        values = super()._prepare_procurement_values(group_id=group_id)
        if self.supplierinfo_id:
            values["supplierinfo_id"] = self.supplierinfo_id
        return values
