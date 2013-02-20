# -*- coding: utf-8 -*-
{
    "name": "Sales Quotation Pre-booking of stock",
    "version": "7.0.0",
    "depends": ["sale_validity"],
    "author": "Jacques-Etienne Baudoux",
    "category": "Sales",
    "description": "Allow to reserve stock (virtual quantity) during quotation",
    'data': [
        "wizard/sale_stock_prebook.xml",
        "view/sale_order.xml",
        ],
    'installable': True,
    'active': False,
}
