# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Cashondelivery",
    "version": "12.0.1.0.0",
    "category": "Sales Management",
    "website": "https://github.com/OCA/sale-workflow",
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
        "views/account_payment_mode_view.xml",
        "views/sale_order_view.xml",
        "views/stock_picking_view.xml",
    ],
    "installable": True
}
