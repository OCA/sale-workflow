# Copyright 2026 OpenStudio SAS
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

{
    "name": "Sale order partner company only",
    "version": "16.0.1.0.0",
    "category": "Sales",
    "license": "LGPL-3",
    "summary": "Restrict partner selection to companies in quotations and sales orders",
    "author": "OpenStudio SAS, Odoo Community Association (OCA)",
    "maintainers": ["maisim"],
    "website": "https://github.com/OCA/sale-workflow",
    "depends": [
        "base_view_inheritance_extension",
        "sale",
    ],
    "data": [
        "views/sale_order_views.xml",
    ],
    "installable": True,
}
