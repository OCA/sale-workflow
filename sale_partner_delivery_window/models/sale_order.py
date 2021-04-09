# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import _, api, models
from odoo.tools.misc import format_datetime


class SaleOrder(models.Model):

    _inherit = "sale.order"

    @api.depends(
        "partner_shipping_id.delivery_time_preference",
        "partner_shipping_id.delivery_time_window_ids",
        "partner_shipping_id.delivery_time_window_ids.time_window_start",
        "partner_shipping_id.delivery_time_window_ids.time_window_end",
        "partner_shipping_id.delivery_time_window_ids.time_window_weekday_ids",
    )
    def _compute_expected_date(self):
        """Add dependencies to consider fixed delivery windows"""
        return super()._compute_expected_date()

    @api.onchange("commitment_date")
    def _onchange_commitment_date(self):
        """Warns if commitment date is not a preferred window for delivery"""
        res = super()._onchange_commitment_date()
        if res and "warning" in res:
            return res
        ps = self.partner_shipping_id
        if self.commitment_date and ps.delivery_time_preference == "time_windows":
            if not ps.is_in_delivery_window(self.commitment_date):
                return {"warning": self._commitment_date_no_delivery_window_match_msg()}

    def _commitment_date_no_delivery_window_match_msg(self):
        ps = self.partner_shipping_id
        windows = ps.get_delivery_windows().get(ps.id)
        return {
            "title": _(
                "Commitment date does not match shipping "
                "partner's Delivery time schedule preference."
            ),
            "message": _(
                "The delivery date is %s, but the shipping "
                "partner is set to prefer deliveries on following "
                "time windows:\n%s"
            )
            % (
                format_datetime(self.env, self.commitment_date),
                "\n".join(["  * %s" % w.display_name for w in windows]),
            ),
        }
