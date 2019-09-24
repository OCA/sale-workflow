# Copyright 2019 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Sale General Term',
    'summary': "Multi-region and multi-language Sales General Terms",
    'version': '12.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'Open Source Integrators,Odoo Community Association (OCA)',
    'website': 'https://github.com/oca/sale-workflow',
    'depends': [
        'sale',
    ],
    'data': [
        'views/sale_order.xml',
        'security/sale_general_term.xml',
        'views/sale_general_term.xml',
        'report/sale_report_templates.xml',
    ],
    'demo': [
        'demo/sale_general_term.xml',
    ],
}
