# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Sale Telegram Notification",
    "summary": "Send Telegram notifications for sales order events",
    "category": "Sales",
    "version": "18.0.1.0.0",
    "author": "Anmol Garg, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/sale-workflow",
    "license": "AGPL-3",
    "depends": [
        "sale",
        "mail_gateway_telegram_standalone",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/sale_telegram_notification_views.xml",
    ],
    "installable": True,
    "application": False,
    "development_status": "Stable",
}
