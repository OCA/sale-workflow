from odoo import models, fields, api, _  # noqa
import re
import logging

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        self._send_telegram_notification("sale_confirmed")
        return res

    def action_cancel(self):
        """Override to send Telegram notification when order is canceled."""
        res = super(SaleOrder, self).action_cancel()
        # Send notification after cancellation is complete
        self._send_telegram_notification("sale_canceled")
        return res

    def action_quotation_send(self):
        res = super(SaleOrder, self).action_quotation_send()
        self._send_telegram_notification("quotation_sent")
        return res

    def _send_telegram_notification(self, event_type):
        """Send a notification to Telegram with better logging"""
        _logger = logging.getLogger(__name__)

        _logger.info(
            "Preparing to send %s notification for order %s", event_type, self.name
        )

        bot = self.env["telegram.notification"].search([], limit=1)
        if not bot:
            _logger.warning("No Telegram notification configuration found")
            return False

        _logger.info("Using Telegram bot: %s", bot.name)

        # Check if this event type is enabled
        is_enabled = bot.is_event_enabled(event_type)
        _logger.info("Event '%s' enabled: %s", event_type, is_enabled)

        if not is_enabled:
            _logger.warning(
                "Event '%s' is not enabled in Telegram configuration", event_type
            )
            return False

        # Generate message from template
        try:
            message = self._generate_notification_message(event_type, bot)
            _logger.info("Generated message: %s", message)

            # Send the message
            success = bot.send_message(message)
            if success:
                _logger.info(
                    "Successfully sent %s notification for order %s",
                    event_type,
                    self.name,
                )
            else:
                _logger.error(
                    "Failed to send %s notification for order %s", event_type, self.name
                )

            return success
        except Exception as e:
            _logger.exception(
                "Error sending %s notification for order %s: %s",
                event_type,
                self.name,
                str(e),
            )
            return False

    def _generate_notification_message(self, event_type, bot):
        """Generate notification message using templates and placeholders"""
        template = bot.get_template_for_event(event_type)
        if not template:
            # Fallback to default messages if template is empty
            if event_type == "sale_confirmed":
                return f"🎉 Sales Order {self.name} has been confirmed!"
            elif event_type == "quotation_sent":
                return f"📄 Quotation {self.name} has been sent"
            elif event_type == "sale_canceled":
                return f"❌ Sales Order {self.name} has been canceled"
            return f"Notification about Sales Order {self.name}"

        # Replace placeholders like ${order.name} with actual values
        def replace_placeholder(match):
            expr = match.group(1)
            try:
                # Start with self (the order) as the base object
                obj = self
                # Split by dots to traverse the object hierarchy
                for attr in expr.split(".")[1:]:  # Skip 'order'
                    obj = getattr(obj, attr)
                return str(obj) if obj is not None else ""
            except Exception as e:
                _logger.error(f"Error processing placeholder ${{{expr}}}: {str(e)}")
                return f"${{{expr}}}"

        # Replace all ${...} placeholders in the template
        message = re.sub(r"\${(order\.[^}]+)}", replace_placeholder, template)
        return message
