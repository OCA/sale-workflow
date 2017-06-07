# -*- coding: utf-8 -*-
# © 2016 Eficent Business and IT Consulting Services S.L. <contact@eficent.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Partner Default Sale Warehouse",
    "summary": "Allows to define a default warehouse in sales orders from "
               "a proposal set in the Delivery Address partner",
    "version": "8.0.1.0.0",
    "author": "Eficent Business and IT Consulting Services S.L., "
              "Odoo Community Association (OCA)",
    "website": "http://www.eficent.com",
    "category": "Sales Management",
    "depends": [
        "sale_stock",
    ],
    "data": [
        "views/res_partner_view.xml"
    ],
    "license": "AGPL-3",
    'installable': True,
    'active': False,
}
