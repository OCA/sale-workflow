# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Sale Revert Done",
    "summary": "This module extends the functionality of sales to allow you "
               "to set a sales order done back to state 'Sale Order'.",
    "version": "10.0.1.0.1",
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
