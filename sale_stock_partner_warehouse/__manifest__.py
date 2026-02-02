# Copyright 2024 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
{
    "name": "sale stock partner wharehouse",
    "summary": "Allow to choose by default a warehouse on SO based on a Partner parameter",
    "version": "16.0.1.0.0",
    "development_status": "Alpha",
    "category": "Warehouse Management",
    "website": "https://github.com/OCA/sale-workflow",
    "author": "Camptocamp, BCIM, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "data": [
        "views/partner_view.xml",
    ],
    "depends": [
        "sale_stock",
    ],
}
