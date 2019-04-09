# Copyright ADHOC S.A.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
{
    'name': 'Sale Exception Credit Limit',
    'version': '12.0.1.0.0',
    'author': 'ADHOC SA, Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/sale-workflow',
    'license': 'AGPL-3',
    'depends': [
        'sale_exception',
    ],
    'data': [
        'security/sale_exception_credit_limit_security.xml',
        'data/exception_rule_data.xml',
        'views/res_partner_views.xml',
    ],
    'demo': [
        'demo/res_partner_demo.xml'
    ],
}
