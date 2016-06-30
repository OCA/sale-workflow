# -*- coding: utf-8 -*-
# © 2015 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Sale Order Line Sequence Propagate",
    "description": "Propagates the SO line sequence to invoices and stock "
                   "pickings.",
    "version": "7.0.1.0.0",
    "author": "Eficent Business and IT Consulting Services S.L.",
    "category": "Sales",
    "website": "http://www.eficent.com/",
    "license": "AGPL-3", 
    "depends": [
        "account_invoice_line_order_sequence",
        "stock_move_order_sequence"
    ],
    "installable": True, 
    "auto_install": False, 
    "active": False
}
