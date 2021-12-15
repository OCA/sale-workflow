# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Sale Timesheet Lock Invoiced',
    'summary': """
        Forbid to update a timesheet line if it has been invoiced.""",
    'version': '11.0.1.0.1',
    'license': 'AGPL-3',
    'author': 'ACSONE SA/NV,Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/sale-workflow',
    'depends': [
        'sale_timesheet',
    ],
    'data': [
    ],
    'demo': [
    ],
}
