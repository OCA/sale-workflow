# -*- coding: utf-8 -*-
# © 2015 Stefan Rijnhart - Opener B.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Modify sale delivery address",
    "summary": "Allow to modify the sale delivery address until the order \
is fully delivered",
    "category": "Sale",
    "version": "8.0.1.0.0",
    "author": "Opener B.V.,Odoo Community Association (OCA)",
    "website": 'https://github.com/oca/sale-workflow',
    "depends": [
        'sale_stock',
    ],
    'data': [
        'views/sale_order.xml',
    ],
    'installable': True,
}
