# Copyright 2023 ForgeFlow S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
import logging

from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = "sale.order"

    validity_date_warning_message = fields.Text(
        compute="_compute_validity_date_warning_message",
    )

    sale_validity_warning_enabled = fields.Boolean(
        related="company_id.sale_validity_warning_enabled", readonly=False,
    )

    def _get_expired_order_states(self):
        # Can be inherited to exclude/include order states
        return ["draft", "sent"]

    def cron_sale_validity_auto_cancel(self):
        today = fields.Date.today()
        for company in self.env["res.company"].search([]):
            threshold = today - relativedelta(
                days=company.sale_validity_auto_cancel_days
            )
            expired_states = self._get_expired_order_states()
            orders = self.env["sale.order"].search(
                [("state", "in", expired_states), ("validity_date", "<", threshold)]
            )
            for order in orders:
                try:
                    order.with_context(company_id=company.id).action_cancel()
                except Exception as e:
                    _logger.error("Failed to auto-cancel %s: %s" % (order.name, str(e)))

    @api.depends("validity_date", "company_id")
    def _compute_validity_date_warning_message(self):
        for order in self:
            order.validity_date_warning_message = False
            company = order.company_id or self.env["res.company"]._company_default_get(
                "sale.order"
            )
            if company.sale_validity_warning_days:
                today = fields.Date.today()
                expired_states = order._get_expired_order_states()
                auto_cancel_date = order.validity_date + relativedelta(
                    days=company.sale_validity_auto_cancel_days
                )
                warning_date = auto_cancel_date - relativedelta(
                    days=company.sale_validity_warning_days
                )
                if (
                    order.state in expired_states
                    and auto_cancel_date > today > warning_date
                ):
                    days = int((auto_cancel_date - today).days)
                    order.validity_date_warning_message = (
                        _(
                            "This Quotation will be automatically cancelled in %s days.\n"
                            "If needed, the expiration date (found on the 'Other info' tab) "
                            "can be updated to a future date."
                        )
                        % days
                    )
