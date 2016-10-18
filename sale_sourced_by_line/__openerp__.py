# -*- coding: utf-8 -*-
# Copyright 2013-2014 Camptocamp SA - Guewen Baconnier
# © 2015 Eficent Business and IT Consulting Services S.L.
# - Jordi Ballester Alomar
# © 2015 Serpent Consulting Services Pvt. Ltd. - Sudhir Arya
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    'name': 'Sale Sourced by Line',
    'summary': 'Multiple warehouse source locations for Sale order',
    'version': '9.0.1.0.0',
    "author": "Camptocamp,"
              "Eficent Business and IT Consulting Services S.L.,"
              "Serpent Consulting Services Pvt. Ltd.,"
              "Odoo Community Association (OCA)",
    'category': 'Warehouse',
    'license': 'AGPL-3',
    'complexity': 'expert',
    'website': "http://www.camptocamp.com",
    'depends': ['sale_stock',
            'sale_procurement_group_by_line',
            ],
    'data': ['view/sale_view.xml',
         ],
    'auto_install': False,
    'installable': True,
 }
