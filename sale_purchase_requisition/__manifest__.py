# Copyright 2023 Moduon - Andrea Cattalani
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl
{
    "name": "Sale purchase requisition",
    "summary": "Connect your quotations with a purchase agreement",
    "version": "14.0.1.0.1",
    "category": "Sale",
    "website": "https://github.com/OCA/sale-workflow",
    "author": "Moduon, Odoo Community Association (OCA)",
    "maintainers": ["shide", "anddago78", "yajo"],
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "sale",
        "purchase_requisition",
    ],
    "data": [
        "security/ir.model.access.csv",
        "security/sale_purchase_requisition_security.xml",
        "views/sale_order.xml",
        "views/purchase_requisition.xml",
    ],
}
