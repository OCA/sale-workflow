# -*- coding: utf-8 -*-
# Copyright 2015 ADHOC SA  (http://www.adhoc.com.ar)
# Copyright 2017 Alex Comba - Agile Business Group
# Copyright 2017 Tecnativa - David Vidal
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Sale Triple Discount',
    'version': '10.0.1.0.0',
    'category': 'Sales Management',
    'author': 'ADHOC SA, '
              'Agile Business Group, '
              'Tecnativa, '
              'Odoo Community Association (OCA)',
    'website': 'https://odoo-community.org',
    'license': 'AGPL-3',
    'summary': 'Manage triple discount on sale order lines',
    'depends': [
        'sale',
        'account_invoice_triple_discount',
    ],
    'data': [
        'views/sale_order_view.xml',
    ],
    'installable': True,
}
