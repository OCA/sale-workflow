# -*- coding: utf-8 -*-
# Copyright 2013-2014 Camptocamp SA - Guewen Baconnier
# © 2016 Eficent Business and IT Consulting Services S.L.
# © 2016 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    'name': 'Sale Sourced by Line',
    'summary': 'Multiple warehouse source locations for Sale order',
    'version': '9.0.1.0.0',
    "author": "Camptocamp,"
              "Eficent,"
              "SerpentCS,"
              "Odoo Community Association (OCA)",
    'category': 'Warehouse',
    'license': 'AGPL-3',
    'website': "http://www.camptocamp.com",
    'depends': ['sale_stock',
                'sale_procurement_group_by_line',
                ],
    'data': [
        'view/sale_view.xml'
    ],
    'auto_install': False,
    'installable': True,
}
