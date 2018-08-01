# -*- coding: utf-8 -*-
# Copyright 2016 Onestein (<http://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    'name': 'Sale Order Mass Confirm',
    'summary': 'Allows confirmation of multiple sale orders in one click',
    'version': '10.0.1.0.0',
    'category': 'Sales',
    'website': 'https://github.com/OCA/sale-workflow',
    'author': 'Onestein, Odoo Community Association (OCA)',
    'license': 'AGPL-3',
    'installable': True,
    'depends': [
        'sale',
    ],
    'data': [
        'wizard/sale_order_confirm.xml',
    ],
}
