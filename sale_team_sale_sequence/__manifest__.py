# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Sale Team Sale Sequence",
    "summary": "Assign a sequence per sales team for sale order numbering",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/sale-workflow",
    "category": "Sales",
    "version": "19.0.1.0.0",
    "license": "AGPL-3",
    "depends": ["sale", "sales_team"],
    "data": ["views/crm_team.xml", "views/sale_order.xml"],
    "installable": True,
}
