# Copyright 2024 Ecosoft Co., Ltd. (https://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Sale Order Sequence Option",
    "summary": "Manage sequence options for sale.order",
    "version": "15.0.1.0.0",
    "author": "Ecosoft, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "development_status": "Alpha",
    "website": "https://github.com/OCA/sale-workflow",
    "category": "Sales",
    "depends": ["sale", "base_sequence_option"],
    "data": ["data/sale_sequence_option.xml"],
    "demo": ["demo/sale_demo_options.xml"],
    "maintainers": ["ps-tubtim"],
    "installable": True,
    "auto_install": False,
}
