# Copyright 2018 Carlos Dauden - Tecnativa <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    'name': 'Sale Stock Picking Note',
    'summary': 'Add picking note in Sale Order',
    'version': '12.0.1.0.0',
    'category': 'Sales',
    'website': 'https://github.com/OCA/sale-workflow',
    'author': 'Tecnativa, '
              'Open Source Integrators, '
              'Odoo Community Association (OCA)',
    'license': 'AGPL-3',
    'depends': [
        'sale_stock',
    ],
    'data': [
        'security/sale_order_security.xml',
        'views/sale_order_view.xml',
        'views/res_config_settings_view.xml',
    ],
    'installable': True,
}
