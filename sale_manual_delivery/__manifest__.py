# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'Sale Manual Delivery',
    'category': 'Sales',
    'author': 'Camptocamp SA, Odoo Community Association (OCA)',
    "license": "AGPL-3",
    'version': '10.0.2.0.0',
    'website': 'https://github.com/OCA/sale-workflow',
    'summary': "Create manually your deliveries",
    'depends': [
        'sale_stock',
        'delivery',
    ],
    'data': [
        'views/crm_team_view.xml',
        'views/sale_order_view.xml',
        'views/procurement_view.xml',
        'wizard/manual_proc_view.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
