# Copyright 2026 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)
#
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    use_price_compliance_threshold = fields.Boolean(
        related="company_id.use_price_compliance_threshold",
        readonly=False,
    )
    price_compliance_threshold_t1 = fields.Float(
        related="company_id.price_compliance_threshold_t1",
        readonly=False,
        help="Threshold for Tier 1 Price Compliance (e.g., High-yield). "
        "Prices below this tier are considered fully compliant.",
    )
    price_compliance_threshold_t2 = fields.Float(
        related="company_id.price_compliance_threshold_t2",
        readonly=False,
        help="Threshold for Tier 2 Price Compliance (e.g., Medium-yield). "
        "Prices between Tier 1 and Tier 2 are considered moderately compliant.",
    )
    price_compliance_threshold_t3 = fields.Float(
        related="company_id.price_compliance_threshold_t3",
        readonly=False,
        help="Threshold for Tier 3 Price Compliance (e.g., Low-yield). "
        "Prices between Tier 2 and Tier 3 are considered low compliant.",
    )
