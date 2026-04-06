{
    "name": "Telegram Notification",
    "version": "16.0.1.0.0",
    "category": "Sales",
    "summary": "Send Telegram notifications for sales orders",
    "author": "Aditya Sebastian, Anmol Garg, Kartikey Sharma, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/sale-workflow",
    "license": "AGPL-3",
    "depends": [
        "sale",
    ],
    "data": [
        "security/ir.model.access.csv",
        "security/telegram_notification_security.xml",
        "views/telegram_notification_views.xml",
    ],
    "demo": [],
    "installable": True,
    "application": False,
    "auto_install": False,
    "external_dependencies": {
        "python": ["requests"],
    },
}
