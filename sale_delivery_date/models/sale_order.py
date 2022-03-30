# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, api, fields, models
from odoo.tools.misc import format_datetime


class SaleOrder(models.Model):
    _inherit = "sale.order"

    display_expected_date_ok = fields.Boolean(
        string="Display Expected Date Ok",
        compute="_compute_display_expected_date_ok",
    )

    @api.depends(
        "partner_shipping_id.delivery_time_preference",
        "partner_shipping_id.delivery_time_window_ids",
        "partner_shipping_id.delivery_time_window_ids.time_window_start",
        "partner_shipping_id.delivery_time_window_ids.time_window_end",
        "partner_shipping_id.delivery_time_window_ids.time_window_weekday_ids",
        "partner_shipping_id.order_delivery_cutoff_preference",
        "partner_shipping_id.cutoff_time",
    )
    def _compute_expected_date(self):
        """Add dependencies to consider fixed delivery windows"""
        return super()._compute_expected_date()

    @api.onchange("expected_date", "commitment_date")
    def _onchange_commitment_date(self):
        """Warns if commitment date is not a preferred window for delivery"""
        res = super()._onchange_commitment_date()
        if res and "warning" in res:
            return res
        ps = self.partner_shipping_id
        if ps and self.commitment_date and ps.delivery_time_preference != "anytime":
            if not ps.is_in_delivery_window(self.commitment_date):
                return {"warning": self._commitment_date_no_delivery_window_match_msg()}

    def _commitment_date_no_delivery_window_match_msg(self):
        ps = self.partner_shipping_id
        commitment_date = self.commitment_date
        if ps.delivery_time_preference == "workdays":
            message = _(
                "The delivery date is {} ({}), but the partner is "
                "set to prefer deliveries on working days."
            ).format(commitment_date, commitment_date.strftime("%A"))
        else:
            windows = ps.get_delivery_windows().get(ps.id)
            message = _(
                "The delivery date is %s, but the shipping "
                "partner is set to prefer deliveries on following "
                "time windows:\n%s"
            ) % (
                format_datetime(self.env, self.commitment_date),
                "\n".join(["  * %s" % w.display_name for w in windows]),
            )
        return {
            "title": _(
                "Commitment date does not match shipping "
                "partner's Delivery time schedule preference."
            ),
            "message": message,
        }

    @api.depends("commitment_date", "expected_date")
    def _compute_display_expected_date_ok(self):
        for record in self:
            record.display_expected_date_ok = record._get_display_expected_date_ok()

    def _get_display_expected_date_ok(self):
        """Conditions to display the expected date on the so report."""
        # display_expected_date_ok is True date is set
        self.ensure_one()
        return bool(self.commitment_date or self.expected_date)

    def get_cutoff_time(self):
        self.ensure_one()
        partner = self.partner_shipping_id
        if (
            partner.order_delivery_cutoff_preference == "warehouse_cutoff"
            and self.warehouse_id.apply_cutoff
        ):
            return self.warehouse_id.get_cutoff_time()
        elif partner.order_delivery_cutoff_preference == "partner_cutoff":
            return self.partner_shipping_id.get_cutoff_time()
        else:
            return {}
