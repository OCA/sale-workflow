# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging

from odoo import models

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _send_telegram_notification(self, event_type):
        """Find active configurations for the given event type and send notifications"""
        notifications = self.env["sale.telegram.notification"].search(
            [("event_type", "=", event_type), ("active", "=", True)]
        )
        if not notifications:
            return

        _logger.info(
            "Sending Telegram notifications for order %s (event: %s)",
            self.name,
            event_type,
        )
        for notification in notifications:
            notification._send_notification(self)

    def action_confirm(self):
        res = super().action_confirm()
        for order in self:
            if order.state == "sale":
                order._send_telegram_notification("sale_confirmed")
        return res

    def action_cancel(self):
        res = super().action_cancel()
        for order in self:
            if order.state == "cancel":
                order._send_telegram_notification("sale_cancelled")
        return res

    def write(self, vals):
        # Detect quotation sent event by state transition from draft -> sent
        sent_orders = self.env["sale.order"]
        if vals.get("state") == "sent":
            sent_orders = self.filtered(lambda o: o.state == "draft")

        res = super().write(vals)

        for order in sent_orders:
            order._send_telegram_notification("quotation_sent")

        return res
