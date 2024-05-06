# Copyright 2024 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

{
    "name": "Sale Warn Option",
    "summary": "Add Options to Sale Warn Messages",
    "version": "15.0.1.0.1",
    "development_status": "Alpha",
    "category": "Sales/Sales",
    "website": "https://github.com/OCA/sale-workflow",
    "author": "Moduon, Odoo Community Association (OCA)",
    "maintainers": ["Shide", "rafaelbn"],
    "license": "LGPL-3",
    "application": False,
    "installable": True,
    "auto_install": True,
    "depends": ["sale", "base_warn_option"],
    "data": [
        "views/res_partner_views.xml",
        "views/product_template_views.xml",
    ],
}
