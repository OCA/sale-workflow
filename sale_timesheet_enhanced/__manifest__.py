# Copyright 2018 Brainbean Apps
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    'name': 'Sales Timesheet (enhanced)',
    'version': '12.0.1.0.0',
    'category': 'Sales',
    'website': 'https://github.com/OCA/sale-workflow',
    'author':
        'Brainbean Apps, '
        'Odoo Community Association (OCA)',
    'license': 'AGPL-3',
    'installable': True,
    'application': False,
    'summary': 'Enhanced selling timesheets in your sales order',
    'depends': [
        'sale_timesheet',
    ],
    'data': [
        'views/account_analytic_line.xml',
        'views/project_project.xml',
        'views/project_task.xml',
        'wizard/project_create_sale_order.xml',
    ],
}
