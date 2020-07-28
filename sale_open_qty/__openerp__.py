# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Sale Open Qty",
    "summary": "Allows to identify the sale orders that have quantities "
               "pending to invoice or to deliver.",
    "version": "9.0.1.0.1",
    "author": "Eficent, "
              "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/sale-workflow",
    "category": "Sales",
    "depends": ["sale_stock"],
    "data": [
        'views/sale_view.xml',
    ],
    'pre_init_hook': 'pre_init_hook',
    "license": "AGPL-3",
    "installable": True,
    "application": False,
}
