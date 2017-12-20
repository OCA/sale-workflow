# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# Copyright 2017 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Sale Order Line Sequence",
    "summary": "Propagates SO line sequence to invoices and stock picking.",
    "version": "9.0.1.0.0",
    "author": "Eficent, "
              "Serpent CS, "
              "Odoo Community Association (OCA)",
    "category": "Sales",
    "website": "https://www.eficent.com/",
    "license": "AGPL-3",
    'data': ['views/sale_view.xml'],
    "depends": [
        "sale",
    ],
    "installable": True,
}
