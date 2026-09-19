# Copyright 2026 OpenStudio SAS
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

{
    "name": "Sale Partner Sale Contact on Project",
    "summary": "Propagate sale contact from sale orders to projects",
    "version": "19.0.1.0.0",
    "category": "Sales Management",
    "website": "https://github.com/OCA/sale-workflow",
    "author": "OpenStudio SAS, Odoo Community Association (OCA)",
    "maintainers": ["maisim"],
    "license": "LGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "sale_partner_sale_contact",
        "sale_project",
    ],
    "data": [
        "views/project_project_views.xml",
    ],
}
