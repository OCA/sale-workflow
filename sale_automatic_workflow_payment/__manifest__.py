# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Sale Automatic Workflow Payment",
    "summary": """
        Assign a workflow if a transaction is created for a sale order with
        an acquirer with a workflow""",
    "version": "13.0.1.0.0",
    "license": "AGPL-3",
    "development_status": "Beta",
    "category": "Sales",
    "maintainers": ["rousseldenis"],
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/sale-workflow",
    "depends": ["sale_automatic_workflow", "payment"],
    "data": ["views/payment_acquirer.xml"],
}
