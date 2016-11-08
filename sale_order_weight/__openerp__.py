# -*- coding: utf-8 -*-
# © 2016 Andrea Cometa - Apulia Software
# License GPL-3.0 or later (http://www.gnu.org/licenses/gpl.html).

{
    'name': "Sale Order Weight",
    'version': '8.0.1.0.0',
    'description': """
This module adds products weight in report for sale.order.
""",
    'author': 'Apulia Software, Odoo Community Association (OCA)',
    'website': 'http://www.odoo-community.org',
    'license': 'GPL-3',
    'depends': [
        'sale',
    ],
    "data": [
        'views/sale_report.xml',
    ],
    "installable": True
}
