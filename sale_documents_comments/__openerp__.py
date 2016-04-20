# -*- coding: utf-8 -*-
# © 2015 Ainara Galdona - AvanzOSC
# © 2015 Oihane Crucelaegui - AvanzOSC
# © 2015 Esther Martín <esthermartin@avanzosc.es> - Avanzosc S.L.
# © 2016 Lorenzo Battistini - Agile Business Group
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    "name": "Comments for sale documents (order, picking and invoice)",
    "version": "8.0.1.0.0",
    "depends": [
        "sale_stock",
        "sale",
        "stock_account",
        "stock",
        "account",
    ],
    "author": "OdooMRP team, "
              "AvanzOSC, "
              "Serv. Tecnol. Avanzados - Pedro M. Baeza, "
              "Odoo Community Association (OCA)",
    "category": "Sales",
    "website": "http://www.odoomrp.com",
    "data": [
        "views/partner_view.xml",
        "views/sale_view.xml",
        "views/stock_view.xml",
        "views/account_view.xml",
    ],
    "installable": True,
    "images": ['images/sale_comments.png'],
}
