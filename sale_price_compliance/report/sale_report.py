# Copyright 2026 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from odoo import api, fields, models


class SaleReport(models.Model):
    _inherit = "sale.report"

    @api.model
    def _get_price_compliance_tiers(self):
        return self.env["sale.order.line"]._get_price_compliance_selection_tiers_text()

    price_compliance_tier = fields.Selection(
        selection="_get_price_compliance_tiers",
        help="Indicates the Tier of Price Compliance based on the unit price and "
        "applied discount compared to defined thresholds.",
    )

    def _select_additional_fields(self):
        res = super()._select_additional_fields()
        res["price_compliance_tier"] = "l.price_compliance_tier"
        return res

    def _group_by_sale(self):
        res = super()._group_by_sale()
        res += """,
            l.price_compliance_tier"""
        return res
