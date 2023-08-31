# Copyright 2023 Ows - Henrik Norlin
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Sell Product Variants with Resources",
    "summary": "",
    "author": "Ows, Odoo Community Association (OCA)",
    "category": "Appointments",
    "data": [
        "views/product_attribute_views.xml",
        "views/product_product_views.xml",
        "views/product_template_views.xml",
        "views/menus.xml",
    ],
    "depends": [
        "sale_resource_booking",
    ],
    "development_status": "Alpha",
    "license": "AGPL-3",
    "maintainers": ["ows-cloud"],
    "post_init_hook": "post_init_hook",
    "uninstall_hook": "uninstall_hook",
    "version": "16.0.1.0.0",
    "website": "https://github.com/OCA/sale-workflow",
}
