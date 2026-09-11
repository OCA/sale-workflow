# Copyright 2026 Lorenzo Carta - Innovyou
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    discount_distribution = fields.Json(
        compute="_compute_discount_distribution",
        store=True,
        readonly=False,
        precompute=True,
        copy=True,
        help="Ordered list of percentage discounts applied multiplicatively "
        "to the line. Edit through the Discount Distribution widget.",
    )

    discount = fields.Float(
        compute="_compute_aggregated_discount",
        store=True,
        readonly=True,
        digits="Discount",
        help="Aggregated discount percentage derived multiplicatively from "
        "discount_distribution. Read-only: edit discount_distribution "
        "instead.",
    )

    @api.depends("discount_distribution")
    def _compute_aggregated_discount(self):
        """Aggregate ``discount_distribution`` multiplicatively into ``discount``.

        Delegates the formula to ``account.move.line``'s static helper so the
        aggregation logic stays in a single place.
        """
        AccountMoveLine = self.env["account.move.line"]
        for line in self:
            line.discount = AccountMoveLine._aggregate_discount_distribution(
                line.discount_distribution
            )

    @api.depends("product_id", "product_uom", "product_uom_qty")
    def _compute_discount_distribution(self):
        """Seed the distribution from the pricelist when the product changes.

        Mirrors Odoo's standard ``_compute_discount`` (sale/sale_order_line.py)
        but writes into ``discount_distribution`` instead of ``discount``,
        since the latter is now a read-only aggregate. Without this the
        standard compute is no longer wired to ``discount`` and the pricelist
        discount never reaches the line on product insertion.
        """
        discount_enabled = self.env[
            "product.pricelist.item"
        ]._is_discount_feature_enabled()
        for line in self:
            if not line.product_id or line.display_type:
                line.discount_distribution = []
                continue

            if not (line.order_id.pricelist_id and discount_enabled):
                continue

            if line.combo_item_id:
                linked = line._get_linked_line()
                line.discount_distribution = linked.discount_distribution or []
                continue

            line.discount_distribution = line._get_pricelist_discount_distribution()

    def _get_pricelist_discount_distribution(self):
        """Return the discount distribution implied by the current pricelist rule.

        Hook intended for downstream modules to inject richer logic — e.g.
        ``sale_pricelist_multi_discount`` copies the rule's own
        ``discount_distribution`` field verbatim. The default implementation
        derives a single percentage from the standard pricelist math.

        :return: list of percentage values, or ``[]`` when the rule yields no
            discount.
        """
        self.ensure_one()
        if not self.pricelist_item_id._show_discount():
            return []

        line_co = self.with_company(self.company_id)
        pricelist_price = line_co._get_pricelist_price()
        base_price = line_co._get_pricelist_price_before_discount()

        if base_price == 0:  # avoid division by zero
            return []

        discount = (base_price - pricelist_price) / base_price * 100
        # Only positive discounts on positive prices (and vice versa);
        # negative-on-positive would be a surcharge.
        if (discount > 0 and base_price > 0) or (discount < 0 and base_price < 0):
            return [discount]
        return []

    @api.depends("discount_distribution")
    def _compute_amount(self):
        # Re-declare the depends so the tax engine refreshes when the
        # distribution is edited even if the aggregated discount happens to
        # land on the same float value (rare but possible for ``[0]`` vs
        # ``[]``).
        return super()._compute_amount()

    def _compute_discount(self):
        """Redirect the core compute to the distribution.

        ``sale.order._recompute_prices`` (invoked by *Update Prices*) calls
        ``_compute_discount`` directly to overwrite the legacy ``discount``
        field on each line. Since ``discount`` is now a read-only aggregate
        of ``discount_distribution``, run the distribution recompute
        instead — otherwise the pricelist would feed a single percentage
        back through our ``write`` override and squash a freshly-edited
        multi-discount rule into a single flattened value.
        """
        self._compute_discount_distribution()

    def _prepare_invoice_line(self, **optional_values):
        """Propagate the distribution to the generated invoice line."""
        res = super()._prepare_invoice_line(**optional_values)
        if self.discount_distribution:
            res["discount_distribution"] = self.discount_distribution
        return res

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if "discount" in vals and "discount_distribution" not in vals:
                discount_val = vals.pop("discount")
                vals["discount_distribution"] = [discount_val] if discount_val else []
        return super().create(vals_list)

    def write(self, vals):
        if "discount" in vals and "discount_distribution" not in vals:
            discount_val = vals.pop("discount")
            vals["discount_distribution"] = [discount_val] if discount_val else []
        return super().write(vals)
