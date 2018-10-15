# Copyright 2018 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    'name': 'Sale Elaboration',
    'summary': 'Set an elaboration for any sale line',
    'version': '11.0.1.0.0',
    'development_status': 'Beta',
    'category': 'Sale',
    'website': 'https://github.com/OCA/sale-workflow',
    'author': 'Tecnativa, Odoo Community Association (OCA)',
    'license': 'AGPL-3',
    'application': False,
    'installable': True,
    'auto_install': True,
    'depends': [
        'sale_stock',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/sale_elaboration_views.xml',
        'views/sale_order_views.xml',
        'views/sale_elaboration_report_views.xml',
    ],
}
