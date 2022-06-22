# Copyright 2022 Open Source Integrators
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Sale Partner Approval",
    "summary": "Control Partners that can be used in Sales Orders",
    "version": "15.0.1.0.0",
    "website": "https://github.com/OCA/sale-workflow",
    "category": "Sales",
    "author": "Open Source Integrators, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "installable": True,
    "maintainers": ["dreispt"],
    "development_status": "Alpha",
    "depends": [
        "partner_stage",  # oca/product-attribute
        "sale_exception",
    ],
    "data": [
        "data/exception_rule.xml",
        "data/init_sale_ok.xml",
        "views/res_partner_stage.xml",
        "views/res_partner.xml",
    ],
}
