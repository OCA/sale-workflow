# -*- coding: utf-8 -*-
# © 2017 Ecosoft (ecosoft.co.th).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Sales - Isolated Quotation',
    'version': '10.0.1.0.0',
    'author': 'Ecosoft,Odoo Community Association (OCA)',
    'category': 'Sales',
    'website': 'https://github.com/OCA/sale-workflow',
    'depends': ['sale'],
    'license': 'AGPL-3',
    'images': [],
    'data': [
        'data/ir_sequence_data.xml',
        'views/sale_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'uninstall_hook': 'uninstall_hook',
    'post_init_hook': 'post_init_hook',
}
