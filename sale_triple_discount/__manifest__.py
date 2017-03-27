# -*- coding: utf-8 -*-
# Copyright 2015 ADHOC SA  (http://www.adhoc.com.ar)
# Copyright 2017 Alex Comba - Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'Sale Triple Discount',
    'version': '10.0.1.0.0',
    'category': 'Sales Management',
    'author': 'ADHOC SA, Agile Business Group, '
              'Odoo Community Association (OCA)',
    'website': 'www.adhoc.com.ar',
    'license': 'AGPL-3',
    'summary': 'Manage triple discount on sale order lines '
               'and on invoice lines',
    'depends': [
        'sale',
        'account'
    ],
    'data': [
        'views/sale_order_view.xml',
        'views/account_invoice_view.xml',
        'views/res_partner_view.xml',
    ],
    'installable': True,
}
