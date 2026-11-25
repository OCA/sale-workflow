# Copyright 2026 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

import logging

from odoo import api, fields, models
from odoo.tools import float_compare, float_round

_logger = logging.getLogger(__name__)


class SaleOrderLine(models.Model):
    _name = "sale.order.line"
    _inherit = ["sale.order.line", "product.price.compliance.threshold.tier.mixin"]

    price_compliance_tier = fields.Selection(
        compute="_compute_price_compliance_tier",
        store=True,
    )
    price_compliance_data = fields.Json(
        compute="_compute_price_compliance_tier",
        store=True,
        readonly=True,
        help="Holds additional data related to price compliance calculations.",
    )

    def _get_price_compliance_thresholds(self):
        """Price compliance thresholds for this sale line"""
        self.ensure_one()
        return self.product_id._get_price_compliance_thresholds()

    def _get_price_compliance_data(self, precision_digits):
        """Gets a full dictionary with all calculated information about
        price compliance for this product"""
        self.ensure_one()

        def _precision_rounder(val):
            return round(
                float_round(val, precision_digits=precision_digits),
                # Post round to ensure only display X decimals
                precision_digits,
            )

        # Base price in sale order currency
        base_price = self.product_id.list_price
        if self.product_id.currency_id != self.currency_id:
            base_price = self.product_id.currency_id._convert(
                base_price,
                self.currency_id,
                self.company_id,
                self._get_order_date(),
            )
        thresholds = self._get_price_compliance_thresholds()
        selection_tiers_map = dict(self._get_price_compliance_selection_tiers())
        selection_tiers_text_map = dict(
            self._get_price_compliance_selection_tiers_text()
        )
        common_data_values = {
            "currency_symbol": self.currency_id.symbol,
            "product_base_uom": self.product_id.uom_id.name,
            "precision_digits": precision_digits,
            "extra_description": "",
        }
        # Prepare data per tier
        price_compliance_data = []
        for idx_tier, current_threshold_disc in enumerate(thresholds, 1):
            current_threshold_price = _precision_rounder(
                base_price * (1.0 - current_threshold_disc),
            )
            if idx_tier == 1:
                price_compliance_data.append(
                    {
                        "tier": f"t{idx_tier}",
                        "discount": (0.0, current_threshold_disc),
                        "price": (current_threshold_price, base_price),
                        "display": (
                            selection_tiers_map[f"t{idx_tier}"],
                            selection_tiers_text_map[f"t{idx_tier}"],
                        ),
                        **common_data_values,
                    }
                )
                continue
            # -2 because idx_tier is 1-based
            prev_threshold_disc = thresholds[idx_tier - 2]
            prev_threshold_price = _precision_rounder(
                base_price * (1.0 - prev_threshold_disc),
            )
            price_compliance_data.append(
                {
                    "tier": f"t{idx_tier}",
                    "discount": (prev_threshold_disc, current_threshold_disc),
                    "price": (current_threshold_price, prev_threshold_price),
                    "display": (
                        selection_tiers_map[f"t{idx_tier}"],
                        selection_tiers_text_map[f"t{idx_tier}"],
                    ),
                    **common_data_values,
                }
            )
        if not thresholds:
            # If no thresholds are defined, return empty data
            return price_compliance_data

        # Add non_compliant tier
        last_threshold_disc = thresholds[-1]
        last_threshold_price = _precision_rounder(
            base_price * (1.0 - last_threshold_disc),
        )
        price_compliance_data.append(
            {
                "tier": "non_compliant",
                "discount": (last_threshold_disc, 1.0),
                "price": (0.0, last_threshold_price),
                "display": (
                    selection_tiers_map["non_compliant"],
                    selection_tiers_text_map["non_compliant"],
                ),
                **common_data_values,
            }
        )

        # Add Pricelist pricelist item data if any
        if self.pricelist_item_id:
            pricelist_price = self._get_pricelist_price()
            pricelist_description = self.pricelist_item_id.price
            price_compliance_data.append(
                {
                    "tier": "pricelist",
                    "discount": (0.0, 0.0),
                    "price": (pricelist_price, pricelist_price),
                    "display": (
                        selection_tiers_map["pricelist"],
                        selection_tiers_text_map["pricelist"],
                    ),
                    **common_data_values,
                    **{"extra_description": pricelist_description},
                }
            )
        return price_compliance_data

    @api.depends(
        "price_unit", "product_uom", "product_id", "discount", "pricelist_item_id"
    )
    def _compute_price_compliance_tier(self):
        """Set price compliance tier"""
        self.price_compliance_tier = False
        self.price_compliance_data = None
        precision_digits = self.env["decimal.precision"].precision_get("Product Price")
        for line in self:
            # 1. Line section/note, no product assigned
            if line.display_type or not line.product_id:
                continue
            # 2. Prepare Widget Display
            price_compliance_data = line._get_price_compliance_data(precision_digits)
            line.price_compliance_data = price_compliance_data
            if not price_compliance_data:
                # Nothing to check. No thresholds defined for this product
                continue
            # 3. Get the UoM factor to convert line price to product base UoM
            uom_factor = line.product_uom._compute_quantity(
                qty=1.0,
                to_unit=line.product_id.uom_id,
                round=False,
            )
            # 4. Convert line price_unit to product base UoM and apply discount
            discount_line_unit_price_on_base_uom = float_round(
                (line.price_unit / uom_factor) * (1 - line.discount / 100.0),
                precision_digits=precision_digits,
            )
            # 5. Apply standard compliance logic
            # Check negative prices
            if (
                float_compare(
                    discount_line_unit_price_on_base_uom,
                    0.0,
                    precision_digits=precision_digits,
                )
                < 0
            ):
                line.price_compliance_tier = "non_compliant"
                continue
            # Default to t1 in case price is higher than all thresholds
            compliant_tier = "t1"
            for compliance_data in price_compliance_data:
                min_price, max_price = compliance_data["price"]
                if min_price <= discount_line_unit_price_on_base_uom <= max_price:
                    compliant_tier = compliance_data["tier"]
                    break

            # 6. Only check pricelist price equality if non compliant
            if compliant_tier == "non_compliant" and line.pricelist_item_id:
                # Consider pricelist compliance if the price after discount is
                # betweeen pricelist price and last compliant tier price.
                if (
                    float_compare(
                        discount_line_unit_price_on_base_uom,
                        line._get_pricelist_price(),
                        precision_digits=precision_digits,
                    )
                    >= 0
                ):
                    # If the final price after discount is equal to the
                    # pricelist price, we consider pricelist compliance.
                    compliant_tier = "pricelist"
            line.price_compliance_tier = compliant_tier
