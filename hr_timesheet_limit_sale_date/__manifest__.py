# Copyright 2016-2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Invoice Sales Timesheets with a Date Limit',
    'summary': 'Layouts',
    'version': '11.0.1.0.0',
    'author': 'Camptocamp',
    'maintainer': 'Camptocamp',
    'category': 'Sales',
    'depends': [
        'sale_timesheet',
    ],
    'website': 'https://www.camptocamp.com',
    'data': [
        'views/sale_order_view.xml',
        'views/invoice_order_view.xml'
    ],
    'installable': True,
}
