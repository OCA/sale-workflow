# Copyright 2023 Ecosoft Co., Ltd (https://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "Sale - Multi branch",
    "version": "15.0.1.0.0",
    "license": "AGPL-3",
    "category": "Sales Management",
    "summary": "Add branch on Sale",
    "author": "Ecosoft, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/sale-workflow",
    "depends": ["sale_management", "account_multi_branch"],
    "data": [
        "views/sale_order_views.xml",
    ],
    "installable": True,
    "maintainers": ["Saran440"],
}
