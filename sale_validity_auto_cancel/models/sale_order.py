# Copyright 2023 ForgeFlow S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
import logging

from dateutil.relativedelta import relativedelta

from odoo import fields, models

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = "sale.order"

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
