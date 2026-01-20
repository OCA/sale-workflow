# Copyright 2026 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from lxml import etree

from odoo import api, fields, models


class PriceComplianceThresholdConfigMixin(models.AbstractModel):
    _name = "product.price.compliance.threshold.config.mixin"
    _description = "Product Price Compliance Threshold Config Mixin"

    use_price_compliance_threshold = fields.Boolean(
        string="Use Price Compliance Thresholds",
    )
    price_compliance_threshold_t1 = fields.Float(
        string="Tier 1",
        default=0.0,
        digits="Discount",
    )
    price_compliance_threshold_t2 = fields.Float(
        string="Tier 2",
        default=0.0,
        digits="Discount",
    )
    price_compliance_threshold_t3 = fields.Float(
        string="Tier 3",
        default=0.0,
        digits="Discount",
    )

    _sql_constraints = [
        (
            "check_price_compliance_positive",
            """CHECK (
                use_price_compliance_threshold IS NOT TRUE
                OR (
                    price_compliance_threshold_t1 >= 0.0 AND
                    price_compliance_threshold_t2 >= 0.0 AND
                    price_compliance_threshold_t3 >= 0.0
                )
            )""",
            "Price Compliance Thresholds Percentage should be positive.",
        ),
        (
            "check_price_compliance_le_1",
            """CHECK (
                use_price_compliance_threshold IS NOT TRUE
                OR (
                    price_compliance_threshold_t1 <= 1.0 AND
                    price_compliance_threshold_t2 <= 1.0 AND
                    price_compliance_threshold_t3 <= 1.0
                )
            )""",
            "Price Compliance Thresholds Percentage should be lower or equal to 100%.",
        ),
        (
            "check_price_compliance_no_gaps",
            """CHECK (
                use_price_compliance_threshold IS NOT TRUE
                OR (
                    (
                        price_compliance_threshold_t1 > 0.0 OR
                        price_compliance_threshold_t2 = 0.0
                    )
                    AND
                    (
                        price_compliance_threshold_t2 > 0.0 OR
                        price_compliance_threshold_t3 = 0.0
                    )
                )
            )""",
            "Price Compliance Thresholds should not have gaps.",
        ),
    ]

    def _get_price_compliance_thresholds(self):
        """Returns price compliance thresholds"""
        self.ensure_one()
        if not self.use_price_compliance_threshold:
            return []
        # Check thresholds in order and stop at the first missing one
        used_threshold_tiers = []
        for threshold in [
            self.price_compliance_threshold_t1,
            self.price_compliance_threshold_t2,
            self.price_compliance_threshold_t3,
        ]:
            if not threshold:
                break
            used_threshold_tiers.append(threshold)
        return used_threshold_tiers

    @api.model
    def get_view(self, view_id=None, view_type="form", **options):
        """Replaces price_compliance_threshold_t[1,2,3] labels based on tier text
        definitions from sale.order.line, which can be customized via system
        parameters."""
        result = super().get_view(view_id=view_id, view_type=view_type, **options)
        # Check if parameter has been created
        if (
            not self.env["ir.config_parameter"]
            .sudo()
            .get_param(
                "sale_price_compliance.price_compliance_selection_tiers_text",
                default=False,
            )
        ):
            return result
        # Get tier text selection from sale.order.line (only t1, t2, t3)
        tiers_selection = self.env[
            "product.price.compliance.threshold.tier.mixin"
        ]._get_price_compliance_selection_tiers_text()[:3]
        # Update field labels in XML
        doc = etree.XML(result["arch"])
        for tier_key, tier_text in tiers_selection:
            field_name = f"price_compliance_threshold_{tier_key}"
            for node in doc.xpath(f"//field[@name='{field_name}']"):
                node.set("string", tier_text)
            if "fields" in result and field_name in result["fields"]:
                result["fields"][field_name]["string"] = tier_text
        result["arch"] = etree.tostring(doc, encoding="unicode")
        return result
