# -*- coding: utf-8 -*-
#
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 20010 Akretion LDTA (<http://www.akretion.com>).
#    @author Raphaël Valyi
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#
{"name": "Sale Dropshipping",
 "version": "1.1.1",
 "author": "Akretion,Odoo Community Association (OCA)",
 "website": "https://github.com/OCA/sale-workflow",
 "category": "Generic Modules/Purchase",
 "depends": ["purchase",
             "sale_stock"],
 "description": """
Makes it better to deal with purchases with known sale schemes, specially the
following case:
1) normal
2) direct delivery (also called drop shipping)
3) direct invoice
4) direct delivery and direct invoice
See the attached diagram in images/purchase_to_sale.png to see the difference
between those flows.

In all those specific MTO (by opposition of MTS) cases,
it will link the sale order line and the purchase order lines together.

A good idea might be to use this module with the mrp_jit module
if you want MTO flows to be automatically dealt with right
at the sale order validation.

You can also tell if product suppliers accept drop shipping or not.
 If they accept it and if sale order
line has more products than the virtual quantity available,
then it selects drop shipping by default.

In the out going product list view, you can filter in or out drop shipping
picking.

TODO: eventually it might be interesting to do a chained move from supplier to
internal location and
from internal location to customer instead of supplier o customer directly.
This would enable moves to properly generate accounting moves
 in the stock journal for better tracking.
    """,
 "init_xml": [],
 "demo_xml": [],
 "test": ['test/test_sale_policy_procurement.yml',
          ],
 "update_xml": [
     "purchase_view.xml",
     "sale_view.xml",
     "product_view.xml",
     "stock_view.xml"],
 'images': ['images/purchase_to_sale.png'],
 'installable': False,
 'certificate': None,
 }
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
