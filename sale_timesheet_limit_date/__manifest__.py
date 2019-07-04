# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Invoice Sales Timesheets with a Date Limit',
    'summary': 'Layouts',
    'version': '12.0.1.0.0',
    'author': 'Camptocamp, '
    'Odoo Community Association (OCA)',
    'license': 'AGPL-3',
    'category': 'Sales',
    'depends': [
        'sale_timesheet',
    ],
    'website': 'https://github.com/OCA/sale-workflow',
    'data': [
        'views/sale_order_view.xml',
        'views/invoice_order_view.xml'
    ],
    'installable': True,
}
