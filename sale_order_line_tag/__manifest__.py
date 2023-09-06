# Copyright 2023 Open Source Integrators
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Sale Order Line Tag",
    "version": "16.0.1.0.0",
    "category": "Sales Management",
    "summary": "Add tags to classify sales order line reasons",
    "author": "Open Source Integrators, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/sale-workflow",
    "license": "AGPL-3",
    "depends": ["sale"],
    "data": [
        "security/ir.model.access.csv",
        "views/sale_order_views.xml",
    ],
    "maintainers": ["smaciaosi", "dreispt", "ckolobow"],
}
