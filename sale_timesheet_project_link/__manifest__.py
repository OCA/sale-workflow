# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Sale Timesheet Project Link',
    'summary': """
        Simply adds a button on the sale order to be redirected on the
        linked projects""",
    'version': '11.0.1.0.1',
    'license': 'AGPL-3',
    'author': 'ACSONE SA/NV, Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/sale-workflow',
    'depends': [
        'project',
        'sale_timesheet',
    ],
    'data': [
        'views/sale_order.xml',
    ],
    'demo': [
    ],
}
