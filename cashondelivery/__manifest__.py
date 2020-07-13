# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Cashondelivery",
    "version": "12.0.1.0.0",
    "category": "Sales Management",
    "website": "https://nodrizatech.com/",
    "author": "Odoo Nodriza Tech (ONT), "
              "Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": [
        "base",
        "sale",
        "stock",
        "payment"
    ],
    "data": [
        "views/account_payment_mode_views.xml",
        "views/sale_order_views.xml",
        "views/stock_picking_views.xml",
    ],
    "installable": True,
}
