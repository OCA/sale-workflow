# coding: utf-8
# Copyright 2018 Acsone
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    'name': 'Blanket Orders',
    'category': 'Sale',
    'license': 'AGPL-3',
    'author': 'Acsone SA/NV,Odoo Community Association (OCA)',
    'version': '10.0.1.0.0',
    'website': 'https://github.com/OCA/sale-workflow',
    'summary': "Blanket Orders",
    'depends': [
        'sale',
        'web_action_conditionable',
    ],
    'data': [
        'data/sequence.xml',
        'data/ir_cron.xml',
        'security/ir.model.access.csv',
        'security/security.xml',
        'wizard/create_sale_orders.xml',
        'views/blanket_orders.xml',
        'views/sale_orders.xml',
        'report/templates.xml',
        'report/report.xml',
    ],
    'installable': True,
}
