# -*- coding: utf-8 -*-
# Copyright 2015 Ainara Galdona - AvanzOSC
# Copyright 2015 Oihane Crucelaegui - AvanzOSC
# Copyright 2015 Esther Martín <esthermartin@avanzosc.es> - Avanzosc S.L.
# Copyright 2016-2017 Lorenzo Battistini - Agile Business Group
# Copyright 2017 Nicola Malcontenti - Agile Business Group
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    "name": "Comments for sale documents (order, picking and invoice)",
    "version": "10.0.1.0.0",
    "license": 'AGPL-3',
    "depends": [
        "sale_stock",
        "sale",
        "stock_account",
        "stock",
        "account",
    ],
    "author": "OdooMRP team, "
              "AvanzOSC, "
              "Tecnativa,  "
              "Odoo Community Association (OCA), "
              "Agile Businnes Group",
    "category": "Sales",
    "data": [
        "views/partner_view.xml",
        "views/sale_view.xml",
        "views/stock_view.xml",
        "views/account_view.xml",
    ],
    "installable": True,
    "images": ['images/sale_comments.png'],
}
