# -*- coding: utf-8 -*-
# Copyright 2018 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Indexed prices on pricelists",
    "version": "10.0.1.0.0",
    "author": "Therp BV,Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "category": "Sales",
    "summary": "Adjust your prices periodically",
    "depends": [
        'product',
        'account',
    ],
    "demo": [
        "demo/product_pricelist.xml",
        "demo/product_pricelist_item.xml",
    ],
    "data": [
        "wizards/product_pricelist_index_generator.xml",
        "views/product_pricelist.xml",
        "views/product_pricelist_item.xml",
    ],
}
