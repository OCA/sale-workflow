# Copyright 2018 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    'name': 'Sale General Discount',
    'summary': 'Discount per sale order',
    'version': '11.0.1.0.0',
    'development_status': 'Alpha',
    'category': 'Sales',
    'website': 'https://github.com/OCA/sale-workflow',
    'author': 'Tecnativa, Odoo Community Association (OCA)',
    'license': 'AGPL-3',
    'application': False,
    'installable': True,
    'depends': [
        'sale',
    ],
    'data': [
        'views/sale_order_view.xml',
        'views/res_partner_view.xml',
        'views/report_sale_order.xml',
    ],
}
