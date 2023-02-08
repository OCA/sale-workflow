# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Sale Payment Method - Hold Pickings (until payment)",
    "version": "15.0.1.0.0",
    "website": "https://github.com/OCA/sale-workflow",
    "category": "Warehouse",
    "summary": """
    Sale Payment Method - Hold Pickings until payment
    ===================================================
    * This module allows to hold the picking until the invoice is paid""",
    "depends": [
        "stock",
        "website_sale",
        "sale_management",
        "account_payment_mode",
    ],
    "author": "initOS GmbH, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "data": [
        "views/stock.xml",
        "views/payment_method.xml",
        "views/sale_order_view.xml",
    ],
    "installable": True,
    "application": False,
}
