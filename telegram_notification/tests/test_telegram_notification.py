from odoo.tests.common import TransactionCase
from unittest.mock import patch


class TestTelegramNotification(TransactionCase):

    def setUp(self):
        super(TestTelegramNotification, self).setUp()
        self.notification = self.env["telegram.notification"].create(
            {
                "name": "Test Bot",
                "token": "test_token",
                "chat_ids": "123456789",
            }
        )

    @patch("requests.post")
    def test_send_message_success(self, mock_post):
        mock_post.return_value.status_code = 200
        result = self.notification.send_message("Test message")
        self.assertTrue(result)
        mock_post.assert_called_once()

    @patch("requests.post")
    def test_send_message_failure(self, mock_post):
        mock_post.return_value.status_code = 400
        result = self.notification.send_message("Test message")
        self.assertFalse(result)
        mock_post.assert_called_once()

    def test_is_event_enabled(self):
        self.notification.enabled_event_sale_confirmed = True
        self.assertTrue(self.notification.is_event_enabled("sale_confirmed"))

    def test_get_template_for_event(self):
        template = self.notification.get_template_for_event("sale_confirmed")
        self.assertEqual(template, self.notification.sale_confirmed_template)
