# -*- coding: utf-8 -*-
# © 2013 Agile Business Group sagl (<http://www.agilebg.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Sale order revisions',
    'version': '10.0.0.1.0',
    'category': 'Sale Management',
    'author': 'Agile Business Group,'
              'Camptocamp,'
              'Akretion,'
              'Ecosoft,'
              'Odoo Community Association (OCA)',
    'website': 'http://www.agilebg.com',
    'license': 'AGPL-3',
    'depends': ['sale'],
    'data': [
        'view/sale_order.xml',
    ],
    'test': [
        'test/sale_order.yml',
    ],
    'installable': True,
    'auto_install': False,
    'post_init_hook': 'populate_unrevisioned_name',
}
