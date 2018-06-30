# -*- coding: utf-8 -*-
# © 2017 Niboo (author: Jérôme Guerriat)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    'name': 'Sale - Proforma from quotation',
    'category': 'Sales Management',
    'license': 'AGPL-3',
    'website': 'https://www.niboo.be',
    'version': '10.0.1.0.0',
    'author': 'Niboo,Odoo Community Association (OCA)',
    'depends': [
        'sale',
    ],
    'data': [
        'reports/sale_order_report.xml',
        'views/sale_order.xml',
    ],
    'installable': True,
    'application': False,
}
