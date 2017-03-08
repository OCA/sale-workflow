# -*- coding: utf-8 -*-
#   Copyright (C) 2015 Akretion (http://www.akretion.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Sales Team Invoice Partner',
    'version': '10.0.1.0.0',
    'category': 'Sales Management',
    'summary': 'Adds invoice partner in sales team for use in a sale order',
    'author': 'Akretion, Odoo Community Association (OCA)',
    'website': 'http://www.akretion.com/',
    'license': 'AGPL-3',
    'depends': [
        'sales_team',
        'sale'
    ],
    'data': [
        'config/sale_config.yml',
        'sales_team_view.xml',
        'sale_view.xml',
    ],
    'demo': [
        'demo/sale.xml',
    ],
    'installable': True,
}
