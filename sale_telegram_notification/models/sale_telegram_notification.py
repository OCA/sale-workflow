# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class SaleTelegramNotification(models.Model):
    _name = "sale.telegram.notification"
    _description = "Sales Telegram Notification Configuration"
    _inherit = ["mail.render.mixin"]

    name = fields.Char(required=True)
    active = fields.Boolean(default=True)
    gateway_id = fields.Many2one(
        "mail.gateway",
        string="Telegram Bot Gateway",
        domain="[('gateway_type', '=', 'telegram')]",
        required=True,
        ondelete="cascade",
    )
    chat_ids = fields.Many2many(
        "telegram.chat",
        "sale_telegram_notification_chat_rel",
        "notification_id",
        "chat_id",
        string="Telegram Chats",
        domain="[('gateway_id', '=', gateway_id)]",
        required=True,
        help="Chats to send the notification to.",
    )
    event_type = fields.Selection(
        [
            ("quotation_sent", "Quotation Sent"),
            ("sale_confirmed", "Sales Order Confirmed"),
            ("sale_cancelled", "Sales Order Cancelled"),
        ],
        string="Trigger Event",
        required=True,
        default="sale_confirmed",
    )
    message_template = fields.Text(
        required=True,
        help=(
            "Use Odoo standard template syntax, e.g., {{ object.name }} "
            "for dynamic placeholders."
        ),
        default="Sales Order {{ object.name }} has been confirmed!",
    )

    def _send_notification(self, order):
        self.ensure_one()
        try:
            rendered_message = self._render_template(
                self.message_template,
                "sale.order",
                [order.id],
                engine="inline_template",
            )[order.id]
        except Exception as e:
            _logger.error(
                "Error rendering Telegram message template for %s: %s",
                order.name,
                e,
            )
            return False

        if not rendered_message:
            _logger.warning(
                "Telegram message template for %s rendered as empty string",
                order.name,
            )
            return False

        success = True
        for chat in self.chat_ids:
            res = self.gateway_id.send_message(chat.chat_id, rendered_message)
            if not res:
                _logger.error(
                    "Failed to send Telegram notification to chat %s (bot: %s)",
                    chat.name,
                    self.gateway_id.name,
                )
                success = False
        return success
