# -*- coding: utf-8 -*-
{
    'name': 'Sales Order with Department Categorization',
    'version': '1.0',
    'category': 'Generic Modules/Sales & Purchases',
    'description': """
Add the department on Sales Order and Customer Invoices
 as well as the related filter and button in the search form.""",
    'author': "Camptocamp,Odoo Community Association (OCA)",
    "license": "AGPL-3",
    'website': 'http://camptocamp.com',
    'depends': ['sale', 'invoice_department', 'hr'],
    'data': ['sale_view.xml'],
    'installable': True,
}
