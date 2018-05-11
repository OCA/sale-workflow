# -*- coding: utf-8 -*-
# Copyright 2015 Carlos Sánchez Cifuentes <csanchez@grupovermon.com>
# Copyright 2015-2016 Oihane Crucelaegui <oihane@avanzosc.com>
# Copyright 2015-2016 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# Copyright 2016 Lorenzo Battistini
# Copyright 2016 Carlos Dauden <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Sale Order Type",
    "version": "10.0.1.0.1",
    "category": "Sales Management",
    "author": "Grupo Vermon,"
              "AvanzOSC,"
              "Tecnativa,"
              "Agile Business Group,"
              "Niboo,"
              "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/sale-workflow",
    "license": "AGPL-3",
    "depends": [
        'sale_stock',
        'account',
    ],
    "demo": [
        "demo/sale_order_demo.xml",
    ],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "views/sale_order_view.xml",
        "views/sale_order_type_view.xml",
        "views/account_invoice_view.xml",
        "views/res_partner_view.xml",
        "data/default_type.xml",
    ],
    'installable': True,
}
