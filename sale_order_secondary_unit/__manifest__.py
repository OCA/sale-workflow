# Copyright 2018-2020 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Sale Order Secondary Unit",
    "summary": "Sale product in a secondary unit",
    "version": "13.0.1.3.0",
    "development_status": "Production/Stable",
    "category": "Sale",
    "website": "https://github.com/OCA/sale-workflow",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "auto_install": True,
    "depends": ["sale", "product_secondary_unit"],
    "data": [
        "views/product_secondary_unit_views.xml",
        "views/product_views.xml",
        "views/sale_order_views.xml",
        "report/sale_report_templates.xml",
    ],
}
