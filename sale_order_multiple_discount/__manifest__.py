# Copyright 2018 Onestein (<http://www.onestein.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': "Sale Order Multiple Discount",
    'summary': "Express discounts on SO lines as mathematical expressions",
    'author': 'Onestein, Odoo Community Association (OCA)',
    'website': 'http://www.onestein.eu',
    'category': 'Sales',
    'license': 'AGPL-3',
    'version': '11.0.1.0.0',
    'depends': [
        'sale'
    ],
    'data': [
        'views/sale_order_view.xml',
        'views/account_invoice_view.xml',
    ]
}
