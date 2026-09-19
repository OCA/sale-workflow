# Copyright 2026 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Partner Last Sale Info",
    "summary": """
        Adds last sale order information on partner forms""",
    "version": "17.0.1.0.0",
    "license": "AGPL-3",
    "category": "Sales",
    "author": "Open Source Integrators,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/sale-workflow",
    "depends": ["sale"],
    "data": [
        "views/res_partner.xml",
    ],
    # Uncomment in large databases to skip automatically populating the data
    # "pre_init_hook": "pre_init_hook",
    "installable": True,
}
