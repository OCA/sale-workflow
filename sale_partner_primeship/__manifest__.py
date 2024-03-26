# Copyright 2021 Akretion - Florian Mounier
{
    "name": "Sale Partner Primeship",
    "summary": """Allow you to manage time limited prime memberships
    and prime membership activation products.""",
    "version": "14.0.1.0.0",
    "author": "Akretion, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/sale-workflow",
    "category": "Sales",
    "depends": ["sale", "account_invoice_start_end_dates"],
    "data": [
        "views/product_template_views.xml",
        "views/sale_primeship_views.xml",
        "views/res_partner_views.xml",
        "security/ir.model.access.csv",
        "security/sale_partner_primeship.xml",
    ],
    "license": "LGPL-3",
}
