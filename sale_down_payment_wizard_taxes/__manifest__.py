# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Sale Down Payment Wizard Taxes",
    "summary": """
        Adds the option to set the tax on down payment""",
    "version": "13.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "website": "https://www.acsone.eu",
    "depends": [
        "sale",
    ],
    "data": [
        "views/sale_make_invoice_advance_views.xml",
    ],
    "demo": [],
}
