# Copyright 2018 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    'name': 'Sales Timesheet (non-billable)',
    'version': '12.0.1.0.0',
    'category': 'Sales Management',
    'website': 'https://github.com/OCA/sale-workflow',
    'author':
        'Brainbean Apps, '
        'Odoo Community Association (OCA)',
    'license': 'AGPL-3',
    'installable': True,
    'application': False,
    'summary': (
        'Allows selective exclusion of timesheet entries from sales order'
    ),
    'depends': [
        'hr_timesheet',
        'sale_timesheet',
    ],
    'data': [
        'views/account_analytic_line.xml',
        'views/project_task.xml',
    ],
}
