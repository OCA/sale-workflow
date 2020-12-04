# Copyright 2020 Tecnativa - Alexandre D. Díaz
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

{
    "name": "Sale PWA Cache",
    "summary": "Adds support to cache sales",
    "version": "12.0.1.0.0",
    "development_status": "Beta",
    "category": "Website",
    "website": "https://github.com/OCA/web",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "maintainers": ["Tardo"],
    "license": "LGPL-3",
    "application": True,
    "installable": True,
    "depends": [
        'sale_management',
        'web_pwa_cache',
        'product_pwa_cache',
        'web_widget_one2many_product_picker',
    ],
    "data": [
        'templates/assets.xml',
        'views/sale_order_views.xml',
        'data/data.xml',
    ],
    'qweb': [
        'static/src/xml/one2many_product_picker.xml',
    ],
}
