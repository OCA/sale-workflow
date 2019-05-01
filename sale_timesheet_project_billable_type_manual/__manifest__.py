# Copyright 2018-2019 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    'name': 'Sales Timesheet: edit Project\'s Billing Type',
    'version': '12.0.1.0.0',
    'category': 'Sales',
    'website': 'https://github.com/OCA/sale-workflow',
    'author':
        'Brainbean Apps, '
        'Odoo Community Association (OCA)',
    'license': 'AGPL-3',
    'installable': True,
    'application': False,
    'summary':
        'Allows to edit Project\'s Billing Type and manually override it',
    'depends': [
        'sale_timesheet',
    ],
    'data': [
        'views/project_project.xml',
    ],
}
