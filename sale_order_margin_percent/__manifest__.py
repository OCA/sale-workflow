# -*- coding: utf-8 -*-
{
    "name": "Sale Order Margin Percent",
    "summary": "Show Percent in sale order",
    "version": "10.0.1.0.0",
    "category": "Sales",
    "website": "http://www.pesol.es",
    "author": "PESOL",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        'sale',
        'sale_margin'
    ],
    "data": [
        'views/sale_order_margin_percent_view.xml',

    ]
}
