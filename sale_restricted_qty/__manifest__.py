# Copyright 2019 Akretion (<http://www.akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Sale order min quantity",
    "version": "14.0.1.1.1",
    "category": "Sales Management",
    "author": "Akretion, Odoo Community Association (OCA)",
    "contributors": ["Ashish Hirpara"],
    "maintainers": ["ashishhirapara"],
    "website": "https://github.com/OCA/sale-workflow",
    "license": "AGPL-3",
    "external_dependencies": {
        "python": ["openupgradelib"],
    },
    "depends": ["sale_management"],
    "data": [
        "views/product_category_views.xml",
        "views/product_template_views.xml",
        "views/product_product_views.xml",
        "views/sale_views.xml",
    ],
    "pre_init_hook": "rename_module",
    "installable": True,
}
