This module links the base Telegram bot integration (`mail_gateway_telegram_standalone`) with Sales Order events.

### Features
* **Event-based outbound alerts** for sales order:
  * Quotation Sent
  * Sales Order Confirmed
  * Sales Order Cancelled
* **Dynamic Placeholders**: Customize message templates securely using Odoo's native sandboxed template engine (e.g. `{{ object.name }}`).
* **Multi-Chat Broadcast**: Configure multiple chats per notification rule.
