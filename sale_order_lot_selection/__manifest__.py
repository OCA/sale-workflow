# Copyright (C) 2025 Cetmix OÜ
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Sale Order Lot Selection",
    "version": "16.0.1.0.1",
    "category": "Sales Management",
    "author": "Odoo Community Association (OCA), Agile Business Group",
    "website": "https://github.com/OCA/sale-workflow",
    "license": "AGPL-3",
    "depends": ["sale_stock", "stock_restrict_lot"],
    "data": [
        "security/ir.model.access.csv",
        "view/sale_view.xml",
        "view/lot_view.xml",
        "view/res_config_settings.xml",
        "wizards/stock_lot_add_to_sale_order.xml",
    ],
    "demo": ["demo/sale_demo.xml"],
    "maintainers": ["bodedra"],
    "installable": True,
}
