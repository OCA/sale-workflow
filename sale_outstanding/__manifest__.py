# Copyright 2022 Stéphan Sainléger (Elabore)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "sale_outstanding",
    "version": "14.0.1.0.0",
    "author": "Elabore, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/sale-workflow",
    "license": "AGPL-3",
    "category": "Tools",
    "summary": "Calculates and displays the amount already invoiced for a sale order",
    # any module necessary for this one to work correctly
    "depends": ["base", "sale"],
    "qweb": [],
    "external_dependencies": {
        "python": [],
    },
    # always loaded
    "data": [
        "views/sale_views.xml",
    ],
    # only loaded in demonstration mode
    "demo": [],
    "js": [],
    "css": [],
    "installable": True,
    # Install this module automatically if all dependency have been previously
    # and independently installed.  Used for synergetic or glue modules.
    "auto_install": False,
    "application": False,
}
