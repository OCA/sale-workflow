# Copyright 2021 Open Source Integrators
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Manufacturing Approval Workflow",
    "summary": "Manufacturing Product Apploval Workflow",
    "version": "14.0.1.0.0",
    "website": "https://github.com/OCA/sale-workflow",
    "category": "Products",
    "author": "Open Source Integrators, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "installable": True,
    "maintainers": ["dreispt"],
    "development_status": "Alpha",
    "depends": ["mrp", "sale_product_approval"],
    "data": [
        "views/product_state.xml",
        "views/product_template.xml",
        "views/mrp_production.xml",
        "views/mrp_bom.xml",
        "views/mrp_production_exception.xml",
    ],
}
