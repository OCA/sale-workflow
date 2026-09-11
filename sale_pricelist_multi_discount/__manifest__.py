# Copyright 2026 Innovyou
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
{
    "name": "Sale Pricelist Multi Discount",
    "summary": "Configure multiple multiplicative discounts on pricelist "
    "rules and propagate them to sale order lines.",
    "version": "18.0.1.0.0",
    "category": "Sales/Sales",
    "author": "Innovyou, Odoo Community Association (OCA)",
    "maintainers": ["LorenzoC0"],
    "website": "https://github.com/OCA/sale-workflow",
    "license": "LGPL-3",
    "depends": [
        "sale_multi_discount",
    ],
    "data": [
        "views/product_pricelist_item_views.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
