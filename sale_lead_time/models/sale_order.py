# Copyright 2025 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.osv import expression


class SaleOrder(models.Model):
    _inherit = "sale.order"

    delivery_lead_time = fields.Float(
        compute="_compute_delivery_lead_time",
        store=True,
        readonly=False,
        help="Number of days expected for delivery from the warehouse to the delivery address.",
    )

    def _get_partner_address_domain(self):
        self.ensure_one()
        partner = self.partner_shipping_id
        partner_domain = [("partner_id", "=", partner.id)]
        state_domain = [
            ("partner_id", "=", False),
            ("state_id", "=", partner.state_id.id),
        ]
        country_domain = [
            ("partner_id", "=", False),
            ("state_id", "=", False),
            ("country_id", "=", partner.country_id.id),
        ]
        no_address_domain = [
            ("partner_id", "=", False),
            ("state_id", "=", False),
            ("country_id", "=", False),
        ]
        return expression.OR(
            [partner_domain, state_domain, country_domain, no_address_domain]
        )

    def _get_warehouse_domain(self):
        self.ensure_one()
        return [
            "|",
            ("warehouse_id", "=", self.warehouse_id.id),
            ("warehouse_id", "=", False),
        ]

    @api.depends("partner_shipping_id", "warehouse_id")
    def _compute_delivery_lead_time(self):
        for rec in self:
            rec.delivery_lead_time = 0.0
            if not rec.partner_shipping_id:
                continue
            partner_address_domain = rec._get_partner_address_domain()
            warehouse_domain = rec._get_warehouse_domain()
            domain = expression.AND(
                [
                    partner_address_domain,
                    warehouse_domain,
                    [
                        ("company_id", "=", rec.company_id.id),
                        ("model_name", "=", self._name),
                    ],
                ]
            )
            profiles = self.env["lead.time.profile"].search(domain)
            if not profiles:
                continue
            profile_scores = {
                profile: profile._get_score(
                    **{
                        "partner": rec.partner_shipping_id,
                        "warehouse": rec.warehouse_id,
                    }
                )
                for profile in profiles
            }
            # In case of a tie, pick the profile with the lowest lead time.
            best_profile = max(
                profiles,
                key=lambda profile: (profile_scores[profile], -profile.lead_time),
                default=None,
            )
            rec.delivery_lead_time = (
                best_profile.lead_time if profile_scores[best_profile] >= 0.0 else 0.0
            )
