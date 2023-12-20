# Copyright 2023 Tecnativa - Carlos Dauden
# Copyright 2023 Tecnativa - Carlos Roca
# Copyright 2023 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Sale Order Product Picker",
    "version": "16.0.1.1.1",
    "development_status": "Beta",
    "category": "Sale",
    "website": "https://github.com/OCA/sale-workflow",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "installable": True,
    "post_init_hook": "_post_init_hook",
    "uninstall_hook": "_uninstall_hook",
    "depends": ["sale_stock"],
    "data": [
        "security/ir.model.access.csv",
        "views/product_views.xml",
        "views/sale_order_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "sale_order_product_picker/static/src/kanban/*",
            "sale_order_product_picker/static/src/x2many/*",
            "sale_order_product_picker/static/src/scss/picker.scss",
        ],
    },
}
