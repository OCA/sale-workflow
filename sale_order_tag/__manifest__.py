# Copyright 2021 Patrick Wilson <patrickraymondwilson@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Sale Order Tags",
    "summary": """Adds Tags to Sales Orders.""",
    "author": "Patrick Wilson, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/sale-workflow",
    "category": "Sale",
    "version": "14.0.1.0.1",
    "license": "AGPL-3",
    "depends": ["crm", "sale_management"],
    "data": [
        "data/sale_order_tag_data.xml",
        "security/ir.model.access.csv",
        "security/sale_order_tag_security.xml",
        "views/sale_order_tag.xml",
        "views/sale_order.xml",
    ],
    "application": False,
    "development_status": "Beta",
    "maintainers": ["patrickrwilson"],
}
