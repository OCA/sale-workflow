import requests
import logging
from odoo import models, fields, api  # noqa

logger = logging.getLogger(__name__)


class TelegramNotification(models.Model):
    _name = "telegram.notification"
    _description = "Telegram Notification Configuration"

    name = fields.Char(string="Bot Name", required=True)
    token = fields.Char(string="Bot Token", required=True)
    chat_ids = fields.Text(
        string="Chat IDs", help="Comma-separated list of Telegram chat IDs"
    )

    # Change from Selection to Many2many with selection_add
    enabled_event_sale_confirmed = fields.Boolean("Sales Order Confirmed", default=True)
    enabled_event_quotation_sent = fields.Boolean("Quotation Sent", default=False)
    enabled_event_sale_canceled = fields.Boolean("Sales Order Canceled", default=False)

    # Message templates for different events
    sale_confirmed_template = fields.Text(
        string="Sale Confirmed Message",
        default="🎉 Sales Order ${order.name} has been confirmed!\n"
        "Customer: ${order.partner_id.name}\n"
        "Total: ${order.amount_total} ${order.currency_id.name}",
        help="Available placeholders: ${order.name}, ${order.partner_id.name}, ${order.amount_total}, ${order.currency_id.name}, etc.",
    )
    quotation_sent_template = fields.Text(
        string="Quotation Sent Message",
        default="📄 Quotation ${order.name} has been sent to ${order.partner_id.name}.\n"
        "Total: ${order.amount_total} ${order.currency_id.name}",
        help="Available placeholders: ${order.name}, ${order.partner_id.name}, ${order.amount_total}, ${order.currency_id.name}, etc.",
    )
    sale_canceled_template = fields.Text(
        string="Sale Canceled Message",
        default="❌ Sales Order ${order.name} has been canceled.\n"
        "Customer: ${order.partner_id.name}",
        help="Available placeholders: ${order.name}, ${order.partner_id.name}, ${order.amount_total}, ${order.currency_id.name}, etc.",
    )

    def send_message(self, message, chat_id=None):
        """Send message to Telegram with improved error handling and logging"""
        logger.info("Attempting to send Telegram message: %s", message)

        if not self.token:
            logger.error("Cannot send message: Bot token is missing")
            return False

        # If no specific chat_id is provided, use all configured chat_ids
        if not chat_id and not self.chat_ids:
            logger.error("Cannot send message: No chat IDs configured")
            return False

        success = False
        if not chat_id:
            # Send to all configured chat IDs
            chat_ids = [cid.strip() for cid in self.chat_ids.split(",") if cid.strip()]
            if not chat_ids:
                logger.error("No valid chat IDs found in configuration")
                return False

            logger.info("Sending message to %d chat(s)", len(chat_ids))
            for chat_id in chat_ids:
                success = self._send_to_chat(chat_id, message) or success
        else:
            success = self._send_to_chat(chat_id, message)

        return success

    def _send_to_chat(self, chat_id, message):
        """Send message to a specific chat with detailed error handling"""
        url = f"https://api.telegram.org/bot{self.token}/sendMessage"

        # Try with HTML first, fallback to plain text if that fails
        try:
            logger.info("Sending to chat ID: %s with HTML formatting", chat_id)
            payload = {"chat_id": chat_id, "text": message, "parse_mode": "HTML"}
            response = requests.post(url, json=payload, timeout=10)

            if response.status_code == 200:
                logger.info("Message sent successfully to chat ID: %s", chat_id)
                return True
            elif response.status_code == 400:  # Bad request - might be parse mode issue
                logger.warning("HTML formatting failed, trying plain text")
                payload = {"chat_id": chat_id, "text": message}
                response = requests.post(url, json=payload, timeout=10)

                if response.status_code == 200:
                    logger.info(
                        "Plain text message sent successfully to chat ID: %s", chat_id
                    )
                    return True
                else:
                    logger.error(
                        "Failed to send plain text message (HTTP %s): %s",
                        response.status_code,
                        response.text,
                    )
                    return False
            else:
                logger.error(
                    "Failed to send message (HTTP %s): %s",
                    response.status_code,
                    response.text,
                )
                return False
        except requests.RequestException as e:
            logger.error("Network error sending Telegram message: %s", str(e))
            return False
        except Exception as e:
            logger.error(
                "Unexpected error sending Telegram message: %s", str(e), exc_info=True
            )
            return False

    def is_event_enabled(self, event_type):
        """Check if the specified event type is enabled for this configuration"""
        if event_type == "sale_confirmed":
            return self.enabled_event_sale_confirmed
        elif event_type == "quotation_sent":
            return self.enabled_event_quotation_sent
        elif event_type == "sale_canceled":
            return self.enabled_event_sale_canceled
        return False

    def get_template_for_event(self, event_type):
        """Get the template for the specified event type"""
        templates = {
            "sale_confirmed": self.sale_confirmed_template,
            "quotation_sent": self.quotation_sent_template,
            "sale_canceled": self.sale_canceled_template,
        }
        return templates.get(event_type, "")
