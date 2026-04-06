# Copyright 2026 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

import logging

from odoo import _, api, fields, models
from odoo.tools.safe_eval import safe_eval

_logger = logging.getLogger(__name__)


class PriceComplianceThresholdTierMixin(models.AbstractModel):
    _name = "product.price.compliance.threshold.tier.mixin"
    _description = "Product Price Compliance Threshold Tier Mixin"

    price_compliance_tier = fields.Selection(
        selection="_get_price_compliance_selection_tiers",
        readonly=True,
        help="Indicates the Tier of Price Compliance based on the unit price and "
        "applied discount compared to defined thresholds.",
    )

    @api.model
    def _get_price_compliance_selection_tiers(self):
        """Price compliance selection tiers with icons.

        Override this method to provide custom icons or define any
        other logic (visual impairments for example)
        """
        return self._get_price_compliance_selection_tiers_icon_color()

    @api.model
    def _get_tier_selections(self, param, default_selection):
        """Get tier selections using config parameters"""
        icp_st = self.env["ir.config_parameter"].sudo().get_param(param)
        if not icp_st:
            return default_selection
        try:
            st_dict = safe_eval(icp_st)
        except Exception:
            _logger.warning("Wrong parameter value for %s", param)
            return default_selection
        if st_dict and isinstance(st_dict, dict):
            return [
                ("t1", st_dict.get("t1", default_selection[0][1])),
                ("t2", st_dict.get("t2", default_selection[1][1])),
                ("t3", st_dict.get("t3", default_selection[2][1])),
                (
                    "non_compliant",
                    st_dict.get("non_compliant", default_selection[3][1]),
                ),
                ("pricelist", st_dict.get("pricelist", default_selection[4][1])),
            ]
        return default_selection

    @api.model
    def _get_price_compliance_selection_tiers_icon_color(self):
        """Default Price Compliance tiers with icon colors"""
        return self._get_tier_selections(
            "sale_price_compliance.price_compliance_selection_tiers_icon",
            self._get_price_compliance_selection_tiers_icon_color_default(),
        )

    @api.model
    def _get_price_compliance_selection_tiers_text(self):
        """Price Compliance selection tiers on text"""
        return self._get_tier_selections(
            "sale_price_compliance.price_compliance_selection_tiers_text",
            self._get_price_compliance_selection_tiers_text_default(),
        )

    @api.model
    def _get_price_compliance_selection_tiers_icon_color_default(self):
        """Default Price Compliance tiers with icon colors (default)"""
        return [
            ("t1", "🟩"),
            ("t2", "🟨"),
            ("t3", "🟧"),
            ("non_compliant", "🟥"),
            ("pricelist", "🟦"),
        ]

    @api.model
    def _get_price_compliance_selection_tiers_text_default(self):
        """Price Compliance selection tiers on text (default)"""
        return [
            ("t1", _("Tier 1")),
            ("t2", _("Tier 2")),
            ("t3", _("Tier 3")),
            ("non_compliant", _("Non Compliant")),
            ("pricelist", _("Pricelist")),
        ]
