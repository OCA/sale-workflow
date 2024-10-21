# Copyright 2024 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
{
    "name": "Sale Order Split Strategy",
    "summary": "Define strategies to split sales orders",
    "version": "14.0.1.0.0",
    "development_status": "Alpha",
    "category": "Sales Management",
    "website": "https://github.com/OCA/sale-workflow",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "maintainers": ["grindtildeath"],
    "license": "AGPL-3",
    "depends": [
        "sale",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/mail_message_template.xml",
        "views/sale_order_split_strategy.xml",
        "views/sale_order.xml",
    ],
}
