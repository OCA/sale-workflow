# Copyright 2015-2019 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Sale Packaging",
    "version": "12.0.1.0.0",
    "author": 'ACSONE SA/NV, '
              'Odoo Community Association (OCA)',
    "category": "Warehouse",
    "development_status": "Stable/Production",
    "maintainers": ["rousseldenis"],
    "website": "http://github.com/OCA/sale-workflow",
    'summary': "In sale, use uom's package",
    "depends": [
        "sale_stock",
        "packaging_uom",
    ],
    "data": [
        "views/sale_order_line_views.xml",
    ],
    "license": "AGPL-3",
    "installable": True,
}
