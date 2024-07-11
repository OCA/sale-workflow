# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': "Company currency in sale orders",
    'version': "10.0.1.0.0",
    'author': "Camptocamp, "
              "Odoo Community Association (OCA) ",
    'website': "https://odoo-community.org/",
    'category': "Sale",
    'license': "AGPL-3",
    'depends': ["sale"],
    'data': [
        "views/sale_order_view.xml"
    ],
    'installable': True,
}
