# Copyright 2026 Aures Tic Consultors S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "Sale Customer Info Quantity Multiple",
    "summary": "Sell to a customer only in multiples of a quantity set in "
    "the product customer info",
    "version": "18.0.1.0.0",
    "category": "Sales Management",
    "website": "https://github.com/OCA/sale-workflow",
    "author": "Aures Tic Consultors S.L., Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": ["product_customerinfo_sale"],
    "data": [
        "views/product_customerinfo_views.xml",
        "views/sale_order_views.xml",
    ],
    "installable": True,
}
