# -*- coding: utf-8 -*-
# (c) 2015 Ainara Galdona - AvanzOSC
# (c) 2015 Oihane Crucelaegui - AvanzOSC
# (c) 2015 Esther Martín <esthermartin@avanzosc.es> - Avanzosc S.L.
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
              "Serv. Tecnol. Avanzados - Pedro M. Baeza",
    "category": "Custom Module",
    "website": "http://www.odoomrp.com",
    "contributors": [
        "Oihane Crucelaegui <oihanecrucelaegi@avanzosc.es>",
        "Ainara Galdona <ainaragaldona@avanzosc.es>",
        "Pedro M. Baeza <pedro.baeza@serviciosbaeza.com>",
        "Ana Juaristi <anajuaristi@avanzosc.es>",
        "Esther Marítn <esthermartin@avanzosc.es"
    ],
    "data": [
        "views/partner_view.xml",
        "views/sale_view.xml",
        "views/stock_view.xml",
        "views/account_view.xml",
    ],
    "installable": True,
}
