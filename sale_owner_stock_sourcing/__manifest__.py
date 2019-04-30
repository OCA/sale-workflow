# -*- coding: utf-8 -*-
# © 2015-2015 Yannick Vaucher, Leonardo Pistone, Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{"name": "Sale Owner Stock Sourcing",
 "summary": "Manage stock ownership on sale order lines",
 "version": "10.0.1.0.0",
 "author": "Camptocamp,Odoo Community Association (OCA)",
 "license": "AGPL-3",
 "category": "Purchase Management",
 'complexity': "normal",
 "website": "http://www.camptocamp.com",
 "depends": [
     'sale_stock',
     'stock_ownership_availability_rules',
 ],
 "data": [
     'view/sale_order.xml',
     'security/group.xml',
 ],
 'installable': True,
 "auto_install": False}
