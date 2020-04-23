# -*- coding: utf-8 -*-
# Copyright 2018 PlanetaTIC - Lluís Rovira <lrovira@planetatic.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Sale Order Pending Payment",
    "version": "10.0.1.0.0",
    "author": "PlanetaTIC, Odoo Community Association (OCA)",
    "website": "https://www.planetatic.com",
    "license": "AGPL-3",
    "description": """
        Show amount total pending in sale order form and template when an
        advance invoice has already been paid.""",
    "category": "Sales Management",
    "depends": [
        "sale",
    ],
    "data": [
        'report/sale_report_templates.xml',
        "views/sale_views.xml",
    ],
    "installable": True,
}
