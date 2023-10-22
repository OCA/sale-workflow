# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Sale Payment Method - Hold Pickings (until payment)",
    "version": "15.0.1.0.0",
    "website": "https://github.com/OCA/sale-workflow",
    "category": "Warehouse",
    "summary": "This module allows to hold the picking until the invoice is paid",
    "depends": [
        "account_payment_mode",
        "sale_stock_picking_blocking",
        "website_sale",
    ],
    "author": "initOS GmbH, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "data": [
        "views/payment_method.xml",
        "views/res_config_settings_view.xml",
        "views/sale_order_view.xml",
    ],
    "installable": True,
    "application": False,
}
