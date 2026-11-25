# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from unittest.mock import patch

from odoo.tests.common import TransactionCase
from odoo.tools import mute_logger


class TestSaleTelegramNotification(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.partner = cls.env["res.partner"].create({"name": "Test Customer"})

        # Create a mock mail gateway of type telegram
        cls.gateway = cls.env["mail.gateway"].create(
            {
                "name": "Test Telegram Bot",
                "gateway_type": "telegram",
                "token": "123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11",
            }
        )

        # Create a telegram chat for the gateway
        cls.chat = cls.env["telegram.chat"].create(
            {
                "name": "Admin Channel",
                "chat_id": "-100123456789",
                "gateway_id": cls.gateway.id,
            }
        )

        # Create configurations for different events
        cls.notif_confirmed = cls.env["sale.telegram.notification"].create(
            {
                "name": "Order Confirmed Alert",
                "gateway_id": cls.gateway.id,
                "chat_ids": [(4, cls.chat.id)],
                "event_type": "sale_confirmed",
                "message_template": (
                    "Order {{ object.name }} is confirmed for "
                    "{{ object.partner_id.name }}."
                ),
            }
        )

        cls.notif_cancelled = cls.env["sale.telegram.notification"].create(
            {
                "name": "Order Cancelled Alert",
                "gateway_id": cls.gateway.id,
                "chat_ids": [(4, cls.chat.id)],
                "event_type": "sale_cancelled",
                "message_template": "Order {{ object.name }} cancelled.",
            }
        )

        cls.notif_sent = cls.env["sale.telegram.notification"].create(
            {
                "name": "Quotation Sent Alert",
                "gateway_id": cls.gateway.id,
                "chat_ids": [(4, cls.chat.id)],
                "event_type": "quotation_sent",
                "message_template": "Quotation {{ object.name }} sent.",
            }
        )

        # Create a sales order
        cls.sale_order = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "state": "draft",
            }
        )

    def test_confirm_notification(self):
        """Test that Telegram notification is sent upon order confirmation"""
        with patch.object(
            self.gateway.__class__, "send_message", return_value=True
        ) as mock_send:
            self.sale_order.action_confirm()
            expected_msg = (
                f"Order {self.sale_order.name} is confirmed for Test Customer."
            )
            mock_send.assert_called_once_with("-100123456789", expected_msg)

    def test_cancel_notification(self):
        """Test that Telegram notification is sent upon order cancellation"""
        with patch.object(
            self.gateway.__class__, "send_message", return_value=True
        ) as mock_send:
            self.sale_order.with_context(disable_cancel_warning=True).action_cancel()
            expected_msg = f"Order {self.sale_order.name} cancelled."
            mock_send.assert_called_once_with("-100123456789", expected_msg)

    def test_sent_notification(self):
        """Test Telegram notification is sent upon quotation state change to sent."""
        with patch.object(
            self.gateway.__class__, "send_message", return_value=True
        ) as mock_send:
            # Change state to sent (simulating email send or manually sending quotation)
            self.sale_order.write({"state": "sent"})
            expected_msg = f"Quotation {self.sale_order.name} sent."
            mock_send.assert_called_once_with("-100123456789", expected_msg)

    def test_no_notification_found(self):
        """Test that nothing happens if no active notifications exist."""
        # Deactivate all notifications
        self.env["sale.telegram.notification"].search([]).write({"active": False})
        with patch.object(
            self.gateway.__class__, "send_message", return_value=True
        ) as mock_send:
            self.sale_order.action_confirm()
            mock_send.assert_not_called()

        # Restore active state for other tests just in case
        self.env["sale.telegram.notification"].search([("active", "=", False)]).write(
            {"active": True}
        )

    @mute_logger(
        "odoo.addons.sale_telegram_notification.models.sale_telegram_notification"
    )
    def test_exception_rendering(self):
        """Test that exception during rendering is caught and handled."""
        with patch.object(
            self.gateway.__class__, "send_message", return_value=True
        ) as mock_send:
            with patch.object(
                self.notif_confirmed.__class__,
                "_render_template",
                side_effect=Exception("Test Exception"),
            ):
                self.sale_order.action_confirm()
                mock_send.assert_not_called()

    @mute_logger(
        "odoo.addons.sale_telegram_notification.models.sale_telegram_notification"
    )
    def test_empty_string_rendering(self):
        """Test that empty string rendering is handled."""
        with patch.object(
            self.gateway.__class__, "send_message", return_value=True
        ) as mock_send:
            with patch.object(
                self.notif_confirmed.__class__,
                "_render_template",
                return_value={self.sale_order.id: ""},
            ):
                self.sale_order.action_confirm()
                mock_send.assert_not_called()

    @mute_logger(
        "odoo.addons.sale_telegram_notification.models.sale_telegram_notification"
    )
    def test_send_message_failure(self):
        """Test that send message failure is handled and logs an error."""
        with patch.object(
            self.gateway.__class__, "send_message", return_value=False
        ) as mock_send:
            self.sale_order.action_confirm()
            mock_send.assert_called_once()

    def test_write_no_state_change(self):
        """Test write without state change to sent."""
        with patch.object(
            self.gateway.__class__, "send_message", return_value=True
        ) as mock_send:
            self.sale_order.write({"note": "Test Note"})
            mock_send.assert_not_called()
