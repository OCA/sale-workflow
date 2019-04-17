# Copyright 2019 JARSA Sistemas S.A. de C.V.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
{
    'name': 'Sale Request',
    'summary': 'Create Sale Order From Sale Requests by Product',
    'version': '12.0.1.0.0',
    'author': 'Jarsa Sistemas S.A. de C.V., '
              'Odoo Community Association (OCA)',
    'category': 'Sales',
    'website': 'https://github.com/OCA/sale-workflow',
    'license': 'LGPL-3',
    'depends': [
        'sale_management',
        'sale_stock',
    ],
    'data': [
        'data/ir_sequence_data.xml',
        'data/ir_config_parameter_time_sale_request.xml',
        'security/sale_request_security.xml',
        'security/ir.model.access.csv',
        'wizards/create_sale_order_wizard_view.xml',
        'wizards/link_sale_order_wizard_view.xml',
        'wizards/create_sale_order_wizard_zone_hour_view.xml',
        'views/sale_order_view.xml',
        'views/sale_request_view.xml',
    ],
}
