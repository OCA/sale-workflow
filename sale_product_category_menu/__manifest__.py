# Copyright 2020 Manuel Regidor <manuel.regidor@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Sale Product Category Menu",
    "summary": "Shows 'Product Categories' menu item in Sales",
    "version": "12.0.1.0.3",
    "category": "Product",
    "website": "https://github.com/OCA/sale-workflow",
    "author": "Sygel, "
              "Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "sale",
    ],
    "data": [
        "views/sale_views.xml",
    ],
}
