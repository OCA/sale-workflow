from odoo import models, fields, api
import requests
import logging
from odoo.exceptions import UserError
from odoo.tools.translate import _


logger = logging.getLogger(__name__)


class SaleOrderNotificationLog(models.Model):
    _name = "sale.order.notification.log"
    _description = _("Log for Sale Order Telegram Notifications")

    sale_order_id = fields.Many2one("sale.order", string=_("Sale Order"), required=True)
    event_type = fields.Selection(
        [("sale_canceled", _("Sale Canceled"))], required=True
    )
    sent = fields.Boolean(default=False)

    @api.model
    def create(self, vals):
        record = super(SaleOrderNotificationLog, self).create(vals)
        record.send_telegram_message()
        return record

    def send_telegram_message(self):
        telegram_bot = (
            self.env["ir.config_parameter"].sudo().get_param("telegram_bot_token")
        )
        chat_id = self.env["ir.config_parameter"].sudo().get_param("telegram_chat_id")

        if not telegram_bot or not chat_id:
            logger.warning(("Telegram bot token or chat ID not configured"))
            return

        message = ""
        if self.event_type == "sale_canceled":
            message = (
                _("🚨 Sales Order %s has been canceled!") % self.sale_order_id.name
            )

        if message:
            try:
                response = requests.post(
                    f"https://api.telegram.org/bot{telegram_bot}/sendMessage",
                    json={"chat_id": chat_id, "text": message},
                )
                if response.status_code == 200:
                    self.sent = True
            except Exception as e:
                logger.error(("Error sending Telegram message: %s"), str(e))
                raise UserError(_("Error sending Telegram notification"))
