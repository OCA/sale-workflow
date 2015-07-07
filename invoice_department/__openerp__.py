# -*- coding: utf-8 -*-
{
    'name': 'Invoices with Department Categorization',
    'version': '1.0',
    'category': 'Generic Modules/Sales & Purchases',
    'description': """
Add the department on Invoices as well as the related
 filter and button in the search form.""",
    'author': "Camptocamp,Odoo Community Association (OCA)",
    'website': 'http://camptocamp.com',
    'license': 'AGPL-3',
    'depends': ['account', 'hr'],
    'data': ['invoice_view.xml'],
    'installable': True,
}
