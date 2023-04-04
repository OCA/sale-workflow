# Copyright 2023 Moduon - Andrea Cattalani
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl
{
    "name": "Sale purchase requisition analytic",
    "summary": "Add analytic account in purchase agreement",
    "version": "14.0.1.0.0",
    "category": "Sale",
    "website": "https://github.com/OCA/sale-workflow",
    "author": "Moduon, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "purchase_requisition_analytic",
    ],
    "data": [
        "views/purchase_requisition.xml",
    ],
}
