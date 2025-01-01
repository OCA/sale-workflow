# Copyright 2023 ForgeFlow S.L.
# Copyright 2024 OERP Canada <https://www.oerp.ca>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
import logging

from dateutil.relativedelta import relativedelta

from odoo import fields, models

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = "sale.order"

    auto_cancel_expired_so = fields.Boolean(
        related="partner_id.auto_cancel_expired_so", string="Auto Cancel"
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
                [
                    ("state", "in", expired_states),
                    ("validity_date", "<", threshold),
                    ("auto_cancel_expired_so", "=", True),
                ]
            )
            for order in orders:
                try:
                    order.with_context(company_id=company.id)._action_cancel()
                except Exception as e:
                    _logger.error("Failed to auto-cancel %s: %s", (order.name, str(e)))
