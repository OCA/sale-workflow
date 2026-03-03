# Copyright 2024 Akretion (https://www.akretion.com).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Sale Order Line Display Stock Per Warehouse",
    "summary": "Sale Order Line Display Stock Per Warehouse",
    "version": "18.0.1.0.0",
    "category": "Hidden",
    "website": "https://github.com/OCA/sale-workflow",
    "author": "Akretion, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "maintainers": ["Kev-Roche"],
    "application": False,
    "installable": True,
    "depends": [
        "sale_stock",
    ],
    "data": [
        "views/res_config_settings.xml",
        "views/sale_order.xml",
        "views/stock_warehouse.xml",
    ],
}
