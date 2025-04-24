# Copyright 2025 Tecnativa - Carlos Roca
# Copyright 2025 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Sale Product Catalog Extended",
    "category": "Sales",
    "license": "AGPL-3",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "version": "18.0.1.0.0",
    "website": "https://github.com/OCA/sale-workflow",
    "depends": ["sale"],
    "data": ["views/sale_order_line_views.xml"],
    "assets": {
        "web.assets_backend": ["sale_product_catalog_extended/static/src/**/*"],
    },
    "installable": True,
}
