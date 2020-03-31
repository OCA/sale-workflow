# Copyright 2020 Akretion France (http://www.akretion.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Sale Check Preparation Time',
    'summary': 'Check preparation time of sale order',
    'version': '12.0.1.0.0',
    'category': 'Sales',
    'author': 'Akretion, Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/sale-workflow',
    'license': 'AGPL-3',
    'depends': ['sale_management', 'sale_stock'],
    'data': [
        'data/res_config_data.xml',
        'views/sale_order.xml',
        'views/res_company.xml',
    ],
    'installable': True,
}
