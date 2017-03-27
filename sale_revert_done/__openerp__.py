# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Sale Revert Done",
    "summary": "Allow you to revert the state of a sale order from 'done' to "
               "'Sale Order' again.",
    "version": "9.0.1.0.0",
    "author": "Eficent, "
              "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/sale-workflow",
    "category": "Sales",
    "depends": ["sale"],
    "data": [
        'views/sale_revert_done_view.xml',
    ],
    "license": "AGPL-3",
    'installable': True,
    'application': False,
}
